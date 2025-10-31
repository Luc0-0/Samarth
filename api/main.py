"""
FastAPI backend for Project Samarth Phase 3
Production-ready Q&A System for Indian Agriculture and Climate Data
"""

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import logging
import json
import os
import sys
import time
import uuid
import io
from datetime import datetime
from typing import Optional, List
import pandas as pd

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.nlu import IntentParser
from core.source_selector import SourceSelector
from core.query_planner import QueryPlanner
from core.live_query_planner import LiveQueryPlanner
from core.synthesizer import AnswerSynthesizer
# from api.pdf_generator import generate_pdf_report  # Disabled for deployment

# Environment variables
DB_PATH = os.getenv('DB_PATH', 'db/canonical.duckdb')
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,https://samarth-two.vercel.app').split(',')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
GOV_API_KEY = os.getenv('GOV_API_KEY')

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Project Samarth Q&A API",
    description="Production Q&A System for Indian Agriculture and Climate Data",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request tracking
request_count = 0
start_time = time.time()

# Initialize components
intent_parser = IntentParser()
source_selector = SourceSelector()

# Debug API key status
if GOV_API_KEY:
    logger.info(f"API key loaded: {GOV_API_KEY[:10]}...{GOV_API_KEY[-4:] if len(GOV_API_KEY) > 14 else 'short'}")
else:
    logger.warning("No GOV_API_KEY found in environment variables")

query_planner = LiveQueryPlanner(DB_PATH, GOV_API_KEY)  # Use live query planner
answer_synthesizer = AnswerSynthesizer()

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    request_id: str
    answer_text: str
    structured_results: List[dict]
    citations: List[dict]
    processing_info: dict
    provenance: dict

class ProvenanceData(BaseModel):
    dataset_title: str
    resource_url: str
    sql_query: str
    sample_rows: List[dict]
    ingestion_timestamp: str
    query_timestamp: str

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID for tracing"""
    global request_count
    request_count += 1
    
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(
    request: QuestionRequest, 
    req: Request,
    x_request_id: Optional[str] = Header(None)
):
    """Process natural language question and return answer with full provenance"""
    
    request_id = getattr(req.state, 'request_id', str(uuid.uuid4()))
    start_time = datetime.now()
    
    try:
        logger.info(f"[{request_id}] Processing question: {request.question}")
        
        # Step 1: Parse natural language question
        intent = intent_parser.parse_question(request.question)
        logger.info(f"[{request_id}] Parsed intent: {intent}")
        
        # Step 2: Select relevant data sources
        sources = source_selector.select_sources(intent)
        logger.info(f"[{request_id}] Selected {len(sources)} sources")
        
        if not sources:
            return QuestionResponse(
                request_id=request_id,
                answer_text="I couldn't find relevant datasets for your question. Please try rephrasing or asking about agriculture production, crop yields, or rainfall data.",
                structured_results=[],
                citations=[],
                processing_info={
                    'intent': intent,
                    'sources_found': 0,
                    'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000
                },
                provenance={}
            )
        
        # Step 3: Execute query
        query_result = query_planner.execute_query(intent, sources)
        logger.info(f"[{request_id}] Query executed, got {len(query_result.get('results', []))} results")
        logger.info(f"[{request_id}] Query result keys: {list(query_result.keys())}")
        logger.info(f"[{request_id}] Data source used: {query_result.get('data_source', 'unknown')}")
        logger.info(f"[{request_id}] Metric detected: {query_result.get('metric', 'unknown')}")
        
        # Step 4: Synthesize answer
        response = answer_synthesizer.synthesize_answer(intent, query_result, sources)
        
        # Step 5: Build provenance data
        provenance = {
            'datasets_used': [],
            'sql_queries': [query_result.get('query', '')],
            'sample_data_available': True,
            'audit_trail_id': request_id
        }
        
        for source in sources:
            provenance['datasets_used'].append({
                'dataset_title': source['dataset_title'],
                'resource_url': source['resource_url'],
                'table_name': source.get('table_name', ''),
                'sample_endpoint': f"/raw/{source['dataset_id']}"
            })
        
        # Log query for traceability
        log_entry = {
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'question': request.question,
            'intent': intent,
            'sources_used': [s['dataset_id'] for s in sources],
            'query': query_result.get('query', ''),
            'results_count': len(query_result.get('results', [])),
            'processing_time_ms': (datetime.now() - start_time).total_seconds() * 1000,
            'user_agent': req.headers.get('user-agent', ''),
            'ip_address': req.client.host if req.client else 'unknown'
        }
        
        with open('logs/query_log.jsonl', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Add processing info
        processing_info = {
            'intent': intent,
            'sources_used': len(sources),
            'processing_time_ms': log_entry['processing_time_ms'],
            'query_type': intent.get('query_type', 'general')
        }
        
        return QuestionResponse(
            request_id=request_id,
            answer_text=response['answer_text'],
            structured_results=response['structured_results'],
            citations=response['citations'],
            processing_info=processing_info,
            provenance=provenance
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/export-pdf")
async def export_pdf(request: QuestionRequest, req: Request):
    """Export query results as PDF report - Disabled for deployment"""
    raise HTTPException(status_code=501, detail="PDF export temporarily disabled")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🌾 Project Samarth Q&A API v3.0",
        "environment": ENVIRONMENT,
        "endpoints": {
            "ask_question": "POST /ask",
            "health_check": "GET /health",
            "metrics": "GET /metrics",
            "list_datasets": "GET /datasets",
            "raw_data": "GET /raw/{dataset_id}",
            "api_docs": "GET /docs"
        },
        "features": [
            "Natural language processing",
            "Citation-backed answers", 
            "Full provenance tracking",
            "Request tracing",
            "CORS enabled"
        ]
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with system status"""
    try:
        # Test database connection
        import duckdb
        conn = duckdb.connect(DB_PATH)
        conn.execute("SELECT 1").fetchone()
        conn.close()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "environment": ENVIRONMENT,
        "database": db_status,
        "api_key_status": "configured" if GOV_API_KEY else "missing",
        "uptime_seconds": time.time() - start_time
    }

@app.get("/metrics")
async def metrics():
    """Basic metrics endpoint"""
    return {
        "requests_total": request_count,
        "uptime_seconds": time.time() - start_time,
        "timestamp": datetime.now().isoformat(),
        "database_size_mb": os.path.getsize(DB_PATH) / (1024 * 1024) if os.path.exists(DB_PATH) else 0
    }

@app.get("/datasets")
async def list_datasets():
    """List available datasets with enhanced metadata"""
    try:
        inventory = source_selector.inventory
        datasets = []
        
        for _, row in inventory.iterrows():
            datasets.append({
                'dataset_id': row['dataset_id'],
                'title': row['dataset_title'],
                'publisher': row['publisher'],
                'resource_url': row['resource_url'],
                'geo_granularity': row['geo_granularity'],
                'temporal_granularity': row['temporal_granularity'],
                'available_years': row['available_years'],
                'fields_summary': row['fields_summary'],
                'access_notes': row['access_notes'],
                'sample_endpoint': f"/raw/{row['dataset_id']}"
            })
            
        return {
            "datasets": datasets, 
            "count": len(datasets),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error listing datasets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/raw/{dataset_id}")
async def get_raw_data(dataset_id: str):
    """Get sample raw data for provenance display"""
    try:
        # Get dataset info
        inventory = source_selector.inventory
        dataset_row = inventory[inventory['dataset_id'] == dataset_id]
        
        if dataset_row.empty:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        # Generate sample data (in production, this would come from actual samples)
        import duckdb
        conn = duckdb.connect(DB_PATH)
        
        if dataset_id.startswith('agri'):
            query = "SELECT * FROM agri_production LIMIT 10"
        elif dataset_id.startswith('climate'):
            query = "SELECT * FROM climate_obs LIMIT 10"
        elif dataset_id.startswith('live'):
            # For live datasets, return sample structure with mock data
            if 'live-1' in dataset_id:
                # Market prices structure
                sample_data = {
                    'state': ['Maharashtra', 'Punjab', 'Gujarat'],
                    'district': ['Mumbai', 'Ludhiana', 'Ahmedabad'],
                    'commodity': ['Rice', 'Wheat', 'Cotton'],
                    'modal_price': [2500, 2200, 5500],
                    'arrival_date': ['2024-01-15', '2024-01-15', '2024-01-15']
                }
            else:
                # Production structure
                sample_data = {
                    'state': ['Maharashtra', 'Punjab', 'Gujarat'],
                    'crop': ['Rice', 'Wheat', 'Cotton'],
                    'season': ['Kharif', 'Rabi', 'Kharif'],
                    'area': [1000, 1200, 800],
                    'production': [2500, 2800, 1600]
                }
            
            results = pd.DataFrame(sample_data)
            conn.close()
            
            return {
                "dataset_id": dataset_id,
                "dataset_title": dataset_row.iloc[0]['dataset_title'],
                "resource_url": dataset_row.iloc[0]['resource_url'],
                "sample_rows": results.to_dict('records'),
                "total_sample_rows": len(results),
                "query_used": "Live API sample data structure",
                "timestamp": datetime.now().isoformat(),
                "note": "This is sample data structure. Actual data comes from live API."
            }
        else:
            raise HTTPException(status_code=404, detail="No sample data available")
        
        results = conn.execute(query).df()
        conn.close()
        
        return {
            "dataset_id": dataset_id,
            "dataset_title": dataset_row.iloc[0]['dataset_title'],
            "resource_url": dataset_row.iloc[0]['resource_url'],
            "sample_rows": results.to_dict('records'),
            "total_sample_rows": len(results),
            "query_used": query,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting raw data for {dataset_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=os.getenv('API_HOST', '0.0.0.0'), 
        port=int(os.getenv('PORT', os.getenv('API_PORT', 8000)))
    )
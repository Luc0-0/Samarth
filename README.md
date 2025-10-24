# Project Samarth - Intelligent Q&A System for Indian Agriculture

🌾 **Phase 3 Complete**: Production-ready deployment with Next.js frontend, enhanced provenance tracking, CI/CD pipeline, and comprehensive monitoring.

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)
```bash
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Local Development
```bash
# Backend
python run_server.py

# Frontend (new terminal)
cd frontend/nextjs
npm install && npm run dev
```

### Option 3: Production Deployment
See [README_DEPLOY.md](README_DEPLOY.md) for cloud deployment instructions.

## 💡 Sample Questions

- "Compare the average annual rainfall in Maharashtra and Punjab"
- "Which state has the highest rice production?"
- "Show me the correlation between rainfall and crop production"
- "What is the average wheat production in Punjab?"
- "Analyze the production trend of cotton from 2010 to 2014"

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Frontend   │◄──►│   FastAPI   │◄──►│    Core     │
│ (Streamlit) │    │   Backend   │    │   Modules   │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                   ┌─────────────┐    ┌─────────────┐
                   │   DuckDB    │    │   Logging   │
                   │  Database   │    │ & Citations │
                   └─────────────┘    └─────────────┘
```

## 📊 Phase 3 Deliverables

### Production Frontend
- ✅ **Next.js React App** (`frontend/nextjs/`) - Modern TypeScript interface
- ✅ **Interactive Chat UI** - Real-time Q&A with loading states
- ✅ **Provenance Modal** - Full data lineage and SQL transparency
- ✅ **Citation Panel** - Clickable links to original datasets
- ✅ **Chart Visualization** - Trend analysis with Recharts
- ✅ **Responsive Design** - Mobile-friendly with Tailwind CSS

### Deployment & DevOps
- ✅ **Docker Containers** - Backend and frontend Dockerfiles
- ✅ **Docker Compose** - Multi-service local deployment
- ✅ **CI/CD Pipeline** - GitHub Actions with automated testing
- ✅ **Cloud Ready** - Render (backend) + Vercel (frontend)
- ✅ **Environment Config** - Secure secrets management
- ✅ **Health Monitoring** - Comprehensive system status

### Enhanced Backend
- ✅ **Request Tracing** - UUID-based request tracking
- ✅ **CORS Configuration** - Production-ready cross-origin setup
- ✅ **Monitoring Endpoints** - `/health`, `/metrics`, `/raw/{id}`
- ✅ **Audit Logging** - Complete query trail for compliance
- ✅ **Error Handling** - Graceful degradation and user feedback

## 📊 Phase 2 Core System

### Backend Foundation
- ✅ **FastAPI Backend** (`api/main.py`) - REST API with `/ask` endpoint
- ✅ **NLU Pipeline** (`core/nlu.py`) - Natural language understanding
- ✅ **Query Engine** (`core/query_planner.py`) - SQL generation and execution
- ✅ **Answer Synthesis** (`core/synthesizer.py`) - Human-readable responses
- ✅ **Citation System** - Full traceability to source datasets

### Database & Data
- ✅ **Canonical Database** (`db/canonical.duckdb`) - 400 sample records
- ✅ **10 Integrated Datasets** - Agriculture and climate data from data.gov.in
- ✅ **Sample Data** - 10 states × 7 crops × 5 years

### User Interfaces
- ✅ **Streamlit Web App** (`frontend/app.py`) - Interactive chat interface
- ✅ **API Documentation** - Auto-generated at `/docs`
- ✅ **Demo Notebook** (`demo_questions.ipynb`) - Jupyter examples

## 📈 Performance

- **Response Time**: < 2 seconds
- **Database Size**: 12MB
- **Query Types**: Comparison, Trend, Correlation, Ranking
- **Citation Accuracy**: 100% traceability

## 🗂️ Phase 1 (Dataset Discovery)

### Key Datasets Discovered
1. **District wise Season wise Crop Production** (2001-2014) - High Priority
2. **District wise Rainfall Normal** (1951-2000) - High Priority  
3. **State wise Monthly Rainfall** (1901-2015) - Long-term series
4. **Agricultural Statistics at a Glance** - Comprehensive stats
5. **IMD Gridded Rainfall** - Requires registration

### Data Ingestion
```bash
# Download agriculture data
cd ingestion
python fetch_agri.py --inventory ../data_inventory.csv

# Download climate data
python fetch_imd.py --inventory ../data_inventory.csv
```

## 🔧 Development

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Create Database
```bash
python create_canonical_db.py
```

### Run Tests
```bash
python test_api.py
```

## 📚 Data Sources
- **Primary**: data.gov.in (Ministry of Agriculture, IMD)
- **Secondary**: USGS/CHG CHIRPS (fallback climate data)
- **Access**: Most datasets publicly available, IMD gridded data requires registration

## 🎯 Next Steps (Phase 3)
- Advanced visualization with charts/maps
- Real-time data ingestion pipeline
- Machine learning predictions
- Mobile app development
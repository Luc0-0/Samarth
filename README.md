# Project Samarth - Intelligent Q&A System for Indian Agriculture

🌾 **LIVE DATA INTEGRATION COMPLETE**: Real-time data fetching from data.gov.in API, production deployment, and comprehensive monitoring.

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

### Historical Data (2001-2014)
- "Compare the average annual rainfall in Maharashtra and Punjab"
- "Which state has the highest rice production?"
- "Analyze the production trend of cotton from 2010 to 2014"

### Live Data (Real-time API)
- "What are the current crop prices in Maharashtra?"
- "Show me latest market rates for Punjab"
- "Compare recent commodity prices across states"

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Frontend   │◄──►│   FastAPI   │◄──►│    Core     │
│ (Next.js)   │    │   Backend   │    │   Modules   │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                   ┌─────────────┐    ┌─────────────┐
                   │ Live API    │    │   DuckDB    │
                   │data.gov.in  │    │  Database   │
                   └─────────────┘    └─────────────┘
                           │                   │
                   ┌─────────────┐    ┌─────────────┐
                   │Real-time    │    │ Historical  │
                   │Market Data  │    │ Sample Data │
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
- ✅ **Live Data Integration** - Real-time API connection to data.gov.in
- ✅ **Smart Query Routing** - Auto-detects live vs historical queries
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
- ✅ **Live API Integration** - Real-time data from data.gov.in with API key
- ✅ **Canonical Database** (`db/canonical.duckdb`) - 400 sample records
- ✅ **12 Integrated Datasets** - Agriculture, climate, and live market data
- ✅ **Hybrid Data Sources** - Live API + Historical database
- ✅ **Sample Data** - 10 states × 7 crops × 5 years

### User Interfaces
- ✅ **Streamlit Web App** (`frontend/app.py`) - Interactive chat interface
- ✅ **API Documentation** - Auto-generated at `/docs`
- ✅ **Demo Notebook** (`demo_questions.ipynb`) - Jupyter examples

## 📈 Performance

- **Response Time**: < 2 seconds (live API + local data)
- **Database Size**: 12MB + Live API
- **Query Types**: Comparison, Trend, Correlation, Ranking, Current
- **Data Sources**: Historical (2001-2014) + Live (Real-time)
- **Citation Accuracy**: 100% traceability

## 🗂️ Phase 1 (Dataset Discovery)

### Key Datasets Integrated
1. **Live Market Prices** (Real-time) - API Integration ⚡
2. **Live Agriculture Production** (Current) - API Integration ⚡
3. **District wise Season wise Crop Production** (2001-2014) - Historical
4. **District wise Rainfall Normal** (1951-2000) - Historical
5. **State wise Monthly Rainfall** (1901-2015) - Long-term series
6. **Agricultural Statistics at a Glance** - Comprehensive stats
7. **IMD Gridded Rainfall** - Requires registration

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

## 🎯 System Capabilities

### ✅ **Completed Features**
- ✅ **Live Data Integration** - Real-time API from data.gov.in
- ✅ **Advanced Visualization** - Charts and trend analysis
- ✅ **Production Deployment** - Render + Vercel
- ✅ **Complete Provenance** - Full audit trail
- ✅ **Citation System** - 100% traceability

### 🚀 **Future Enhancements**
- Machine learning predictions
- Mobile app development
- Advanced geospatial analysis
- Multi-language support
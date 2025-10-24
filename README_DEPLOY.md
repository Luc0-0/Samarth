# Deployment Guide - Project Samarth Phase 3

## 🚀 Quick Deploy Options

### Option 1: Local Development
```bash
# Backend
python run_server.py

# Frontend (new terminal)
cd frontend/nextjs
npm install
npm run dev
```

### Option 2: Docker Compose (Recommended)
```bash
# Build and start all services
docker-compose up --build

# Access:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Option 3: Cloud Deployment

## 🌐 Cloud Deployment

### Backend on Render

1. **Create Render Account**: https://render.com
2. **Connect GitHub**: Link your repository
3. **Create Web Service**:
   - Runtime: Docker
   - Build Command: `docker build -f api/Dockerfile .`
   - Start Command: Auto-detected from Dockerfile
4. **Environment Variables**:
   ```
   DB_PATH=/app/db/canonical.duckdb
   CORS_ORIGINS=https://your-frontend.vercel.app
   ENVIRONMENT=production
   ```
5. **Deploy**: Render will auto-deploy on git push

### Frontend on Vercel

1. **Create Vercel Account**: https://vercel.com
2. **Import Project**: Connect GitHub repository
3. **Configure**:
   - Framework: Next.js
   - Root Directory: `frontend/nextjs`
4. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   ```
5. **Deploy**: Auto-deploys on git push

## 🔐 Environment Variables

### Backend (.env)
```bash
# Required
DB_PATH=db/canonical.duckdb
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app

# Optional
API_HOST=127.0.0.1
API_PORT=8000
RATE_LIMIT_PER_MINUTE=60
LOG_LEVEL=INFO
REDIS_URL=redis://localhost:6379
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🔑 Secrets Management

### GitHub Secrets (for CI/CD)
```
RENDER_API_KEY=your-render-api-key
RENDER_SERVICE_ID=your-service-id
VERCEL_TOKEN=your-vercel-token
VERCEL_ORG_ID=your-org-id
VERCEL_PROJECT_ID=your-project-id
```

### Render Environment Variables
- Set in Render Dashboard > Service > Environment
- Use for sensitive data like API keys
- Auto-redeploys on changes

### Vercel Environment Variables
- Set in Vercel Dashboard > Project > Settings > Environment Variables
- Separate values for Development/Preview/Production
- Auto-redeploys on changes

## 🧪 Testing Deployment

### Local Testing
```bash
# Test API
python simple_test.py

# Test endpoints
chmod +x test_endpoints.sh
./test_endpoints.sh http://localhost:8000

# Test frontend
cd frontend/nextjs
npm run build
npm start
```

### Production Testing
```bash
# Test deployed API
./test_endpoints.sh https://your-backend.onrender.com

# Test frontend
curl -I https://your-frontend.vercel.app
```

## 📊 Monitoring

### Health Checks
- **Backend**: `GET /health`
- **Frontend**: Built-in Vercel monitoring
- **Database**: Included in health check

### Logs
- **Render**: Dashboard > Service > Logs
- **Vercel**: Dashboard > Project > Functions
- **Local**: `logs/api.log` and `logs/query_log.jsonl`

### Metrics
- **API Metrics**: `GET /metrics`
- **Request Tracing**: X-Request-ID headers
- **Performance**: Processing time in responses

## 🔧 Troubleshooting

### Common Issues

**CORS Errors**:
```bash
# Update CORS_ORIGINS environment variable
CORS_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

**Database Connection**:
```bash
# Check database file exists and is readable
ls -la db/canonical.duckdb
```

**Build Failures**:
```bash
# Check dependencies
pip install -r requirements.txt
cd frontend/nextjs && npm install
```

**API Timeouts**:
```bash
# Check health endpoint
curl https://your-backend.onrender.com/health
```

### Debug Commands
```bash
# Check API status
curl -v https://your-backend.onrender.com/health

# Test CORS
curl -H "Origin: https://your-frontend.vercel.app" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     https://your-backend.onrender.com/ask

# Check logs
tail -f logs/api.log
```

## 🚀 CI/CD Pipeline

### GitHub Actions
- **Triggers**: Push to main, PRs
- **Tests**: pytest, linting, build validation
- **Deploy**: Auto-deploy to Render/Vercel on main branch
- **Secrets**: Stored in GitHub repository settings

### Manual Deploy
```bash
# Trigger Render deploy
curl -X POST "https://api.render.com/v1/services/YOUR_SERVICE_ID/deploys" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Trigger Vercel deploy
npx vercel --prod
```

## 📈 Scaling Considerations

### Performance Optimization
- Enable Redis caching for repeated queries
- Use CDN for static assets (Vercel provides this)
- Database connection pooling
- API rate limiting

### Security Hardening
- HTTPS only (provided by Render/Vercel)
- API key authentication (if needed)
- Input validation and sanitization
- Regular security updates

### Monitoring & Alerting
- Set up Render/Vercel alerts for downtime
- Monitor API response times
- Track error rates and patterns
- Set up log aggregation (optional)

## 🆘 Support

### Documentation
- API Docs: `https://your-backend.onrender.com/docs`
- Repository: https://github.com/Luc0-0/Samarth
- Issues: GitHub Issues tab

### Quick Links
- **Render Dashboard**: https://dashboard.render.com
- **Vercel Dashboard**: https://vercel.com/dashboard
- **GitHub Actions**: Repository > Actions tab
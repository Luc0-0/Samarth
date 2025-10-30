"""
Simple server runner for Project Samarth
"""

import uvicorn
from api.main import app

if __name__ == "__main__":
    print("🌾 Starting Project Samarth API Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("❤️  Health check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    import os
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=False,
        log_level="info"
    )
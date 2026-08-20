from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os
from backend.config.settings import settings
from backend.database.db import engine, Base

# Import router modules
from backend.routes.suppliers import router as suppliers_router
from backend.routes.logistics import router as logistics_router
from backend.routes.shipments import router as shipments_router
from backend.routes.risks import router as risks_router
from backend.routes.recommendations import router as recommendations_router
from backend.routes.dashboard import router as dashboard_router
from backend.routes.compliance import router as compliance_router
from backend.routes.news import router as news_router
from backend.routes.inventory import router as inventory_router
from backend.routes.scenarios import router as scenarios_router
from backend.routes.demo import router as demo_router
from backend.routes.reports import router as reports_router
from backend.routes.ai import router as ai_router

# Create DB tables
try:
    Base.metadata.create_all(bind=engine)
except Exception:
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AegisFlow - AI-Powered Autonomous Supply Chain Decision Intelligence Platform"
)

# Configured CORS for development origins
allowed_origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # Also allow any Cloudflare tunnel subdomain and
    # any other same-host variant (useful during demos)
    allow_origin_regex=r"https://.*\.trycloudflare\.com",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

# Root Endpoint: Return index.html for browser text/html requests, JSON for API / TestClient calls
@app.get("/")
def read_root(request: Request):
    accept_header = request.headers.get("accept", "")
    index_path = os.path.join(frontend_dir, "index.html")
    if "text/html" in accept_header and os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "project": "AegisFlow",
        "status": "running"
    }

@app.get("/health")
def read_health():
    return {
        "status": "healthy"
    }

@app.get("/api")
@app.get("/api/v1")
def read_api_status():
    return {
        "project": "AegisFlow",
        "status": "running"
    }

# Register Routers under /api and /api/v1 prefixes
for prefix in ["/api", "/api/v1"]:
    app.include_router(suppliers_router, prefix=prefix)
    app.include_router(logistics_router, prefix=prefix)
    app.include_router(shipments_router, prefix=prefix)
    app.include_router(risks_router, prefix=prefix)
    app.include_router(recommendations_router, prefix=prefix)
    app.include_router(dashboard_router, prefix=prefix)
    app.include_router(compliance_router, prefix=prefix)
    app.include_router(news_router, prefix=prefix)
    app.include_router(inventory_router, prefix=prefix)
    app.include_router(scenarios_router, prefix=prefix)
    app.include_router(demo_router, prefix=prefix)
    app.include_router(reports_router, prefix=prefix)
    app.include_router(ai_router, prefix=prefix)

# Serve frontend static assets if directory exists
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)


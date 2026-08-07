from fastapi import FastAPI

from backend.routes import (
    suppliers,
    risks,
    dashboard,
    inventory,
    alerts,
    recommendations,
    auth
)

app = FastAPI(
    title="AegisFlow Backend",
    version="1.0.0"
)

# Register all routers
app.include_router(auth.router)
app.include_router(suppliers.router)
app.include_router(inventory.router)
app.include_router(risks.router)
app.include_router(alerts.router)
app.include_router(recommendations.router)
app.include_router(dashboard.router)


@app.get("/")
def home():
    return {
        "message": "Welcome to AegisFlow Backend"
    }
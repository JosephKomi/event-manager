import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

from database import init_db
from routes.events import router as events_router
from routes.monitoring import router as monitoring_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Actions au demarrage et a l'arret du serveur."""
    # Au demarrage
    await init_db()
    print("Serveur demarre avec succes")
    yield
    # A l'arret
    print("Serveur arrete")


app = FastAPI(
    title="Event Manager",
    description="Service central de gestion des evenements pour une plateforme e-commerce",
    version=os.getenv("APP_VERSION", "1.0.0"),
    lifespan=lifespan,
)

# Enregistrement des routes
app.include_router(events_router)
app.include_router(monitoring_router)


@app.get("/")
async def root():
    return {
        "service": "Event Manager",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "status": "running",
        "docs": "/docs",
    }
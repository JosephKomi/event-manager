import time
import os
import aiosqlite
from fastapi import APIRouter, Depends
from database import get_db
from models import HealthResponse, MetricsResponse

router = APIRouter()

# Heure de demarrage du serveur
START_TIME = time.time()


@router.get("/health", response_model=HealthResponse)
async def health():
    """Retourne l'etat du service."""

    return HealthResponse(
        status="ok",
        version=os.getenv("APP_VERSION", "1.0.0"),
        uptime=round(time.time() - START_TIME, 2),
    )


@router.get("/metrics", response_model=MetricsResponse)
async def metrics(db: aiosqlite.Connection = Depends(get_db)):
    """Retourne les statistiques des evenements."""

    # Total general
    async with db.execute("SELECT COUNT(*) as total FROM events") as cursor:
        row = await cursor.fetchone()
        total = row["total"]

    # Repartition par statut
    async with db.execute(
        """
        SELECT status, COUNT(*) as count
        FROM events
        GROUP BY status
        """
    ) as cursor:
        rows = await cursor.fetchall()
        by_status = {row["status"]: row["count"] for row in rows}

    # Repartition par type d'evenement
    async with db.execute(
        """
        SELECT event_type, COUNT(*) as count
        FROM events
        GROUP BY event_type
        """
    ) as cursor:
        rows = await cursor.fetchall()
        by_type = {row["event_type"]: row["count"] for row in rows}

    return MetricsResponse(
        total=total,
        by_status=by_status,
        by_type=by_type,
    )
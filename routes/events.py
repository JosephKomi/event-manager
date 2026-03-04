import json
import uuid
from datetime import datetime, timezone

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from database import get_db
from models import EventCreate, EventResponse

router = APIRouter()


@router.post("/events", response_model=EventResponse, status_code=201)
async def create_event(event: EventCreate, db: aiosqlite.Connection = Depends(get_db)):
    """Recoit et stocke un evenement."""

    event_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    await db.execute(
        """
        INSERT INTO events (id, event_type, source_service, payload, status, retry_count, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            event.event_type,
            event.source_service,
            json.dumps(event.payload),
            "PENDING",
            0,
            now,
            now,
        ),
    )
    await db.commit()

    return EventResponse(
        id=event_id,
        event_type=event.event_type,
        source_service=event.source_service,
        payload=json.dumps(event.payload),
        status="PENDING",
        retry_count=0,
        created_at=now,
        updated_at=now,
    )


@router.get("/events", response_model=list[EventResponse])
async def list_events(
    status: Optional[str] = Query(None, description="Filtrer par statut : PENDING, PROCESSED, FAILED"),
    event_type: Optional[str] = Query(None, description="Filtrer par type d'evenement"),
    source_service: Optional[str] = Query(None, description="Filtrer par service source"),
    page: int = Query(1, ge=1, description="Numero de page"),
    limit: int = Query(10, ge=1, le=100, description="Nombre d'elements par page"),
    db: aiosqlite.Connection = Depends(get_db),
):
    """Retourne la liste paginee des evenements avec filtres optionnels."""

    query = "SELECT * FROM events WHERE 1=1"
    params = []

    if status:
        query += " AND status = ?"
        params.append(status)

    if event_type:
        query += " AND event_type = ?"
        params.append(event_type)

    if source_service:
        query += " AND source_service = ?"
        params.append(source_service)

    offset = (page - 1) * limit
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    async with db.execute(query, params) as cursor:
        rows = await cursor.fetchall()

    return [
        EventResponse(
            id=row["id"],
            event_type=row["event_type"],
            source_service=row["source_service"],
            payload=row["payload"],
            status=row["status"],
            retry_count=row["retry_count"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
        for row in rows
    ]


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, db: aiosqlite.Connection = Depends(get_db)):
    """Retourne le detail complet d'un evenement par son UUID."""

    async with db.execute(
        "SELECT * FROM events WHERE id = ?", (event_id,)
    ) as cursor:
        row = await cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Evenement non trouve")

    return EventResponse(
        id=row["id"],
        event_type=row["event_type"],
        source_service=row["source_service"],
        payload=row["payload"],
        status=row["status"],
        retry_count=row["retry_count"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# Modele pour recevoir un evenement (entree)
class EventCreate(BaseModel):
    event_type: str = Field(..., example="order.created")
    source_service: str = Field(..., example="order")
    payload: dict = Field(..., example={"order_id": "abc123", "amount": 49.99})


# Modele pour retourner un evenement (sortie)
class EventResponse(BaseModel):
    id: str
    event_type: str
    source_service: str
    payload: str
    status: str
    retry_count: int
    created_at: str
    updated_at: str


# Modele pour les filtres de la liste des evenements
class EventFilters(BaseModel):
    status: Optional[Literal["PENDING", "PROCESSED", "FAILED"]] = None
    event_type: Optional[str] = None
    source_service: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)


# Modele pour /health
class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float


# Modele pour /metrics
class MetricsResponse(BaseModel):
    total: int
    by_status: dict
    by_type: dict
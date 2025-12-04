"""
Event endpoints router.

This module defines API endpoints for event management.
"""

from typing import List, Optional

from fastapi import APIRouter, Query

from models import Event, EventCreate, EventUpdate
from services import event_service

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=Event, status_code=201)
def create_event(event: EventCreate):
    """Create a new event."""
    return event_service.create_event(event)


@router.get("", response_model=List[Event])
def list_events(status: Optional[str] = Query(None)):
    """List all events with optional status filter."""
    return event_service.list_events(status)


@router.get("/{event_id}", response_model=Event)
def get_event(event_id: str):
    """Get a specific event by ID."""
    return event_service.get_event(event_id)


@router.put("/{event_id}", response_model=Event)
def update_event(event_id: str, event_update: EventUpdate):
    """Update an existing event."""
    return event_service.update_event(event_id, event_update)


@router.delete("/{event_id}")
def delete_event(event_id: str):
    """Delete an event."""
    return event_service.delete_event(event_id)

"""
Registration endpoints router.

This module defines API endpoints for event registration management.
"""

from typing import List

from fastapi import APIRouter

from models import Registration, RegistrationCreate
from services import registration_service

router = APIRouter(tags=["registrations"])


@router.post("/events/{event_id}/registrations", response_model=Registration, status_code=201)
def register_for_event(event_id: str, registration: RegistrationCreate):
    """Register a user for an event."""
    return registration_service.register(event_id, registration)


@router.delete("/events/{event_id}/registrations/{user_id}")
def unregister_from_event(event_id: str, user_id: str):
    """Unregister a user from an event."""
    return registration_service.unregister(event_id, user_id)


@router.get("/users/{user_id}/registrations", response_model=List[Registration])
def get_user_registrations(user_id: str):
    """Get all registrations for a user."""
    return registration_service.get_user_registrations(user_id)

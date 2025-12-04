"""
Service layer for business logic.

This module contains business logic for users, events, and registrations.
Services coordinate between API handlers and the repository layer.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException

from models import (
    Event, EventCreate, EventUpdate,
    User, UserCreate,
    Registration, RegistrationCreate
)
from repository import repository


class UserService:
    """Service for user business logic."""

    def create_user(self, user: UserCreate) -> User:
        """Create a new user.
        
        Raises:
            HTTPException: 400 if user already exists
        """
        if repository.user_exists(user.userId):
            raise HTTPException(status_code=400, detail="User already exists")
        
        result = repository.create_user(user.userId, user.name)
        return User(**result)

    def get_user(self, user_id: str) -> User:
        """Get a user by ID.
        
        Raises:
            HTTPException: 404 if user not found
        """
        result = repository.get_user(user_id)
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        return User(**result)


class EventService:
    """Service for event business logic."""

    def create_event(self, event: EventCreate) -> Event:
        """Create a new event."""
        event_id = event.eventId if event.eventId else str(uuid.uuid4())
        
        event_data = {
            "eventId": event_id,
            "title": event.title,
            "description": event.description,
            "date": event.date,
            "location": event.location,
            "capacity": event.capacity,
            "organizer": event.organizer,
            "status": event.status,
            "waitlistEnabled": event.waitlistEnabled,
        }
        
        result = repository.create_event(event_data)
        return Event(**result)


    def get_event(self, event_id: str) -> Event:
        """Get an event by ID.
        
        Raises:
            HTTPException: 404 if event not found
        """
        result = repository.get_event(event_id)
        if not result:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return Event(**result)

    def list_events(self, status: Optional[str] = None) -> List[Event]:
        """List all events with optional status filter."""
        results = repository.list_events(status)
        return [Event(**r) for r in results]

    def update_event(self, event_id: str, event_update: EventUpdate) -> Event:
        """Update an existing event.
        
        Raises:
            HTTPException: 404 if event not found
            HTTPException: 400 if no fields to update
        """
        existing = repository.get_event_raw(event_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Event not found")

        update_data = event_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Apply updates to existing item
        if "title" in update_data:
            existing["title"] = update_data["title"]
        if "description" in update_data:
            existing["description"] = update_data["description"]
        if "date" in update_data:
            existing["eventDate"] = str(update_data["date"])
        if "location" in update_data:
            existing["eventLocation"] = update_data["location"]
        if "capacity" in update_data:
            existing["eventCapacity"] = update_data["capacity"]
        if "organizer" in update_data:
            existing["organizer"] = update_data["organizer"]
        if "status" in update_data:
            existing["eventStatus"] = update_data["status"]
        if "waitlistEnabled" in update_data:
            existing["waitlistEnabled"] = update_data["waitlistEnabled"]

        result = repository.update_event(event_id, existing)
        return Event(**result)

    def delete_event(self, event_id: str) -> dict:
        """Delete an event.
        
        Raises:
            HTTPException: 404 if event not found
        """
        existing = repository.get_event(event_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Event not found")
        
        repository.delete_event(event_id)
        return {"message": "Event deleted"}


class RegistrationService:
    """Service for registration business logic."""

    def register(self, event_id: str, registration: RegistrationCreate) -> Registration:
        """Register a user for an event.
        
        Handles capacity checking and waitlist logic.
        
        Raises:
            HTTPException: 404 if event not found
            HTTPException: 404 if user not found
            HTTPException: 400 if already registered
            HTTPException: 400 if event is full and waitlist disabled
        """
        # Get event
        event = repository.get_event_raw(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Check user exists
        if not repository.user_exists(registration.userId):
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if already registered
        existing_reg = repository.get_registration(event_id, registration.userId)
        if existing_reg:
            raise HTTPException(status_code=400, detail="Already registered")
        
        capacity = event.get("eventCapacity", 0)
        reg_count = event.get("registrationCount", 0)
        waitlist_enabled = event.get("waitlistEnabled", False)
        
        now = datetime.utcnow().isoformat()
        
        if reg_count < capacity:
            reg_status = "confirmed"
            waitlist_pos = None
            new_reg_count = reg_count + 1
        elif waitlist_enabled:
            reg_status = "waitlisted"
            # Get current waitlist count
            waitlisted = repository.get_waitlisted_registrations(event_id)
            waitlist_pos = len(waitlisted) + 1
            new_reg_count = reg_count
        else:
            raise HTTPException(status_code=400, detail="Event is full")
        
        # Create registration
        result = repository.create_registration(
            event_id=event_id,
            user_id=registration.userId,
            status=reg_status,
            registered_at=now,
            waitlist_pos=waitlist_pos
        )
        
        # Update event registration count if confirmed
        if reg_status == "confirmed":
            repository.update_event_registration_count(event_id, new_reg_count)
        
        return Registration(**result)


    def unregister(self, event_id: str, user_id: str) -> dict:
        """Unregister a user from an event.
        
        Handles waitlist promotion when a confirmed user unregisters.
        
        Raises:
            HTTPException: 400 if not registered for this event
        """
        # Get registration
        reg = repository.get_registration_raw(event_id, user_id)
        if not reg:
            raise HTTPException(status_code=400, detail="Not registered for this event")
        
        was_confirmed = reg.get("registrationStatus") == "confirmed"
        
        # Delete registration
        repository.delete_registration(event_id, user_id)
        
        # If was confirmed, promote from waitlist and update count
        if was_confirmed:
            event = repository.get_event_raw(event_id)
            
            if event:
                reg_count = event.get("registrationCount", 1)
                
                # Check for waitlisted users
                waitlisted = repository.get_waitlisted_registrations(event_id)
                
                if waitlisted:
                    # Promote first waitlisted user
                    first = waitlisted[0]
                    repository.update_registration_status(
                        event_id=event_id,
                        user_id=first["userId"],
                        status="confirmed",
                        waitlist_pos=None
                    )
                else:
                    # Decrement registration count
                    repository.update_event_registration_count(
                        event_id,
                        max(0, reg_count - 1)
                    )
        
        return {"message": "Unregistered successfully"}

    def get_user_registrations(self, user_id: str) -> List[Registration]:
        """Get all registrations for a user.
        
        Raises:
            HTTPException: 404 if user not found
        """
        # Check user exists
        if not repository.user_exists(user_id):
            raise HTTPException(status_code=404, detail="User not found")
        
        results = repository.get_user_registrations(user_id)
        return [Registration(**r) for r in results]


# Singleton instances for use across the application
user_service = UserService()
event_service = EventService()
registration_service = RegistrationService()

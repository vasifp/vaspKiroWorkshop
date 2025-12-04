"""
Pydantic models for the Events API.

This module defines the data models used for request/response validation
in the Events REST API.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class EventBase(BaseModel):
    """Base model for event data with common fields.
    
    Attributes:
        title: The event title (1-200 characters).
        description: Optional event description (max 2000 characters).
        date: The date of the event.
        location: The event location (1-500 characters).
        capacity: Maximum number of attendees (1-100000).
        organizer: Name of the event organizer (1-200 characters).
        status: Event status (draft, published, cancelled, completed, active).
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    date: date
    location: str = Field(..., min_length=1, max_length=500)
    capacity: int = Field(..., gt=0, le=100000)
    organizer: str = Field(..., min_length=1, max_length=200)
    status: str = Field(..., pattern=r"^(draft|published|cancelled|completed|active)$")


class EventCreate(BaseModel):
    """Model for creating a new event.
    
    Attributes:
        eventId: Optional custom event ID. If not provided, a UUID will be generated.
        title: The event title.
        description: Optional event description.
        date: The date of the event.
        location: The event location.
        capacity: Maximum number of attendees.
        organizer: Name of the event organizer.
        status: Event status.
    """
    eventId: Optional[str] = Field(None, min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    date: date
    location: str = Field(..., min_length=1, max_length=500)
    capacity: int = Field(..., gt=0, le=100000)
    organizer: str = Field(..., min_length=1, max_length=200)
    status: str = Field(..., pattern=r"^(draft|published|cancelled|completed|active)$")


class EventUpdate(BaseModel):
    """Model for updating an existing event.
    
    All fields are optional. Only provided fields will be updated.
    
    Attributes:
        title: Updated event title.
        description: Updated event description.
        date: Updated event date.
        location: Updated event location.
        capacity: Updated maximum attendees.
        organizer: Updated organizer name.
        status: Updated event status.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    date: Optional[date] = None
    location: Optional[str] = Field(None, min_length=1, max_length=500)
    capacity: Optional[int] = Field(None, gt=0, le=100000)
    organizer: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = Field(None, pattern=r"^(draft|published|cancelled|completed|active)$")


class Event(EventBase):
    """Complete event model including the event ID.
    
    Attributes:
        eventId: Unique identifier for the event.
    """
    eventId: str

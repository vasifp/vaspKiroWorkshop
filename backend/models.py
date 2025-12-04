"""
Pydantic models for the Events API.

This module defines the data models used for request/response validation
in the Events REST API.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field


# ============== User Models ==============

class UserCreate(BaseModel):
    """Model for creating a new user."""
    userId: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)


class User(BaseModel):
    """Complete user model."""
    userId: str
    name: str


# ============== Event Models ==============

class EventBase(BaseModel):
    """Base model for event data with common fields."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    date: date
    location: str = Field(..., min_length=1, max_length=500)
    capacity: int = Field(..., gt=0, le=100000)
    organizer: str = Field(..., min_length=1, max_length=200)
    status: str = Field(..., pattern=r"^(draft|published|cancelled|completed|active)$")
    waitlistEnabled: bool = False


class EventCreate(BaseModel):
    """Model for creating a new event."""
    eventId: Optional[str] = Field(None, min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    date: date
    location: str = Field(..., min_length=1, max_length=500)
    capacity: int = Field(..., gt=0, le=100000)
    organizer: str = Field(..., min_length=1, max_length=200)
    status: str = Field(..., pattern=r"^(draft|published|cancelled|completed|active)$")
    waitlistEnabled: bool = False


class EventUpdate(BaseModel):
    """Model for updating an existing event."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    date: Optional[date] = None
    location: Optional[str] = Field(None, min_length=1, max_length=500)
    capacity: Optional[int] = Field(None, gt=0, le=100000)
    organizer: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = Field(None, pattern=r"^(draft|published|cancelled|completed|active)$")
    waitlistEnabled: Optional[bool] = None


class Event(EventBase):
    """Complete event model including the event ID."""
    eventId: str
    registrationCount: int = 0


# ============== Registration Models ==============

class RegistrationCreate(BaseModel):
    """Model for creating a registration."""
    userId: str = Field(..., min_length=1, max_length=100)


class Registration(BaseModel):
    """Complete registration model."""
    eventId: str
    userId: str
    registrationStatus: str  # "confirmed" or "waitlisted"
    registeredAt: str
    waitlistPosition: Optional[int] = None

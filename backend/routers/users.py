"""
User endpoints router.

This module defines API endpoints for user management.
"""

from fastapi import APIRouter

from models import User, UserCreate
from services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=User, status_code=201)
def create_user(user: UserCreate):
    """Create a new user."""
    return user_service.create_user(user)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: str):
    """Get a user by ID."""
    return user_service.get_user(user_id)

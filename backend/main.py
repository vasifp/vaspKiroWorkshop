"""
Events API - FastAPI REST Backend.

This module provides a REST API for managing events using AWS DynamoDB
as the data store. It supports CRUD operations with proper validation
and error handling.

API Endpoints:
    - GET /health: Health check endpoint
    - GET /events: List all events (optional status filter)
    - POST /events: Create a new event
    - GET /events/{event_id}: Get a specific event
    - PUT /events/{event_id}: Update an event
    - DELETE /events/{event_id}: Delete an event
"""

import os
import uuid
from typing import List, Optional

import boto3
from boto3.dynamodb.conditions import Attr
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from models import Event, EventCreate, EventUpdate

app = FastAPI(
    title="Events API",
    description="REST API for managing events",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TABLE_NAME = os.environ.get("TABLE_NAME", "Events")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


@app.get("/health")
def health():
    """Health check endpoint.
    
    Returns:
        dict: Status message indicating the API is healthy.
    """
    return {"status": "healthy"}


@app.post("/events", response_model=Event, status_code=201)
def create_event(event: EventCreate):
    """Create a new event.
    
    Args:
        event: Event data for creation.
        
    Returns:
        Event: The created event with its ID.
    """
    event_id = event.eventId if event.eventId else str(uuid.uuid4())
    item = {
        "eventId": event_id,
        "title": event.title,
        "description": event.description,
        "eventDate": str(event.date),
        "eventLocation": event.location,
        "eventCapacity": event.capacity,
        "organizer": event.organizer,
        "eventStatus": event.status,
    }
    table.put_item(Item=item)
    return _to_response(item)


@app.get("/events", response_model=List[Event])
def list_events(status: Optional[str] = Query(None)):
    """List all events with optional status filter.
    
    Args:
        status: Optional status to filter events by.
        
    Returns:
        List[Event]: List of events matching the filter criteria.
    """
    if status:
        response = table.scan(FilterExpression=Attr("eventStatus").eq(status))
    else:
        response = table.scan()
    items = response.get("Items", [])
    return [_to_response(item) for item in items]


@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: str):
    """Get a specific event by ID.
    
    Args:
        event_id: The unique identifier of the event.
        
    Returns:
        Event: The requested event.
        
    Raises:
        HTTPException: 404 if event not found.
    """
    response = table.get_item(Key={"eventId": event_id})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Event not found")
    return _to_response(item)


@app.put("/events/{event_id}", response_model=Event)
def update_event(event_id: str, event_update: EventUpdate):
    """Update an existing event.
    
    Args:
        event_id: The unique identifier of the event to update.
        event_update: The fields to update.
        
    Returns:
        Event: The updated event.
        
    Raises:
        HTTPException: 404 if event not found, 400 if no fields to update.
    """
    response = table.get_item(Key={"eventId": event_id})
    existing = response.get("Item")
    if not existing:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data = event_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

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

    table.put_item(Item=existing)
    return _to_response(existing)


@app.delete("/events/{event_id}")
def delete_event(event_id: str):
    """Delete an event.
    
    Args:
        event_id: The unique identifier of the event to delete.
        
    Returns:
        dict: Confirmation message.
        
    Raises:
        HTTPException: 404 if event not found.
    """
    response = table.get_item(Key={"eventId": event_id})
    if not response.get("Item"):
        raise HTTPException(status_code=404, detail="Event not found")
    table.delete_item(Key={"eventId": event_id})
    return {"message": "Event deleted"}


def _to_response(item: dict) -> dict:
    """Convert DynamoDB item to API response format.
    
    Maps internal DynamoDB field names (avoiding reserved keywords)
    to the external API field names.
    
    Args:
        item: DynamoDB item dictionary.
        
    Returns:
        dict: API response dictionary.
    """
    return {
        "eventId": item["eventId"],
        "title": item["title"],
        "description": item.get("description"),
        "date": item["eventDate"],
        "location": item["eventLocation"],
        "capacity": item["eventCapacity"],
        "organizer": item["organizer"],
        "status": item["eventStatus"],
    }


handler = Mangum(app)

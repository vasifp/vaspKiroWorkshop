"""
Events API - FastAPI REST Backend with User Registration.

This module provides a REST API for managing events and user registrations
using AWS DynamoDB with a single-table design (PK/SK pattern).
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional

import boto3
from boto3.dynamodb.conditions import Key, Attr
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from models import (
    Event, EventCreate, EventUpdate,
    User, UserCreate,
    Registration, RegistrationCreate
)

app = FastAPI(
    title="Events API",
    description="REST API for managing events and registrations",
    version="2.0.0"
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
    return {"status": "healthy"}


# ============== User Endpoints ==============

@app.post("/users", response_model=User, status_code=201)
def create_user(user: UserCreate):
    """Create a new user."""
    pk = f"USER#{user.userId}"
    sk = "METADATA"
    
    response = table.get_item(Key={"PK": pk, "SK": sk})
    if response.get("Item"):
        raise HTTPException(status_code=400, detail="User already exists")
    
    item = {
        "PK": pk,
        "SK": sk,
        "userId": user.userId,
        "userName": user.name,
        "createdAt": datetime.utcnow().isoformat(),
    }
    table.put_item(Item=item)
    return {"userId": user.userId, "name": user.name}


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str):
    """Get a user by ID."""
    pk = f"USER#{user_id}"
    sk = "METADATA"
    
    response = table.get_item(Key={"PK": pk, "SK": sk})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"userId": item["userId"], "name": item["userName"]}


# ============== Event Endpoints ==============

@app.post("/events", response_model=Event, status_code=201)
def create_event(event: EventCreate):
    """Create a new event."""
    event_id = event.eventId if event.eventId else str(uuid.uuid4())
    pk = f"EVENT#{event_id}"
    sk = "METADATA"
    
    item = {
        "PK": pk,
        "SK": sk,
        "eventId": event_id,
        "title": event.title,
        "description": event.description,
        "eventDate": str(event.date),
        "eventLocation": event.location,
        "eventCapacity": event.capacity,
        "organizer": event.organizer,
        "eventStatus": event.status,
        "waitlistEnabled": event.waitlistEnabled,
        "registrationCount": 0,
    }
    table.put_item(Item=item)
    return _event_to_response(item)


@app.get("/events", response_model=List[Event])
def list_events(status: Optional[str] = Query(None)):
    """List all events with optional status filter."""
    response = table.scan(
        FilterExpression=Attr("SK").eq("METADATA") & Attr("PK").begins_with("EVENT#")
    )
    items = response.get("Items", [])
    
    if status:
        items = [i for i in items if i.get("eventStatus") == status]
    
    return [_event_to_response(item) for item in items]


@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: str):
    """Get a specific event by ID."""
    pk = f"EVENT#{event_id}"
    sk = "METADATA"
    
    response = table.get_item(Key={"PK": pk, "SK": sk})
    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return _event_to_response(item)


@app.put("/events/{event_id}", response_model=Event)
def update_event(event_id: str, event_update: EventUpdate):
    """Update an existing event."""
    pk = f"EVENT#{event_id}"
    sk = "METADATA"
    
    response = table.get_item(Key={"PK": pk, "SK": sk})
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
    if "waitlistEnabled" in update_data:
        existing["waitlistEnabled"] = update_data["waitlistEnabled"]

    table.put_item(Item=existing)
    return _event_to_response(existing)


@app.delete("/events/{event_id}")
def delete_event(event_id: str):
    """Delete an event."""
    pk = f"EVENT#{event_id}"
    sk = "METADATA"
    
    response = table.get_item(Key={"PK": pk, "SK": sk})
    if not response.get("Item"):
        raise HTTPException(status_code=404, detail="Event not found")
    
    table.delete_item(Key={"PK": pk, "SK": sk})
    return {"message": "Event deleted"}


# ============== Registration Endpoints ==============

@app.post("/events/{event_id}/registrations", response_model=Registration, status_code=201)
def register_for_event(event_id: str, registration: RegistrationCreate):
    """Register a user for an event."""
    event_pk = f"EVENT#{event_id}"
    event_sk = "METADATA"
    
    # Get event
    event_response = table.get_item(Key={"PK": event_pk, "SK": event_sk})
    event_item = event_response.get("Item")
    if not event_item:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check user exists
    user_pk = f"USER#{registration.userId}"
    user_response = table.get_item(Key={"PK": user_pk, "SK": "METADATA"})
    if not user_response.get("Item"):
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already registered
    reg_sk = f"REG#{registration.userId}"
    existing_reg = table.get_item(Key={"PK": event_pk, "SK": reg_sk})
    if existing_reg.get("Item"):
        raise HTTPException(status_code=400, detail="Already registered")
    
    capacity = event_item.get("eventCapacity", 0)
    reg_count = event_item.get("registrationCount", 0)
    waitlist_enabled = event_item.get("waitlistEnabled", False)
    
    now = datetime.utcnow().isoformat()
    
    if reg_count < capacity:
        reg_status = "confirmed"
        waitlist_pos = None
        new_reg_count = reg_count + 1
    elif waitlist_enabled:
        reg_status = "waitlisted"
        # Get current waitlist count
        waitlist_response = table.query(
            KeyConditionExpression=Key("PK").eq(event_pk) & Key("SK").begins_with("REG#"),
            FilterExpression=Attr("registrationStatus").eq("waitlisted")
        )
        waitlist_pos = len(waitlist_response.get("Items", [])) + 1
        new_reg_count = reg_count
    else:
        raise HTTPException(status_code=400, detail="Event is full")
    
    # Create registration record (event side)
    event_reg_item = {
        "PK": event_pk,
        "SK": reg_sk,
        "eventId": event_id,
        "userId": registration.userId,
        "registrationStatus": reg_status,
        "registeredAt": now,
        "waitlistPosition": waitlist_pos,
        "GSI1PK": user_pk,
        "GSI1SK": f"REG#{event_id}",
    }
    table.put_item(Item=event_reg_item)
    
    # Update event registration count if confirmed
    if reg_status == "confirmed":
        table.update_item(
            Key={"PK": event_pk, "SK": event_sk},
            UpdateExpression="SET registrationCount = :count",
            ExpressionAttributeValues={":count": new_reg_count}
        )
    
    return {
        "eventId": event_id,
        "userId": registration.userId,
        "registrationStatus": reg_status,
        "registeredAt": now,
        "waitlistPosition": waitlist_pos,
    }


@app.delete("/events/{event_id}/registrations/{user_id}")
def unregister_from_event(event_id: str, user_id: str):
    """Unregister a user from an event."""
    event_pk = f"EVENT#{event_id}"
    event_sk = "METADATA"
    reg_sk = f"REG#{user_id}"
    
    # Get registration
    reg_response = table.get_item(Key={"PK": event_pk, "SK": reg_sk})
    reg_item = reg_response.get("Item")
    if not reg_item:
        raise HTTPException(status_code=400, detail="Not registered for this event")
    
    was_confirmed = reg_item.get("registrationStatus") == "confirmed"
    
    # Delete registration
    table.delete_item(Key={"PK": event_pk, "SK": reg_sk})
    
    # If was confirmed, promote from waitlist and update count
    if was_confirmed:
        # Get event
        event_response = table.get_item(Key={"PK": event_pk, "SK": event_sk})
        event_item = event_response.get("Item")
        
        if event_item:
            reg_count = event_item.get("registrationCount", 1)
            
            # Check for waitlisted users
            waitlist_response = table.query(
                KeyConditionExpression=Key("PK").eq(event_pk) & Key("SK").begins_with("REG#"),
                FilterExpression=Attr("registrationStatus").eq("waitlisted")
            )
            waitlisted = waitlist_response.get("Items", [])
            
            if waitlisted:
                # Promote first waitlisted user
                waitlisted.sort(key=lambda x: x.get("waitlistPosition", 999))
                first = waitlisted[0]
                table.update_item(
                    Key={"PK": event_pk, "SK": first["SK"]},
                    UpdateExpression="SET registrationStatus = :status, waitlistPosition = :pos",
                    ExpressionAttributeValues={":status": "confirmed", ":pos": None}
                )
            else:
                # Decrement registration count
                table.update_item(
                    Key={"PK": event_pk, "SK": event_sk},
                    UpdateExpression="SET registrationCount = :count",
                    ExpressionAttributeValues={":count": max(0, reg_count - 1)}
                )
    
    return {"message": "Unregistered successfully"}


@app.get("/users/{user_id}/registrations", response_model=List[Registration])
def get_user_registrations(user_id: str):
    """Get all registrations for a user."""
    # Check user exists
    user_pk = f"USER#{user_id}"
    user_response = table.get_item(Key={"PK": user_pk, "SK": "METADATA"})
    if not user_response.get("Item"):
        raise HTTPException(status_code=404, detail="User not found")
    
    # Query GSI for user's registrations
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq(user_pk) & Key("GSI1SK").begins_with("REG#")
    )
    
    items = response.get("Items", [])
    return [
        {
            "eventId": item["eventId"],
            "userId": item["userId"],
            "registrationStatus": item["registrationStatus"],
            "registeredAt": item["registeredAt"],
            "waitlistPosition": item.get("waitlistPosition"),
        }
        for item in items
    ]


# ============== Helper Functions ==============

def _event_to_response(item: dict) -> dict:
    """Convert DynamoDB event item to API response format."""
    return {
        "eventId": item["eventId"],
        "title": item["title"],
        "description": item.get("description"),
        "date": item["eventDate"],
        "location": item["eventLocation"],
        "capacity": item["eventCapacity"],
        "organizer": item["organizer"],
        "status": item["eventStatus"],
        "waitlistEnabled": item.get("waitlistEnabled", False),
        "registrationCount": item.get("registrationCount", 0),
    }


handler = Mangum(app)

"""
Repository layer for DynamoDB operations.

This module encapsulates all DynamoDB operations for users, events, and registrations
using a single-table design with PK/SK pattern.
"""

import os
from datetime import datetime
from typing import List, Optional

import boto3
from boto3.dynamodb.conditions import Key, Attr


TABLE_NAME = os.environ.get("TABLE_NAME", "Events")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


class Repository:
    """Repository for all DynamoDB operations."""

    # ============== Key Construction ==============

    @staticmethod
    def _user_pk(user_id: str) -> str:
        """Construct user partition key."""
        return f"USER#{user_id}"

    @staticmethod
    def _event_pk(event_id: str) -> str:
        """Construct event partition key."""
        return f"EVENT#{event_id}"

    @staticmethod
    def _registration_sk(user_id: str) -> str:
        """Construct registration sort key."""
        return f"REG#{user_id}"

    @staticmethod
    def _metadata_sk() -> str:
        """Construct metadata sort key."""
        return "METADATA"

    # ============== User Operations ==============

    def get_user(self, user_id: str) -> Optional[dict]:
        """Get a user by ID. Returns None if not found."""
        pk = self._user_pk(user_id)
        sk = self._metadata_sk()

        response = table.get_item(Key={"PK": pk, "SK": sk})
        item = response.get("Item")

        if not item:
            return None

        return {"userId": item["userId"], "name": item["userName"]}

    def user_exists(self, user_id: str) -> bool:
        """Check if a user exists."""
        pk = self._user_pk(user_id)
        sk = self._metadata_sk()

        response = table.get_item(Key={"PK": pk, "SK": sk})
        return response.get("Item") is not None

    def create_user(self, user_id: str, name: str) -> dict:
        """Create a new user. Returns the created user."""
        pk = self._user_pk(user_id)
        sk = self._metadata_sk()

        item = {
            "PK": pk,
            "SK": sk,
            "userId": user_id,
            "userName": name,
            "createdAt": datetime.utcnow().isoformat(),
        }
        table.put_item(Item=item)

        return {"userId": user_id, "name": name}

    # ============== Event Operations ==============

    def get_event(self, event_id: str) -> Optional[dict]:
        """Get an event by ID. Returns None if not found."""
        pk = self._event_pk(event_id)
        sk = self._metadata_sk()

        response = table.get_item(Key={"PK": pk, "SK": sk})
        item = response.get("Item")

        if not item:
            return None

        return self._event_item_to_dict(item)

    def get_event_raw(self, event_id: str) -> Optional[dict]:
        """Get raw DynamoDB event item. Returns None if not found."""
        pk = self._event_pk(event_id)
        sk = self._metadata_sk()

        response = table.get_item(Key={"PK": pk, "SK": sk})
        return response.get("Item")

    def create_event(self, event_data: dict) -> dict:
        """Create a new event. Returns the created event."""
        event_id = event_data["eventId"]
        pk = self._event_pk(event_id)
        sk = self._metadata_sk()

        item = {
            "PK": pk,
            "SK": sk,
            "eventId": event_id,
            "title": event_data["title"],
            "description": event_data.get("description"),
            "eventDate": str(event_data["date"]),
            "eventLocation": event_data["location"],
            "eventCapacity": event_data["capacity"],
            "organizer": event_data["organizer"],
            "eventStatus": event_data["status"],
            "waitlistEnabled": event_data.get("waitlistEnabled", False),
            "registrationCount": 0,
        }
        table.put_item(Item=item)

        return self._event_item_to_dict(item)

    def update_event(self, event_id: str, existing_item: dict) -> dict:
        """Update an existing event item. Returns the updated event."""
        table.put_item(Item=existing_item)
        return self._event_item_to_dict(existing_item)

    def delete_event(self, event_id: str) -> bool:
        """Delete an event. Returns True if deleted."""
        pk = self._event_pk(event_id)
        sk = self._metadata_sk()

        table.delete_item(Key={"PK": pk, "SK": sk})
        return True

    def list_events(self, status: Optional[str] = None) -> List[dict]:
        """List all events with optional status filter."""
        response = table.scan(
            FilterExpression=Attr("SK").eq("METADATA") & Attr("PK").begins_with("EVENT#")
        )
        items = response.get("Items", [])

        if status:
            items = [i for i in items if i.get("eventStatus") == status]

        return [self._event_item_to_dict(item) for item in items]

    def update_event_registration_count(self, event_id: str, count: int) -> None:
        """Update the registration count for an event."""
        pk = self._event_pk(event_id)
        sk = self._metadata_sk()

        table.update_item(
            Key={"PK": pk, "SK": sk},
            UpdateExpression="SET registrationCount = :count",
            ExpressionAttributeValues={":count": count}
        )


    # ============== Registration Operations ==============

    def get_registration(self, event_id: str, user_id: str) -> Optional[dict]:
        """Get a registration by event and user ID. Returns None if not found."""
        pk = self._event_pk(event_id)
        sk = self._registration_sk(user_id)

        response = table.get_item(Key={"PK": pk, "SK": sk})
        item = response.get("Item")

        if not item:
            return None

        return self._registration_item_to_dict(item)

    def get_registration_raw(self, event_id: str, user_id: str) -> Optional[dict]:
        """Get raw DynamoDB registration item. Returns None if not found."""
        pk = self._event_pk(event_id)
        sk = self._registration_sk(user_id)

        response = table.get_item(Key={"PK": pk, "SK": sk})
        return response.get("Item")

    def create_registration(
        self,
        event_id: str,
        user_id: str,
        status: str,
        registered_at: str,
        waitlist_pos: Optional[int] = None
    ) -> dict:
        """Create a new registration. Returns the created registration."""
        event_pk = self._event_pk(event_id)
        user_pk = self._user_pk(user_id)
        reg_sk = self._registration_sk(user_id)

        item = {
            "PK": event_pk,
            "SK": reg_sk,
            "eventId": event_id,
            "userId": user_id,
            "registrationStatus": status,
            "registeredAt": registered_at,
            "waitlistPosition": waitlist_pos,
            "GSI1PK": user_pk,
            "GSI1SK": f"REG#{event_id}",
        }
        table.put_item(Item=item)

        return self._registration_item_to_dict(item)

    def delete_registration(self, event_id: str, user_id: str) -> bool:
        """Delete a registration. Returns True if deleted."""
        pk = self._event_pk(event_id)
        sk = self._registration_sk(user_id)

        table.delete_item(Key={"PK": pk, "SK": sk})
        return True

    def get_event_registrations(
        self,
        event_id: str,
        status: Optional[str] = None
    ) -> List[dict]:
        """Get all registrations for an event with optional status filter."""
        pk = self._event_pk(event_id)

        if status:
            response = table.query(
                KeyConditionExpression=Key("PK").eq(pk) & Key("SK").begins_with("REG#"),
                FilterExpression=Attr("registrationStatus").eq(status)
            )
        else:
            response = table.query(
                KeyConditionExpression=Key("PK").eq(pk) & Key("SK").begins_with("REG#")
            )

        items = response.get("Items", [])
        return [self._registration_item_to_dict(item) for item in items]

    def get_waitlisted_registrations(self, event_id: str) -> List[dict]:
        """Get all waitlisted registrations for an event, sorted by position."""
        registrations = self.get_event_registrations(event_id, status="waitlisted")
        registrations.sort(key=lambda x: x.get("waitlistPosition") or 999)
        return registrations

    def get_user_registrations(self, user_id: str) -> List[dict]:
        """Get all registrations for a user using GSI."""
        user_pk = self._user_pk(user_id)

        response = table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(user_pk) & Key("GSI1SK").begins_with("REG#")
        )

        items = response.get("Items", [])
        return [self._registration_item_to_dict(item) for item in items]

    def update_registration_status(
        self,
        event_id: str,
        user_id: str,
        status: str,
        waitlist_pos: Optional[int] = None
    ) -> None:
        """Update the status and waitlist position of a registration."""
        pk = self._event_pk(event_id)
        sk = self._registration_sk(user_id)

        table.update_item(
            Key={"PK": pk, "SK": sk},
            UpdateExpression="SET registrationStatus = :status, waitlistPosition = :pos",
            ExpressionAttributeValues={":status": status, ":pos": waitlist_pos}
        )

    # ============== Helper Methods ==============

    @staticmethod
    def _event_item_to_dict(item: dict) -> dict:
        """Convert DynamoDB event item to domain dict."""
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

    @staticmethod
    def _registration_item_to_dict(item: dict) -> dict:
        """Convert DynamoDB registration item to domain dict."""
        return {
            "eventId": item["eventId"],
            "userId": item["userId"],
            "registrationStatus": item["registrationStatus"],
            "registeredAt": item["registeredAt"],
            "waitlistPosition": item.get("waitlistPosition"),
        }


# Singleton instance for use across the application
repository = Repository()

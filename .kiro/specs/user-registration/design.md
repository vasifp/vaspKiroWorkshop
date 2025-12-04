# Design Document: User Registration Feature

## Overview

This feature extends the Events API to support user management and event registration. Users can register for events with capacity constraints and optional waitlists. The system uses a single-table DynamoDB design with composite keys (PK/SK) for efficient access patterns.

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│ API Gateway │────▶│   Lambda    │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
                                        ┌─────────────┐
                                        │  DynamoDB   │
                                        │ (Single     │
                                        │  Table)     │
                                        └─────────────┘
```

## Components and Interfaces

### New API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/users` | Create a new user |
| GET | `/users/{userId}` | Get user details |
| POST | `/events/{eventId}/registrations` | Register user for event |
| DELETE | `/events/{eventId}/registrations/{userId}` | Unregister user |
| GET | `/users/{userId}/registrations` | List user's registrations |

### Updated Event Endpoints

Events now include `waitlistEnabled` field (default: false).

## Data Models

### Single-Table Design (PK/SK Pattern)

| Entity | PK | SK | Attributes |
|--------|----|----|------------|
| Event | `EVENT#{eventId}` | `METADATA` | title, description, date, location, capacity, organizer, status, waitlistEnabled, registrationCount |
| User | `USER#{userId}` | `METADATA` | name, createdAt |
| Registration | `EVENT#{eventId}` | `REG#{userId}` | status (confirmed/waitlisted), registeredAt, waitlistPosition |
| UserRegistration | `USER#{userId}` | `REG#{eventId}` | status, registeredAt (for querying user's events) |

### Pydantic Models

```python
class UserCreate(BaseModel):
    userId: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=200)

class User(BaseModel):
    userId: str
    name: str

class RegistrationCreate(BaseModel):
    userId: str

class Registration(BaseModel):
    eventId: str
    userId: str
    status: str  # "confirmed" or "waitlisted"
    registeredAt: str

class EventCreate(BaseModel):  # Updated
    # ... existing fields ...
    waitlistEnabled: bool = False
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: User creation returns stored data
*For any* valid user creation request with non-empty userId and name, the system should store the user and return data matching the input.
**Validates: Requirements 1.1**

### Property 2: Empty/whitespace user fields are rejected
*For any* user creation request where userId or name consists only of whitespace characters, the system should reject the request with a validation error.
**Validates: Requirements 1.3**

### Property 3: Event capacity and waitlist fields are persisted
*For any* event created or updated with capacity and waitlistEnabled values, the system should store and return these fields correctly.
**Validates: Requirements 2.1**

### Property 4: Positive capacity validation
*For any* event creation or update with a non-positive capacity value, the system should reject the request with a validation error.
**Validates: Requirements 2.3**

### Property 5: Registration with available capacity succeeds as confirmed
*For any* event with registrationCount < capacity, when a new user registers, the system should create a registration with status "confirmed".
**Validates: Requirements 3.1**

### Property 6: Registration timestamp is recorded
*For any* successful registration (confirmed or waitlisted), the system should record a registeredAt timestamp.
**Validates: Requirements 3.5**

### Property 7: Unregistration removes the registration
*For any* registered user who unregisters from an event, the system should remove their registration and it should no longer appear in queries.
**Validates: Requirements 4.1**

### Property 8: Waitlist removal preserves other positions
*For any* waitlisted user who unregisters, the remaining waitlisted users should maintain their relative order.
**Validates: Requirements 4.3**

### Property 9: User registrations list completeness
*For any* user registered for N events, querying their registrations should return exactly N items.
**Validates: Requirements 5.1**

### Property 10: Registration status is included in list
*For any* registration returned in a user's registration list, the status field should be either "confirmed" or "waitlisted".
**Validates: Requirements 5.2**

## Error Handling

| Scenario | Status Code | Response |
|----------|-------------|----------|
| User not found | 404 | `{"detail": "User not found"}` |
| Event not found | 404 | `{"detail": "Event not found"}` |
| Duplicate user ID | 400 | `{"detail": "User already exists"}` |
| Event full (no waitlist) | 400 | `{"detail": "Event is full"}` |
| Already registered | 400 | `{"detail": "Already registered"}` |
| Not registered | 400 | `{"detail": "Not registered for this event"}` |
| Validation error | 422 | Pydantic validation details |

## Testing Strategy

### Unit Tests
- Test Pydantic model validation for all new models
- Test helper functions for DynamoDB key generation

### Property-Based Tests
Use `hypothesis` library for property-based testing:
- Configure minimum 100 iterations per property test
- Tag each test with: `**Feature: user-registration, Property {number}: {property_text}**`

Properties to implement:
1. User creation round-trip
2. Input validation rejection
3. Registration capacity logic
4. Waitlist ordering preservation
5. Registration list completeness

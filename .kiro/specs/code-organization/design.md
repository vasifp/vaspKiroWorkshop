# Design Document: Code Organization

## Overview

This design refactors the Events API backend from a monolithic `main.py` into a layered architecture with clear separation of concerns. The refactoring introduces:
- **Repository layer**: Handles all DynamoDB operations
- **Service layer**: Contains business logic
- **Router layer**: Thin API handlers that delegate to services

The architecture is intentionally simple to minimize refactoring complexity while achieving the core goals.

## Architecture

```
backend/
├── main.py              # App initialization, middleware, Lambda handler
├── models.py            # Pydantic models (unchanged)
├── repository.py        # DynamoDB operations for all entities
├── services.py          # Business logic for all entities
└── routers/
    ├── __init__.py
    ├── events.py        # Event endpoints
    ├── users.py         # User endpoints
    └── registrations.py # Registration endpoints
```

### Layer Responsibilities

1. **Routers** (`routers/*.py`): 
   - Define FastAPI routes
   - Parse request data
   - Call service methods
   - Return HTTP responses

2. **Services** (`services.py`):
   - Implement business logic
   - Coordinate between repositories
   - Handle business validation
   - Raise HTTPException for errors

3. **Repository** (`repository.py`):
   - All DynamoDB get/put/delete/query/scan operations
   - PK/SK key construction
   - Data transformation between DynamoDB and Python dicts

## Components and Interfaces

### Repository Interface

```python
class Repository:
    # User operations
    def get_user(user_id: str) -> Optional[dict]
    def create_user(user_id: str, name: str) -> dict
    def user_exists(user_id: str) -> bool
    
    # Event operations
    def get_event(event_id: str) -> Optional[dict]
    def create_event(event_data: dict) -> dict
    def update_event(event_id: str, updates: dict) -> dict
    def delete_event(event_id: str) -> bool
    def list_events(status: Optional[str]) -> List[dict]
    
    # Registration operations
    def get_registration(event_id: str, user_id: str) -> Optional[dict]
    def create_registration(event_id: str, user_id: str, status: str, waitlist_pos: Optional[int]) -> dict
    def delete_registration(event_id: str, user_id: str) -> bool
    def get_event_registrations(event_id: str, status: Optional[str]) -> List[dict]
    def get_user_registrations(user_id: str) -> List[dict]
    def update_registration_status(event_id: str, user_id: str, status: str) -> None
    def update_event_registration_count(event_id: str, count: int) -> None
```

### Service Interface

```python
class UserService:
    def create_user(user: UserCreate) -> User
    def get_user(user_id: str) -> User

class EventService:
    def create_event(event: EventCreate) -> Event
    def get_event(event_id: str) -> Event
    def list_events(status: Optional[str]) -> List[Event]
    def update_event(event_id: str, update: EventUpdate) -> Event
    def delete_event(event_id: str) -> dict

class RegistrationService:
    def register(event_id: str, user_id: str) -> Registration
    def unregister(event_id: str, user_id: str) -> dict
    def get_user_registrations(user_id: str) -> List[Registration]
```

## Data Models

No changes to existing Pydantic models in `models.py`. The models remain the API contract.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


Based on the prework analysis, most requirements are architectural (code organization) rather than functional. The key testable property is API equivalence after refactoring.

### Property 1: API Response Equivalence

*For any* valid API request to any endpoint, the refactored system SHALL return an identical response (same status code, same response body structure, same error messages) as the original implementation.

**Validates: Requirements 4.1, 4.2, 4.3**

## Error Handling

Error handling remains unchanged. All HTTPException raises move from `main.py` to `services.py`, maintaining:
- 400 for validation errors and business rule violations
- 404 for not found resources
- Same error message strings

## Testing Strategy

### Approach

Since this is a refactoring task, the primary testing strategy is **regression testing** - verifying that all existing functionality works identically after the refactor.

### Manual Verification

After refactoring, manually test all endpoints:
1. `GET /health`
2. `POST /users`, `GET /users/{id}`
3. `POST /events`, `GET /events`, `GET /events/{id}`, `PUT /events/{id}`, `DELETE /events/{id}`
4. `POST /events/{id}/registrations`, `DELETE /events/{id}/registrations/{user_id}`
5. `GET /users/{id}/registrations`

### Property-Based Testing (Optional)

Use `hypothesis` library to generate random valid requests and compare responses between original and refactored implementations. This would validate Property 1 across many inputs.

## Migration Strategy

1. Create new files (`repository.py`, `services.py`, `routers/`)
2. Move code incrementally, keeping `main.py` functional at each step
3. Deploy and verify after complete migration

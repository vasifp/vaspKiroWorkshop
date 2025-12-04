# Business Logic Separation

Business logic is separated into dedicated files.

## Guidelines

When working with the backend codebase:

1. **Services contain business logic** - All business rules, validation, and domain logic should be in service modules (`services.py`)
2. **Routers are thin** - API handlers should only parse requests, call services, and return responses
3. **Repositories handle data** - Database operations belong in repository modules (`repository.py`)

## File Structure

```
backend/
├── main.py          # App initialization only
├── models.py        # Pydantic models
├── repository.py    # Database operations
├── services.py      # Business logic
└── routers/         # API endpoints
    ├── users.py
    ├── events.py
    └── registrations.py
```

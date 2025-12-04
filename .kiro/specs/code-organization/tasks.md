# Implementation Plan

- [ ] 1. Create Repository layer
  - [ ] 1.1 Create `backend/repository.py` with DynamoDB operations
    - Move table initialization and all DynamoDB operations from main.py
    - Implement user, event, and registration repository methods
    - Encapsulate PK/SK key construction
    - _Requirements: 1.1, 1.2, 1.3_

- [ ] 2. Create Services layer
  - [ ] 2.1 Create `backend/services.py` with business logic
    - Implement UserService, EventService, RegistrationService classes
    - Move business logic from main.py (validation, waitlist promotion, etc.)
    - Services call repository methods for data access
    - _Requirements: 2.1, 2.2, 2.3_

- [ ] 3. Create Router layer
  - [ ] 3.1 Create `backend/routers/__init__.py`
    - Empty init file for routers package
    - _Requirements: 3.1_
  - [ ] 3.2 Create `backend/routers/users.py`
    - Move user endpoints from main.py
    - Thin handlers that call UserService
    - _Requirements: 3.1, 3.2_
  - [ ] 3.3 Create `backend/routers/events.py`
    - Move event endpoints from main.py
    - Thin handlers that call EventService
    - _Requirements: 3.1, 3.2_
  - [ ] 3.4 Create `backend/routers/registrations.py`
    - Move registration endpoints from main.py
    - Thin handlers that call RegistrationService
    - _Requirements: 3.1, 3.2_

- [ ] 4. Update main.py
  - [ ] 4.1 Refactor `backend/main.py` to use routers
    - Keep FastAPI app initialization and middleware
    - Import and include all routers
    - Remove all endpoint definitions (now in routers)
    - Keep Mangum handler
    - _Requirements: 3.3_

- [ ] 5. Deploy and verify
  - [ ] 5.1 Deploy refactored application
    - Run `cdk deploy` to update Lambda
    - _Requirements: 4.1, 4.2, 4.3_
  - [ ] 5.2 Verify all endpoints work correctly
    - Test all user, event, and registration endpoints
    - Verify same responses as before refactoring
    - _Requirements: 4.1, 4.2, 4.3_

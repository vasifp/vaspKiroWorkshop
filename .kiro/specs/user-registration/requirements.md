# Requirements Document

## Introduction

This document specifies the requirements for a user registration feature that allows users to register for events. The system supports capacity constraints with optional waitlists, enabling users to register, unregister, and view their registered events.

## Glossary

- **User**: A person who can register for events, identified by a unique userId
- **Event**: An organized activity with a title, date, location, capacity, and optional waitlist
- **Registration**: A record linking a user to an event they have signed up for
- **Waitlist**: An ordered queue of users waiting for a spot when an event is at capacity
- **Capacity**: The maximum number of confirmed registrations allowed for an event
- **waitlistEnabled**: A boolean flag indicating whether an event accepts waitlist entries when full

## Requirements

### Requirement 1

**User Story:** As a system administrator, I want to create users with basic information, so that they can register for events.

#### Acceptance Criteria

1. WHEN a user is created with a userId and name THEN the System SHALL store the user and return the created user data
2. WHEN a user attempts to create a user with an existing userId THEN the System SHALL reject the request with an error
3. WHEN a user is created THEN the System SHALL validate that userId and name are non-empty strings

### Requirement 2

**User Story:** As an event organizer, I want to configure events with capacity constraints and optional waitlists, so that I can manage attendance.

#### Acceptance Criteria

1. WHEN an event is created or updated THEN the System SHALL accept a capacity value and a waitlistEnabled flag
2. WHEN waitlistEnabled is not specified THEN the System SHALL default it to false
3. WHEN capacity is specified THEN the System SHALL validate it is a positive integer

### Requirement 3

**User Story:** As a user, I want to register for an event, so that I can attend it.

#### Acceptance Criteria

1. WHEN a user registers for an event with available capacity THEN the System SHALL create a confirmed registration
2. WHEN a user registers for a full event without waitlist THEN the System SHALL reject the registration with an error
3. WHEN a user registers for a full event with waitlist enabled THEN the System SHALL add the user to the waitlist
4. WHEN a user attempts to register for an event they are already registered for THEN the System SHALL reject the request
5. WHEN a registration is created THEN the System SHALL record the registration timestamp

### Requirement 4

**User Story:** As a user, I want to unregister from an event, so that I can free up my spot.

#### Acceptance Criteria

1. WHEN a user unregisters from an event THEN the System SHALL remove their registration
2. WHEN a confirmed user unregisters and a waitlist exists THEN the System SHALL promote the first waitlisted user to confirmed
3. WHEN a waitlisted user unregisters THEN the System SHALL remove them from the waitlist without affecting others
4. WHEN a user attempts to unregister from an event they are not registered for THEN the System SHALL return an error

### Requirement 5

**User Story:** As a user, I want to list the events I am registered for, so that I can see my schedule.

#### Acceptance Criteria

1. WHEN a user requests their registrations THEN the System SHALL return all events they are registered for
2. WHEN listing registrations THEN the System SHALL include the registration status (confirmed or waitlisted)
3. WHEN a user has no registrations THEN the System SHALL return an empty list

### Requirement 6

**User Story:** As a developer, I want the data model to use a consistent composite key schema, so that the system is scalable and maintainable.

#### Acceptance Criteria

1. WHEN storing data in DynamoDB THEN the System SHALL use a composite key schema with PK (partition key) and SK (sort key)
2. WHEN migrating existing event data THEN the System SHALL update the schema to use PK/SK pattern
3. WHEN querying data THEN the System SHALL use efficient key-based access patterns

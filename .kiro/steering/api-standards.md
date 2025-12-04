---
inclusion: fileMatch
fileMatchPattern: "**/*.py"
---

# REST API Standards

When working with API files, follow these conventions:

## HTTP Methods
- `GET` - Retrieve resources (no request body)
- `POST` - Create new resources (returns 201 with created resource)
- `PUT` - Full update of existing resources
- `PATCH` - Partial update of existing resources
- `DELETE` - Remove resources (returns 200 or 204)

## Status Codes
- `200 OK` - Successful GET, PUT, PATCH, DELETE
- `201 Created` - Successful POST (include created resource in response)
- `204 No Content` - Successful DELETE with no response body
- `400 Bad Request` - Invalid request data or validation errors
- `404 Not Found` - Resource does not exist
- `422 Unprocessable Entity` - Validation failed
- `500 Internal Server Error` - Server-side errors

## JSON Response Format

### Success Response
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

### List Response
```json
[
  {"id": "1", "name": "Item 1"},
  {"id": "2", "name": "Item 2"}
]
```

### Error Response
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Naming Conventions
- Use plural nouns for resource endpoints: `/events`, `/users`
- Use kebab-case for multi-word paths: `/event-categories`
- Use camelCase for JSON field names: `eventId`, `createdAt`

## Query Parameters
- Use for filtering: `GET /events?status=active`
- Use for pagination: `GET /events?page=1&limit=10`
- Use for sorting: `GET /events?sort=date&order=desc`

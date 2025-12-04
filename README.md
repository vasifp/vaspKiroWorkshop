# Events Management API

A serverless REST API for managing events, built with FastAPI and deployed on AWS using CDK.

## Architecture

- **Backend**: FastAPI with Pydantic validation
- **Database**: Amazon DynamoDB
- **Compute**: AWS Lambda
- **API**: Amazon API Gateway
- **Infrastructure**: AWS CDK (TypeScript)

## Project Structure

```
.
├── backend/                 # FastAPI application
│   ├── main.py             # API endpoints
│   ├── models.py           # Pydantic models
│   ├── requirements.txt    # Python dependencies
│   └── docs/               # Generated API documentation
├── infrastructure/          # CDK infrastructure code
│   ├── lib/
│   │   └── infrastructure-stack.ts
│   └── bin/
│       └── infrastructure.ts
└── README.md
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/events` | List all events |
| GET | `/events?status={status}` | Filter events by status |
| POST | `/events` | Create a new event |
| GET | `/events/{eventId}` | Get a specific event |
| PUT | `/events/{eventId}` | Update an event |
| DELETE | `/events/{eventId}` | Delete an event |

## Event Schema

```json
{
  "eventId": "string",
  "title": "string",
  "description": "string (optional)",
  "date": "YYYY-MM-DD",
  "location": "string",
  "capacity": "integer",
  "organizer": "string",
  "status": "draft|published|cancelled|completed|active"
}
```

## Setup

### Prerequisites

- Node.js 18+
- Python 3.12+
- AWS CLI configured
- Docker (for CDK bundling)

### Installation

1. Install CDK dependencies:
```bash
cd infrastructure
npm install
```

2. Install Python dependencies (for local development):
```bash
cd backend
pip install -r requirements.txt
```

### Deployment

1. Bootstrap CDK (first time only):
```bash
cd infrastructure
npx cdk bootstrap
```

2. Deploy the stack:
```bash
npx cdk deploy
```

The API endpoint URL will be displayed in the outputs.

## Usage Examples

### Create an Event
```bash
curl -X POST https://YOUR_API_URL/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tech Conference 2024",
    "description": "Annual technology conference",
    "date": "2024-12-15",
    "location": "San Francisco, CA",
    "capacity": 500,
    "organizer": "Tech Events Inc",
    "status": "published"
  }'
```

### List All Events
```bash
curl https://YOUR_API_URL/events
```

### Filter Events by Status
```bash
curl "https://YOUR_API_URL/events?status=active"
```

### Get a Specific Event
```bash
curl https://YOUR_API_URL/events/{eventId}
```

### Update an Event
```bash
curl -X PUT https://YOUR_API_URL/events/{eventId} \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Event Title",
    "capacity": 750
  }'
```

### Delete an Event
```bash
curl -X DELETE https://YOUR_API_URL/events/{eventId}
```

## API Documentation

Generated API documentation is available in `backend/docs/`. To regenerate:

```bash
cd backend
pip install pdoc
pdoc main models -o ./docs
```

## Development

### Local Testing

Run the FastAPI server locally:
```bash
cd backend
uvicorn main:app --reload
```

Access the interactive API docs at `http://localhost:8000/docs`.

## License

MIT

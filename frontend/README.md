# Events Management Frontend

A React TypeScript application built with Vite and CloudScape Design components for managing events, users, and registrations.

## Prerequisites

- Node.js 18+ 
- npm or yarn

## Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure API endpoint (optional):

The default API endpoint is set to the deployed AWS API Gateway. To change it:

**Option 1: Environment variable**
```bash
export VITE_API_URL=https://your-api-endpoint.execute-api.region.amazonaws.com/prod
npm run dev
```

**Option 2: Create `.env.local` file**
```
VITE_API_URL=https://your-api-endpoint.execute-api.region.amazonaws.com/prod
```

**Option 3: Edit `src/config.ts` directly**

## Running the Application

Development mode:
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Features

- **Events Management**: Create, view, edit, and delete events
- **User Management**: Create users for event registration
- **Registration Management**: Register/unregister users for events, view user registrations

## API Endpoints Used

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /events | List all events |
| POST | /events | Create event |
| GET | /events/{id} | Get event |
| PUT | /events/{id} | Update event |
| DELETE | /events/{id} | Delete event |
| POST | /users | Create user |
| GET | /users/{id} | Get user |
| POST | /events/{id}/registrations | Register user |
| DELETE | /events/{id}/registrations/{userId} | Unregister user |
| GET | /users/{id}/registrations | Get user registrations |

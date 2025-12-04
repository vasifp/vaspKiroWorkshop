"""
Events API - FastAPI REST Backend with User Registration.

This module provides the FastAPI application initialization, middleware configuration,
and Lambda handler. All endpoint definitions are in the routers package.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from routers import users, events, registrations

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


@app.get("/health")
def health():
    return {"status": "healthy"}


# Include routers
app.include_router(users.router)
app.include_router(events.router)
app.include_router(registrations.router)


handler = Mangum(app)

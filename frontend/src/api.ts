import { API_BASE_URL } from './config';
import { User, Event, EventCreate, Registration } from './types';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options?.headers },
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

// Users API
export const createUser = (userId: string, name: string) =>
  request<User>('/users', { method: 'POST', body: JSON.stringify({ userId, name }) });

export const getUser = (userId: string) => request<User>(`/users/${userId}`);

// Events API
export const listEvents = (status?: string) =>
  request<Event[]>(`/events${status ? `?status=${status}` : ''}`);

export const getEvent = (eventId: string) => request<Event>(`/events/${eventId}`);

export const createEvent = (event: EventCreate) =>
  request<Event>('/events', { method: 'POST', body: JSON.stringify(event) });

export const updateEvent = (eventId: string, event: Partial<EventCreate>) =>
  request<Event>(`/events/${eventId}`, { method: 'PUT', body: JSON.stringify(event) });

export const deleteEvent = (eventId: string) =>
  request<{ message: string }>(`/events/${eventId}`, { method: 'DELETE' });

// Registrations API
export const registerForEvent = (eventId: string, userId: string) =>
  request<Registration>(`/events/${eventId}/registrations`, {
    method: 'POST', body: JSON.stringify({ userId }),
  });

export const unregisterFromEvent = (eventId: string, userId: string) =>
  request<{ message: string }>(`/events/${eventId}/registrations/${userId}`, { method: 'DELETE' });

export const getUserRegistrations = (userId: string) =>
  request<Registration[]>(`/users/${userId}/registrations`);

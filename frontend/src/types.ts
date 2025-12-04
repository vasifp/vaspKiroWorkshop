export interface User {
  userId: string;
  name: string;
}

export interface Event {
  eventId: string;
  title: string;
  description?: string;
  date: string;
  location: string;
  capacity: number;
  organizer: string;
  status: 'draft' | 'published' | 'cancelled' | 'completed' | 'active';
  waitlistEnabled: boolean;
  registrationCount: number;
}

export interface EventCreate {
  eventId?: string;
  title: string;
  description?: string;
  date: string;
  location: string;
  capacity: number;
  organizer: string;
  status: string;
  waitlistEnabled: boolean;
}

export interface Registration {
  eventId: string;
  userId: string;
  registrationStatus: 'confirmed' | 'waitlisted';
  registeredAt: string;
  waitlistPosition?: number;
}

import { useState, useEffect } from 'react';
import AppLayout from '@cloudscape-design/components/app-layout';
import ContentLayout from '@cloudscape-design/components/content-layout';
import Header from '@cloudscape-design/components/header';
import SideNavigation from '@cloudscape-design/components/side-navigation';
import Tabs from '@cloudscape-design/components/tabs';
import Table from '@cloudscape-design/components/table';
import Button from '@cloudscape-design/components/button';
import Box from '@cloudscape-design/components/box';
import SpaceBetween from '@cloudscape-design/components/space-between';
import Modal from '@cloudscape-design/components/modal';
import FormField from '@cloudscape-design/components/form-field';
import Input from '@cloudscape-design/components/input';
import Textarea from '@cloudscape-design/components/textarea';
import Select from '@cloudscape-design/components/select';
import Checkbox from '@cloudscape-design/components/checkbox';
import DatePicker from '@cloudscape-design/components/date-picker';
import Alert from '@cloudscape-design/components/alert';
import Badge from '@cloudscape-design/components/badge';
import StatusIndicator from '@cloudscape-design/components/status-indicator';
import { Event, Registration, EventCreate } from './types';
import * as api from './api';

const STATUS_OPTIONS = [
  { value: 'draft', label: 'Draft' },
  { value: 'published', label: 'Published' },
  { value: 'active', label: 'Active' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
];

function App() {
  const [activeTab, setActiveTab] = useState('events');
  const [events, setEvents] = useState<Event[]>([]);
  const [selectedEvents, setSelectedEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Event Modal
  const [eventModalVisible, setEventModalVisible] = useState(false);
  const [editingEvent, setEditingEvent] = useState<Event | null>(null);
  const [eventForm, setEventForm] = useState<EventCreate>({
    title: '', description: '', date: '', location: '',
    capacity: 100, organizer: '', status: 'draft', waitlistEnabled: false,
  });

  // User Modal
  const [userModalVisible, setUserModalVisible] = useState(false);
  const [userForm, setUserForm] = useState({ userId: '', name: '' });

  // Registration Modal
  const [regModalVisible, setRegModalVisible] = useState(false);
  const [regEventId, setRegEventId] = useState('');
  const [regUserId, setRegUserId] = useState('');

  // User Registrations
  const [userRegUserId, setUserRegUserId] = useState('');
  const [userRegistrations, setUserRegistrations] = useState<Registration[]>([]);
  const [loadingRegs, setLoadingRegs] = useState(false);

  // Delete Confirmation
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);
  const [eventToDelete, setEventToDelete] = useState<Event | null>(null);

  useEffect(() => { loadEvents(); }, []);

  const loadEvents = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.listEvents();
      setEvents(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load events');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateEvent = () => {
    setEditingEvent(null);
    setEventForm({
      title: '', description: '', date: '', location: '',
      capacity: 100, organizer: '', status: 'draft', waitlistEnabled: false,
    });
    setEventModalVisible(true);
  };

  const handleEditEvent = (event: Event) => {
    setEditingEvent(event);
    setEventForm({
      title: event.title, description: event.description || '',
      date: event.date, location: event.location, capacity: event.capacity,
      organizer: event.organizer, status: event.status, waitlistEnabled: event.waitlistEnabled,
    });
    setEventModalVisible(true);
  };

  const handleSaveEvent = async () => {
    setError('');
    try {
      if (editingEvent) {
        await api.updateEvent(editingEvent.eventId, eventForm);
      } else {
        await api.createEvent(eventForm);
      }
      setEventModalVisible(false);
      loadEvents();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save event');
    }
  };

  const handleDeleteEvent = async () => {
    if (!eventToDelete) return;
    try {
      await api.deleteEvent(eventToDelete.eventId);
      setDeleteModalVisible(false);
      setEventToDelete(null);
      loadEvents();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to delete event');
    }
  };

  const handleCreateUser = async () => {
    setError('');
    try {
      await api.createUser(userForm.userId, userForm.name);
      setUserModalVisible(false);
      setUserForm({ userId: '', name: '' });
      setError('');
      alert('User created successfully!');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to create user');
    }
  };

  const handleRegister = async () => {
    setError('');
    try {
      await api.registerForEvent(regEventId, regUserId);
      setRegModalVisible(false);
      setRegEventId('');
      setRegUserId('');
      loadEvents();
      alert('Registration successful!');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to register');
    }
  };

  const handleUnregister = async (eventId: string, userId: string) => {
    try {
      await api.unregisterFromEvent(eventId, userId);
      loadUserRegistrations(userRegUserId);
      loadEvents();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to unregister');
    }
  };

  const loadUserRegistrations = async (userId: string) => {
    setLoadingRegs(true);
    try {
      const regs = await api.getUserRegistrations(userId);
      setUserRegistrations(regs);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load registrations');
    } finally {
      setLoadingRegs(false);
    }
  };

  const handleViewUserRegs = () => {
    if (userRegUserId) {
      loadUserRegistrations(userRegUserId);
    }
  };

  const getStatusIndicator = (status: string) => {
    const map: Record<string, 'success' | 'warning' | 'error' | 'info' | 'stopped'> = {
      active: 'success', published: 'info', draft: 'warning',
      completed: 'stopped', cancelled: 'error',
    };
    return <StatusIndicator type={map[status] || 'info'}>{status}</StatusIndicator>;
  };

  return (
    <AppLayout
      navigation={
        <SideNavigation
          header={{ text: 'Events Manager', href: '#' }}
          items={[
            { type: 'link', text: 'Events', href: '#events' },
            { type: 'link', text: 'Users', href: '#users' },
            { type: 'link', text: 'Registrations', href: '#registrations' },
          ]}
        />
      }
      content={
        <ContentLayout header={<Header variant="h1">Events Management System</Header>}>
          <SpaceBetween size="l">
            {error && <Alert type="error" dismissible onDismiss={() => setError('')}>{error}</Alert>}

            <Tabs
              activeTabId={activeTab}
              onChange={({ detail }) => setActiveTab(detail.activeTabId)}
              tabs={[
                {
                  id: 'events',
                  label: 'Events',
                  content: (
                    <Table
                      loading={loading}
                      items={events}
                      trackBy="eventId"
                      selectionType="single"
                      selectedItems={selectedEvents}
                      onSelectionChange={({ detail }) => setSelectedEvents(detail.selectedItems)}
                      header={
                        <Header
                          counter={`(${events.length})`}
                          actions={
                            <SpaceBetween direction="horizontal" size="xs">
                              <Button onClick={loadEvents} iconName="refresh">Refresh</Button>
                              <Button variant="primary" onClick={handleCreateEvent}>Create Event</Button>
                            </SpaceBetween>
                          }
                        >
                          Events
                        </Header>
                      }
                      columnDefinitions={[
                        { id: 'eventId', header: 'Event ID', cell: (e) => e.eventId, sortingField: 'eventId' },
                        { id: 'title', header: 'Title', cell: (e) => e.title, sortingField: 'title' },
                        { id: 'date', header: 'Date', cell: (e) => e.date, sortingField: 'date' },
                        { id: 'location', header: 'Location', cell: (e) => e.location },
                        { id: 'capacity', header: 'Capacity', cell: (e) => `${e.registrationCount}/${e.capacity}` },
                        { id: 'status', header: 'Status', cell: (e) => getStatusIndicator(e.status) },
                        { id: 'waitlist', header: 'Waitlist', cell: (e) => e.waitlistEnabled ? <Badge color="blue">Enabled</Badge> : '-' },
                        {
                          id: 'actions',
                          header: 'Actions',
                          cell: (e) => (
                            <SpaceBetween direction="horizontal" size="xs">
                              <Button variant="inline-link" onClick={() => handleEditEvent(e)}>Edit</Button>
                              <Button variant="inline-link" onClick={() => { setEventToDelete(e); setDeleteModalVisible(true); }}>Delete</Button>
                            </SpaceBetween>
                          ),
                        },
                      ]}
                      empty={
                        <Box textAlign="center" color="inherit">
                          <b>No events</b>
                          <Box padding={{ bottom: 's' }} variant="p" color="inherit">No events to display.</Box>
                          <Button onClick={handleCreateEvent}>Create event</Button>
                        </Box>
                      }
                    />
                  ),
                },
                {
                  id: 'users',
                  label: 'Users',
                  content: (
                    <SpaceBetween size="l">
                      <Header actions={<Button variant="primary" onClick={() => setUserModalVisible(true)}>Create User</Button>}>
                        User Management
                      </Header>
                      <Box>Create users to register them for events.</Box>
                    </SpaceBetween>
                  ),
                },
                {
                  id: 'registrations',
                  label: 'Registrations',
                  content: (
                    <SpaceBetween size="l">
                      <Header
                        actions={
                          <SpaceBetween direction="horizontal" size="xs">
                            <Button variant="primary" onClick={() => setRegModalVisible(true)}>Register User</Button>
                          </SpaceBetween>
                        }
                      >
                        Registration Management
                      </Header>
                      <Box variant="h3">View User Registrations</Box>
                      <SpaceBetween direction="horizontal" size="xs">
                        <FormField label="User ID">
                          <Input value={userRegUserId} onChange={({ detail }) => setUserRegUserId(detail.value)} placeholder="Enter user ID" />
                        </FormField>
                        <Box padding={{ top: 'l' }}>
                          <Button onClick={handleViewUserRegs} disabled={!userRegUserId}>View Registrations</Button>
                        </Box>
                      </SpaceBetween>
                      {userRegistrations.length > 0 && (
                        <Table
                          loading={loadingRegs}
                          items={userRegistrations}
                          trackBy="eventId"
                          columnDefinitions={[
                            { id: 'eventId', header: 'Event ID', cell: (r) => r.eventId },
                            { id: 'status', header: 'Status', cell: (r) => <Badge color={r.registrationStatus === 'confirmed' ? 'green' : 'blue'}>{r.registrationStatus}</Badge> },
                            { id: 'waitlistPos', header: 'Waitlist Position', cell: (r) => r.waitlistPosition ?? '-' },
                            { id: 'registeredAt', header: 'Registered At', cell: (r) => r.registeredAt },
                            {
                              id: 'actions',
                              header: 'Actions',
                              cell: (r) => <Button variant="inline-link" onClick={() => handleUnregister(r.eventId, r.userId)}>Unregister</Button>,
                            },
                          ]}
                          header={<Header counter={`(${userRegistrations.length})`}>Registrations for {userRegUserId}</Header>}
                        />
                      )}
                    </SpaceBetween>
                  ),
                },
              ]}
            />
          </SpaceBetween>


          {/* Event Create/Edit Modal */}
          <Modal
            visible={eventModalVisible}
            onDismiss={() => setEventModalVisible(false)}
            header={editingEvent ? 'Edit Event' : 'Create Event'}
            size="large"
            footer={
              <Box float="right">
                <SpaceBetween direction="horizontal" size="xs">
                  <Button variant="link" onClick={() => setEventModalVisible(false)}>Cancel</Button>
                  <Button variant="primary" onClick={handleSaveEvent}>Save</Button>
                </SpaceBetween>
              </Box>
            }
          >
            <SpaceBetween size="l">
              <FormField label="Title">
                <Input value={eventForm.title} onChange={({ detail }) => setEventForm({ ...eventForm, title: detail.value })} />
              </FormField>
              <FormField label="Description">
                <Textarea value={eventForm.description || ''} onChange={({ detail }) => setEventForm({ ...eventForm, description: detail.value })} />
              </FormField>
              <FormField label="Date">
                <DatePicker value={eventForm.date} onChange={({ detail }) => setEventForm({ ...eventForm, date: detail.value })} placeholder="YYYY-MM-DD" />
              </FormField>
              <FormField label="Location">
                <Input value={eventForm.location} onChange={({ detail }) => setEventForm({ ...eventForm, location: detail.value })} />
              </FormField>
              <FormField label="Capacity">
                <Input type="number" value={String(eventForm.capacity)} onChange={({ detail }) => setEventForm({ ...eventForm, capacity: parseInt(detail.value) || 0 })} />
              </FormField>
              <FormField label="Organizer">
                <Input value={eventForm.organizer} onChange={({ detail }) => setEventForm({ ...eventForm, organizer: detail.value })} />
              </FormField>
              <FormField label="Status">
                <Select
                  selectedOption={STATUS_OPTIONS.find((o) => o.value === eventForm.status) || null}
                  onChange={({ detail }) => setEventForm({ ...eventForm, status: detail.selectedOption.value || 'draft' })}
                  options={STATUS_OPTIONS}
                />
              </FormField>
              <Checkbox checked={eventForm.waitlistEnabled} onChange={({ detail }) => setEventForm({ ...eventForm, waitlistEnabled: detail.checked })}>
                Enable Waitlist
              </Checkbox>
            </SpaceBetween>
          </Modal>

          {/* Delete Confirmation Modal */}
          <Modal
            visible={deleteModalVisible}
            onDismiss={() => setDeleteModalVisible(false)}
            header="Delete Event"
            footer={
              <Box float="right">
                <SpaceBetween direction="horizontal" size="xs">
                  <Button variant="link" onClick={() => setDeleteModalVisible(false)}>Cancel</Button>
                  <Button variant="primary" onClick={handleDeleteEvent}>Delete</Button>
                </SpaceBetween>
              </Box>
            }
          >
            <Box>Are you sure you want to delete "{eventToDelete?.title}"? This action cannot be undone.</Box>
          </Modal>

          {/* Create User Modal */}
          <Modal
            visible={userModalVisible}
            onDismiss={() => setUserModalVisible(false)}
            header="Create User"
            footer={
              <Box float="right">
                <SpaceBetween direction="horizontal" size="xs">
                  <Button variant="link" onClick={() => setUserModalVisible(false)}>Cancel</Button>
                  <Button variant="primary" onClick={handleCreateUser}>Create</Button>
                </SpaceBetween>
              </Box>
            }
          >
            <SpaceBetween size="l">
              <FormField label="User ID">
                <Input value={userForm.userId} onChange={({ detail }) => setUserForm({ ...userForm, userId: detail.value })} placeholder="e.g., user123" />
              </FormField>
              <FormField label="Name">
                <Input value={userForm.name} onChange={({ detail }) => setUserForm({ ...userForm, name: detail.value })} placeholder="e.g., John Doe" />
              </FormField>
            </SpaceBetween>
          </Modal>

          {/* Register User Modal */}
          <Modal
            visible={regModalVisible}
            onDismiss={() => setRegModalVisible(false)}
            header="Register User for Event"
            footer={
              <Box float="right">
                <SpaceBetween direction="horizontal" size="xs">
                  <Button variant="link" onClick={() => setRegModalVisible(false)}>Cancel</Button>
                  <Button variant="primary" onClick={handleRegister}>Register</Button>
                </SpaceBetween>
              </Box>
            }
          >
            <SpaceBetween size="l">
              <FormField label="Event ID">
                <Input value={regEventId} onChange={({ detail }) => setRegEventId(detail.value)} placeholder="e.g., event-123" />
              </FormField>
              <FormField label="User ID">
                <Input value={regUserId} onChange={({ detail }) => setRegUserId(detail.value)} placeholder="e.g., user123" />
              </FormField>
            </SpaceBetween>
          </Modal>
        </ContentLayout>
      }
      toolsHide={true}
    />
  );
}

export default App;

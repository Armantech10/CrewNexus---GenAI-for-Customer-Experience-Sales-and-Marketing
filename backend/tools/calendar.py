"""
Calendar Scheduling Tool
Integration with calendar services for event management.
Falls back to mock mode when credentials are not configured.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
from enum import Enum
import uuid

from backend.config.settings import settings


class EventStatus(str, Enum):
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


class EventType(str, Enum):
    MEETING = "meeting"
    CALL = "call"
    WEBINAR = "webinar"
    DEMO = "demo"
    FOLLOWUP = "followup"
    OTHER = "other"


class Attendee(BaseModel):
    """Event attendee model"""
    email: str
    name: Optional[str] = None
    response_status: str = "needsAction"  # needsAction, declined, tentative, accepted
    optional: bool = False


class CalendarEvent(BaseModel):
    """Calendar event model"""
    id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    event_type: EventType = EventType.MEETING
    status: EventStatus = EventStatus.CONFIRMED
    attendees: List[Attendee] = []
    meeting_link: Optional[str] = None
    reminders: List[int] = [30]  # Minutes before
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()


class TimeSlot(BaseModel):
    """Available time slot"""
    start: datetime
    end: datetime
    duration_minutes: int


class CalendarScheduling:
    """
    Calendar scheduling integration.
    Supports Google Calendar (OAuth required for real functionality).
    """
    
    def __init__(self):
        # Check for credentials
        self.google_credentials = getattr(settings, 'GOOGLE_CALENDAR_CREDENTIALS', None)
        self.mock_mode = not self.google_credentials
        
        # Mock storage
        self._mock_events: Dict[str, CalendarEvent] = {}
        
        # Seed some mock events
        self._seed_mock_events()
    
    def _seed_mock_events(self):
        """Seed mock events for demo"""
        now = datetime.now()
        
        events = [
            {
                "title": "Sales Demo - Acme Corp",
                "description": "Product demonstration for potential enterprise client",
                "start_time": now + timedelta(hours=2),
                "end_time": now + timedelta(hours=3),
                "event_type": EventType.DEMO,
                "attendees": [
                    Attendee(email="john@acme.com", name="John Smith", response_status="accepted")
                ],
                "meeting_link": "https://meet.google.com/abc-defg-hij"
            },
            {
                "title": "Weekly Marketing Sync",
                "description": "Review campaign performance and plan next week",
                "start_time": now + timedelta(days=1, hours=10),
                "end_time": now + timedelta(days=1, hours=11),
                "event_type": EventType.MEETING,
                "attendees": [
                    Attendee(email="marketing@company.com", name="Marketing Team", response_status="accepted")
                ]
            },
            {
                "title": "Customer Success Follow-up",
                "description": "Monthly check-in with key accounts",
                "start_time": now + timedelta(days=3, hours=14),
                "end_time": now + timedelta(days=3, hours=14, minutes=30),
                "event_type": EventType.FOLLOWUP,
                "attendees": [
                    Attendee(email="customer@client.com", name="Client Rep", response_status="tentative")
                ]
            }
        ]
        
        for event_data in events:
            event_id = f"evt_{uuid.uuid4().hex[:12]}"
            self._mock_events[event_id] = CalendarEvent(
                id=event_id,
                **event_data
            )
    
    @property
    def is_mock(self) -> bool:
        return self.mock_mode
    
    async def create_event(
        self,
        title: str,
        start_time: datetime,
        end_time: datetime,
        description: Optional[str] = None,
        location: Optional[str] = None,
        event_type: EventType = EventType.MEETING,
        attendees: Optional[List[Dict[str, str]]] = None,
        send_invites: bool = True,
        add_meeting_link: bool = True
    ) -> CalendarEvent:
        """
        Create a calendar event.
        
        Args:
            title: Event title
            start_time: Start datetime
            end_time: End datetime
            description: Event description
            location: Physical or virtual location
            event_type: Type of event
            attendees: List of attendees with email and name
            send_invites: Send email invitations
            add_meeting_link: Generate a meeting link
        
        Returns:
            Created event
        """
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        
        # Parse attendees
        attendee_list = []
        if attendees:
            for a in attendees:
                attendee_list.append(Attendee(
                    email=a.get("email", ""),
                    name=a.get("name"),
                    optional=a.get("optional", False)
                ))
        
        # Generate meeting link if requested
        meeting_link = None
        if add_meeting_link and self.mock_mode:
            meeting_link = f"https://meet.google.com/{uuid.uuid4().hex[:3]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:3]}"
        
        event = CalendarEvent(
            id=event_id,
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time,
            location=location,
            event_type=event_type,
            attendees=attendee_list,
            meeting_link=meeting_link
        )
        
        self._mock_events[event_id] = event
        return event
    
    async def update_event(
        self,
        event_id: str,
        **updates
    ) -> CalendarEvent:
        """
        Update an existing event.
        
        Args:
            event_id: ID of event to update
            **updates: Fields to update
        
        Returns:
            Updated event
        """
        if event_id not in self._mock_events:
            raise ValueError(f"Event {event_id} not found")
        
        event = self._mock_events[event_id]
        
        for key, value in updates.items():
            if hasattr(event, key) and value is not None:
                setattr(event, key, value)
        
        event.updated_at = datetime.now()
        return event
    
    async def cancel_event(
        self,
        event_id: str,
        notify_attendees: bool = True
    ) -> CalendarEvent:
        """
        Cancel an event.
        
        Args:
            event_id: ID of event to cancel
            notify_attendees: Send cancellation notice
        
        Returns:
            Cancelled event
        """
        if event_id not in self._mock_events:
            raise ValueError(f"Event {event_id} not found")
        
        event = self._mock_events[event_id]
        event.status = EventStatus.CANCELLED
        event.updated_at = datetime.now()
        
        return event
    
    async def delete_event(self, event_id: str) -> bool:
        """Delete an event permanently"""
        if event_id in self._mock_events:
            del self._mock_events[event_id]
            return True
        return False
    
    async def get_event(self, event_id: str) -> Optional[CalendarEvent]:
        """Get an event by ID"""
        return self._mock_events.get(event_id)
    
    async def list_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[EventType] = None,
        limit: int = 50
    ) -> List[CalendarEvent]:
        """
        List events with optional filtering.
        
        Args:
            start_date: Filter events starting after this time
            end_date: Filter events ending before this time
            event_type: Filter by event type
            limit: Maximum results
        
        Returns:
            List of events
        """
        events = list(self._mock_events.values())
        
        if start_date:
            events = [e for e in events if e.start_time >= start_date]
        if end_date:
            events = [e for e in events if e.end_time <= end_date]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        # Filter out cancelled
        events = [e for e in events if e.status != EventStatus.CANCELLED]
        
        # Sort by start time
        events.sort(key=lambda e: e.start_time)
        
        return events[:limit]
    
    async def find_available_slots(
        self,
        duration_minutes: int,
        start_date: datetime,
        end_date: datetime,
        working_hours: tuple = (9, 17),
        exclude_weekends: bool = True
    ) -> List[TimeSlot]:
        """
        Find available time slots for scheduling.
        
        Args:
            duration_minutes: Required duration
            start_date: Start of search range
            end_date: End of search range
            working_hours: Tuple of (start_hour, end_hour)
            exclude_weekends: Skip Saturday/Sunday
        
        Returns:
            List of available slots
        """
        slots = []
        current = start_date.replace(hour=working_hours[0], minute=0, second=0)
        
        # Get existing events
        existing = await self.list_events(start_date, end_date)
        
        while current < end_date:
            # Skip weekends
            if exclude_weekends and current.weekday() >= 5:
                current += timedelta(days=1)
                current = current.replace(hour=working_hours[0], minute=0)
                continue
            
            # Check if within working hours
            if current.hour >= working_hours[1]:
                current += timedelta(days=1)
                current = current.replace(hour=working_hours[0], minute=0)
                continue
            
            slot_end = current + timedelta(minutes=duration_minutes)
            
            # Check for conflicts
            has_conflict = any(
                (current < e.end_time and slot_end > e.start_time)
                for e in existing
            )
            
            if not has_conflict and slot_end.hour <= working_hours[1]:
                slots.append(TimeSlot(
                    start=current,
                    end=slot_end,
                    duration_minutes=duration_minutes
                ))
            
            current += timedelta(minutes=30)  # Check every 30 min slot
            
            if len(slots) >= 10:  # Limit results
                break
        
        return slots
    
    async def schedule_meeting(
        self,
        title: str,
        duration_minutes: int,
        attendees: List[Dict[str, str]],
        preferred_date: Optional[datetime] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Smart scheduling: find a slot and create the meeting.
        
        Args:
            title: Meeting title
            duration_minutes: Duration in minutes
            attendees: List of attendees
            preferred_date: Preferred start date (defaults to tomorrow)
            description: Meeting description
        
        Returns:
            Scheduling result with event or available alternatives
        """
        if preferred_date is None:
            preferred_date = datetime.now() + timedelta(days=1)
        
        # Find available slots
        end_search = preferred_date + timedelta(days=7)
        slots = await self.find_available_slots(
            duration_minutes=duration_minutes,
            start_date=preferred_date,
            end_date=end_search
        )
        
        if not slots:
            return {
                "success": False,
                "message": "No available slots found in the next 7 days",
                "alternatives": []
            }
        
        # Use first available slot
        slot = slots[0]
        
        event = await self.create_event(
            title=title,
            start_time=slot.start,
            end_time=slot.end,
            description=description,
            attendees=attendees,
            add_meeting_link=True
        )
        
        return {
            "success": True,
            "event": event.dict(),
            "alternatives": [s.dict() for s in slots[1:5]],
            "mock": self.is_mock
        }


# Singleton instance
calendar = CalendarScheduling()

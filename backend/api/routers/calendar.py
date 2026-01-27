"""
Calendar Router
API endpoints for calendar scheduling and event management.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

from backend.tools.calendar import calendar, EventType, EventStatus

router = APIRouter()


class CreateEventRequest(BaseModel):
    title: str
    start_time: datetime
    end_time: datetime
    description: Optional[str] = None
    location: Optional[str] = None
    event_type: EventType = EventType.MEETING
    attendees: Optional[List[Dict[str, str]]] = None
    add_meeting_link: bool = True


class UpdateEventRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None


class ScheduleMeetingRequest(BaseModel):
    title: str
    duration_minutes: int
    attendees: List[Dict[str, str]]
    preferred_date: Optional[datetime] = None
    description: Optional[str] = None


class FindSlotsRequest(BaseModel):
    duration_minutes: int
    start_date: datetime
    end_date: datetime
    working_hours: tuple = (9, 17)
    exclude_weekends: bool = True


@router.get("/mode")
async def get_calendar_mode():
    """Check if calendar is in mock or live mode"""
    return {
        "mock_mode": calendar.is_mock,
        "message": "Mock mode - simulated calendar" if calendar.is_mock else "Live Google Calendar"
    }


@router.post("/events")
async def create_event(request: CreateEventRequest):
    """Create a new calendar event"""
    event = await calendar.create_event(
        title=request.title,
        start_time=request.start_time,
        end_time=request.end_time,
        description=request.description,
        location=request.location,
        event_type=request.event_type,
        attendees=request.attendees,
        add_meeting_link=request.add_meeting_link
    )
    return {**event.dict(), "mock": calendar.is_mock}


@router.get("/events")
async def list_events(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    event_type: Optional[EventType] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """List calendar events with optional filtering"""
    events = await calendar.list_events(
        start_date=start_date,
        end_date=end_date,
        event_type=event_type,
        limit=limit
    )
    return {
        "events": [e.dict() for e in events],
        "total": len(events),
        "mock": calendar.is_mock
    }


@router.get("/events/{event_id}")
async def get_event(event_id: str):
    """Get a specific event by ID"""
    event = await calendar.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {**event.dict(), "mock": calendar.is_mock}


@router.put("/events/{event_id}")
async def update_event(event_id: str, request: UpdateEventRequest):
    """Update an existing event"""
    try:
        event = await calendar.update_event(
            event_id=event_id,
            **request.dict(exclude_none=True)
        )
        return {**event.dict(), "mock": calendar.is_mock}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/events/{event_id}/cancel")
async def cancel_event(event_id: str, notify_attendees: bool = True):
    """Cancel an event (marks as cancelled, doesn't delete)"""
    try:
        event = await calendar.cancel_event(event_id, notify_attendees)
        return {**event.dict(), "mock": calendar.is_mock}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """Permanently delete an event"""
    deleted = await calendar.delete_event(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"deleted": True, "event_id": event_id}


@router.post("/find-slots")
async def find_available_slots(request: FindSlotsRequest):
    """Find available time slots for scheduling"""
    slots = await calendar.find_available_slots(
        duration_minutes=request.duration_minutes,
        start_date=request.start_date,
        end_date=request.end_date,
        working_hours=request.working_hours,
        exclude_weekends=request.exclude_weekends
    )
    return {
        "slots": [s.dict() for s in slots],
        "total": len(slots),
        "mock": calendar.is_mock
    }


@router.post("/schedule")
async def schedule_meeting(request: ScheduleMeetingRequest):
    """
    Smart scheduling: automatically find a slot and create the meeting.
    """
    result = await calendar.schedule_meeting(
        title=request.title,
        duration_minutes=request.duration_minutes,
        attendees=request.attendees,
        preferred_date=request.preferred_date,
        description=request.description
    )
    return result

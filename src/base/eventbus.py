from uuid import UUID, uuid4

from pydantic import BaseModel, PrivateAttr, Field


class Event(BaseModel):
    uuid: UUID = Field(default_factory=uuid4)


class EventStore(BaseModel):
    _events: list[Event] = PrivateAttr(default_factory=list)

    def push_event(self, event: Event):
        self._events.append(event)

    def parse_events(self) -> list[Event]:
        events = self._events
        self._events = []
        return events

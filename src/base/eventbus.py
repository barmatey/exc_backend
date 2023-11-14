from collections import deque
from typing import Generic, TypeVar, Callable, Sequence, Optional
from uuid import UUID, uuid4

from loguru import logger
from pydantic import BaseModel, Field

T = TypeVar("T")


class Event(BaseModel):
    key: str
    id: UUID = Field(default_factory=uuid4)


class Created(Event, Generic[T]):
    entity: T


class Updated(Event, Generic[T]):
    entity: T


class Deleted(Event, Generic[T]):
    entity: T


class EventStore:
    def __init__(self):
        self._events = []
        self._uniques = {}

    def push_unique_event(self, key: str, event: Event):
        self._uniques[key] = event

    def push_event(self, event: Event):
        self._events.append(event)

    def parse_events(self) -> list[Event]:
        events = self._events
        events.extend(self._uniques.values())
        self._events = []
        self._uniques = {}
        return events


class Queue:
    def __init__(self):
        self._queue: deque = deque()

    def append(self, event: Event):
        # logger.debug(f"APPEND: {event.key}")
        self._queue.append(event)

    def popleft(self) -> Event:
        event = self._queue.popleft()
        logger.debug(f"EXTRACT: {event.key}")
        return event

    def extend(self, events: Sequence[Event]):
        for x in events:
            self.append(x)

    @property
    def empty(self):
        return len(self._queue) == 0


class EventBus:
    def __init__(self, queue: Queue):
        self._queue = queue
        self._handlers: dict[str, Callable] = {}

    def register(self, key: str, handler: Callable):
        self._handlers[key] = handler

    def extend_events(self, events: list[Event]):
        self._queue.extend(events)

    async def run(self):
        while not self._queue.empty:
            event = self._queue.popleft()
            handler = self._handlers[event.key]
            await handler(event)

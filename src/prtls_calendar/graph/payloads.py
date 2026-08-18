"""Typed calendar node payloads."""

from __future__ import annotations

from enum import StrEnum

from pydantic import AwareDatetime, ConfigDict, Field, field_validator, model_validator
from prtls_graph import NodePayload


class _DomainPayload(NodePayload):
    model_config = ConfigDict(frozen=True, extra="forbid")


class CalendarEventType(StrEnum):
    HOLIDAY = "holiday"
    RELIGIOUS = "religious"
    MERCHANDISING = "merchandising"
    PROMOTION = "promotion"
    CULTURAL = "cultural"
    OTHER = "other"


class DateSource(StrEnum):
    MANUAL = "manual"
    IMPORTED = "imported"
    COMPUTED = "computed"
    EXTERNAL = "external"


class CalendarPayload(_DomainPayload):
    """A named calendar and its date interpretation settings."""

    name: str = Field(min_length=1, max_length=255)
    timezone: str = Field(default="UTC", min_length=1, max_length=128)
    locale: str = Field(default="", max_length=32)
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("name", "timezone", "locale")
    @classmethod
    def _strip_text(cls, value: str) -> str:
        return value.strip()


class CalendarEventPayload(_DomainPayload):
    """One occasion in a calendar."""

    name: str = Field(min_length=1, max_length=255)
    event_type: CalendarEventType = CalendarEventType.OTHER
    date_source: DateSource = DateSource.MANUAL
    description: str = ""
    starts_at: AwareDatetime | None = None
    ends_at: AwareDatetime | None = None
    all_day: bool = True
    is_active: bool = True
    metadata: dict[str, object] = Field(default_factory=dict)

    @field_validator("name", "description")
    @classmethod
    def _strip_text(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def _validate_range(self) -> "CalendarEventPayload":
        if self.starts_at is not None and self.ends_at is not None and self.ends_at < self.starts_at:
            raise ValueError("ends_at must be greater than or equal to starts_at")
        if self.all_day:
            for value in (self.starts_at, self.ends_at):
                if value is not None and (value.hour, value.minute, value.second, value.microsecond) != (0, 0, 0, 0):
                    raise ValueError("all-day event timestamps must be midnight")
        return self

    def embedding_text(self) -> str:
        return " ".join(part for part in (self.name, self.description) if part).strip()

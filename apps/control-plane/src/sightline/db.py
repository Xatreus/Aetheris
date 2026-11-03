import json
import os
from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sightline.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class EventRecord(Base):
    __tablename__ = "reliability_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    service: Mapped[str] = mapped_column(String(120), index=True)
    environment: Mapped[str] = mapped_column(String(40))
    version: Mapped[str] = mapped_column(String(80), index=True)
    event_type: Mapped[str] = mapped_column(String(30), index=True)
    trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payload_json: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[object] = mapped_column(DateTime(timezone=True))


def init_db():
    Base.metadata.create_all(bind=engine)


def save_event(event) -> int:
    payload = event.model_dump(mode="json")
    with SessionLocal() as session:
        row = EventRecord(
            service=event.service,
            environment=event.environment,
            version=event.version,
            event_type=event.event_type,
            trace_id=event.trace_id,
            payload_json=json.dumps(payload),
            occurred_at=event.occurred_at or datetime.now(UTC),
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        return row.id

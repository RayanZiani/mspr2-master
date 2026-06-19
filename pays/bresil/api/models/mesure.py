"""Modèle SQLAlchemy pour les mesures capteurs — Brésil."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, String

from api.db.database import Base


class Mesure(Base):
    """Mesure de température et humidité pour un lot."""
    __tablename__ = "mesures"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lot_id = Column(String(36), ForeignKey("lots.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)

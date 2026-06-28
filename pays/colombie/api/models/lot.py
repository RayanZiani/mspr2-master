"""Modèle SQLAlchemy pour les lots — Colombie."""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, String

from api.db.database import Base


class Lot(Base):
    """Lot de café stocké en entrepôt."""
    __tablename__ = "lots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pays = Column(String(50), nullable=False)
    exploitation = Column(String(100), nullable=False)
    entrepot = Column(String(100), nullable=False)
    date_stockage = Column(DateTime, nullable=False, default=datetime.utcnow)
    statut = Column(
        Enum("conforme", "alerte", "perime"),
        nullable=False,
        default="conforme",
    )

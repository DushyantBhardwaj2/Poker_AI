import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base, is_sqlite

class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32), storing as string without hyphens.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if not isinstance(value, uuid.UUID):
            return uuid.UUID(value)
        else:
            return value

def generate_uuid():
    return uuid.uuid4()

def default_dynamic_features():
    return {
        "vpip_count": 0,
        "pfr_count": 0,
        "aggression_ip": 0.0,
        "aggression_oop": 0.0,
        "strict_bluff_showdowns": 0
    }

class User(Base):
    __tablename__ = "users"

    user_id = Column(GUID(), primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    poker_experience = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    opponents = relationship("Opponent", back_populates="user")

class Opponent(Base):
    __tablename__ = "opponents"

    opponent_id = Column(GUID(), primary_key=True, default=generate_uuid)
    user_id = Column(GUID(), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    player_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="opponents")
    stats = relationship("OpponentStats", back_populates="opponent", uselist=False)

class OpponentStats(Base):
    __tablename__ = "opponent_stats"

    opponent_id = Column(GUID(), ForeignKey("opponents.opponent_id", ondelete="CASCADE"), primary_key=True)
    hands_played = Column(Integer, default=0)
    
    # Use JSONB for Postgres, JSON for others
    dynamic_features = Column(
        JSONB if not is_sqlite else JSON, 
        default=default_dynamic_features
    )
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    opponent = relationship("Opponent", back_populates="stats")


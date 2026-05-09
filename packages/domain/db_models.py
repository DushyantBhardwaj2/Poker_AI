import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, TypeDecorator, CHAR, Float, Text, Boolean
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
        "strict_bluff_showdowns": 0,
        # Phase 3 additional stats
        "cbet_count": 0,
        "cbet_success": 0,
        "three_bet_count": 0,
        "three_bet_success": 0,
        "fold_to_river_bet": 0,
        "calls_showdown": 0,
        "wins_at_showdown": 0,
        "total_bets": 0,
        "total_calls": 0,
    }

def default_session_features():
    """Tracks session-only stats for session vs baseline analysis"""
    return {
        "hands_played": 0,
        "vpip_count": 0,
        "pfr_count": 0,
        "session_bets": 0.0,
        "session_calls": 0.0,
        "cbet_count": 0,
        "three_bet_count": 0,
        "recent_history": []
    }

class User(Base):
    __tablename__ = "users"

    user_id = Column(GUID(), primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    poker_experience = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    opponents = relationship("Opponent", back_populates="user")
    sessions = relationship("GameSession", back_populates="user")

class Opponent(Base):
    __tablename__ = "opponents"

    opponent_id = Column(GUID(), primary_key=True, default=generate_uuid)
    user_id = Column(GUID(), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    player_name = Column(String, nullable=False)
    notes = Column(Text, default="")  # User notes about opponent
    playstyle_archetype = Column(String, default="Unknown")  # TAG, LAG, Rock, etc.
    last_seen = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="opponents")
    stats = relationship("OpponentStats", back_populates="opponent", uselist=False)

class OpponentStats(Base):
    __tablename__ = "opponent_stats"

    opponent_id = Column(GUID(), ForeignKey("opponents.opponent_id", ondelete="CASCADE"), primary_key=True)
    hands_played = Column(Integer, default=0)
    last_hand_timestamp = Column(DateTime(timezone=True), nullable=True)

    # Human-readable behavioral description (e.g., "Likes to bluff", "Hand-focused player")
    behavioral_description = Column(String, default="Unknown")

    # Use JSONB for Postgres, JSON for others
    dynamic_features = Column(
        JSONB if not is_sqlite else JSON,
        default=default_dynamic_features
    )

    # Session vs baseline tracking
    session_features = Column(
        JSONB if not is_sqlite else JSON,
        default=default_session_features
    )

    # Reliability score based on sample size
    reliability_score = Column(String, default="Low")  # Low, Medium, High

    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    opponent = relationship("Opponent", back_populates="stats")


class GameSession(Base):
    """Tracks individual game sessions for session-vs-baseline analysis"""
    __tablename__ = "game_sessions"

    session_id = Column(GUID(), primary_key=True, default=generate_uuid)
    user_id = Column(GUID(), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    session_name = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    total_hands = Column(Integer, default=0)
    total_winnings = Column(Float, default=0.0)

    user = relationship("User", back_populates="sessions")
    opponents = relationship("SessionOpponent", back_populates="session")
    hands = relationship("HandHistory", back_populates="session")


class HandHistory(Base):
    """Tracks individual hand results for session analytics"""
    __tablename__ = "hand_history"

    hand_id = Column(GUID(), primary_key=True, default=generate_uuid)
    session_id = Column(GUID(), ForeignKey("game_sessions.session_id", ondelete="CASCADE"), nullable=False)
    street = Column(String, nullable=False)  # pre-flop, flop, turn, river, showdown
    pot_size = Column(Float, default=0.0)
    your_cards = Column(JSON, nullable=True)
    community_cards = Column(JSON, nullable=True)
    result = Column(String, nullable=True)  # win, loss, tie
    amount_won = Column(Float, default=0.0)
    action_count = Column(Integer, default=0)
    duration_seconds = Column(Integer, default=0)
    
    # Advanced Analytics & Leak Detection
    tactical_data = Column(JSONB if not is_sqlite else JSON, nullable=True)
    leak_detected = Column(Boolean, default=False)
    leak_description = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("GameSession", back_populates="hands")


class SessionOpponent(Base):
    """Tracks opponent stats within a specific session"""
    __tablename__ = "session_opponents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(GUID(), ForeignKey("game_sessions.session_id", ondelete="CASCADE"), nullable=False)
    opponent_id = Column(GUID(), ForeignKey("opponents.opponent_id", ondelete="CASCADE"), nullable=False)

    hands_played = Column(Integer, default=0)
    vpip_count = Column(Integer, default=0)
    pfr_count = Column(Integer, default=0)
    aggression_total = Column(Float, default=0.0)
    total_won = Column(Float, default=0.0)

    session = relationship("GameSession", back_populates="opponents")
    opponent = relationship("Opponent")

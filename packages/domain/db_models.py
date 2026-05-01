from sqlalchemy import Column, Integer, String, Float
from .database import Base

class DBPlayerStat(Base):
    __tablename__ = "player_stats"

    name = Column(String, primary_key=True, index=True)
    total_hands = Column(Integer, default=0)
    vpip_hands = Column(Integer, default=0)
    pfr_hands = Column(Integer, default=0)

from typing import Optional, Dict
from sqlalchemy.orm import Session
from .db_models import DBPlayerStat

class StatsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_player_stats(self, name: str) -> Optional[DBPlayerStat]:
        return self.db.query(DBPlayerStat).filter(DBPlayerStat.name == name).first()

    def update_player_stats(self, name: str, vpip_this_hand: bool, pfr_this_hand: bool):
        stat = self.get_player_stats(name)
        if not stat:
            stat = DBPlayerStat(name=name, total_hands=0, vpip_hands=0, pfr_hands=0)
            self.db.add(stat)
        
        stat.total_hands += 1
        if vpip_this_hand:
            stat.vpip_hands += 1
        if pfr_this_hand:
            stat.pfr_hands += 1
            
        self.db.commit()
        self.db.refresh(stat)
        return stat

    def get_all_stats(self) -> Dict[str, Dict]:
        stats = self.db.query(DBPlayerStat).all()
        result = {}
        for s in stats:
            vpip = s.vpip_hands / s.total_hands if s.total_hands > 0 else 0
            pfr = s.pfr_hands / s.total_hands if s.total_hands > 0 else 0
            result[s.name] = {
                "total_hands": s.total_hands,
                "vpip": vpip,
                "pfr": pfr
            }
        return result

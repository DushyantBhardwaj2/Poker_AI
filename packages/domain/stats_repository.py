import uuid
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from .db_models import User, Opponent, OpponentStats, default_dynamic_features

class StatsRepository:
    def __init__(self, db: Session):
        self.db = db

    def _ensure_uuid(self, id_val) -> uuid.UUID:
        if isinstance(id_val, str):
            return uuid.UUID(id_val)
        return id_val

    def _ensure_user_exists(self, user_id: uuid.UUID, email: Optional[str] = None, name: Optional[str] = None):
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            new_user = User(
                user_id=user_id, 
                email=email if email else f"user-{str(user_id)[:8]}@pokersense.ai",
                name=name
            )
            self.db.add(new_user)
            try:
                self.db.flush()
            except Exception as e:
                self.db.rollback()
                user = self.db.query(User).filter(User.user_id == user_id).first()
                if not user:
                    raise e
        elif email or name:
            # Update existing user if info provided
            if email: user.email = email
            if name: user.name = name
            self.db.flush()

    def get_or_create_opponent(self, user_id: uuid.UUID, player_name: str, active_table_names: Optional[List[str]] = None) -> Opponent:
        user_id = self._ensure_uuid(user_id)
        self._ensure_user_exists(user_id)
        
        opponent = self.db.query(Opponent).filter(
            Opponent.user_id == user_id,
            Opponent.player_name == player_name
        ).first()

        if not opponent:
            opponent = Opponent(user_id=user_id, player_name=player_name)
            self.db.add(opponent)
            self.db.flush()  # Get opponent_id
            
            # Initialize stats with table-averaged baseline or defaults
            features = self.get_table_averaged_baseline(user_id, active_table_names) if active_table_names else None
            
            stats = OpponentStats(
                opponent_id=opponent.opponent_id,
                hands_played=10 if features else 0,
                dynamic_features=features if features else default_dynamic_features()
            )
            self.db.add(stats)
            self.db.commit()
            self.db.refresh(opponent)
            
        return opponent

    def update_player_stats(self, user_id: uuid.UUID, name: str, vpip_this_hand: bool, pfr_this_hand: bool, is_bluff: bool = False):
        user_id = self._ensure_uuid(user_id)
        opponent = self.get_or_create_opponent(user_id, name)
        stats = opponent.stats

        if not stats:
            # Should not happen due to get_or_create_opponent logic, but for safety:
            stats = OpponentStats(opponent_id=opponent.opponent_id)
            self.db.add(stats)

        # Update features
        features = dict(stats.dynamic_features) if stats.dynamic_features else default_dynamic_features()
        
        # SQL-style updates for core counts
        if stats.hands_played is None:
            stats.hands_played = 0
        stats.hands_played += 1
        
        # JSONB-style updates for ML features
        features["vpip_count"] = features.get("vpip_count", 0) + (1 if vpip_this_hand else 0)
        features["pfr_count"] = features.get("pfr_count", 0) + (1 if pfr_this_hand else 0)
        
        if is_bluff:
            features["strict_bluff_showdowns"] = features.get("strict_bluff_showdowns", 0) + 1

        # Re-assign to trigger SQLAlchemy detection
        stats.dynamic_features = features
        
        self.db.commit()
        self.db.refresh(stats)
        return stats

    def get_table_averaged_baseline(self, user_id: uuid.UUID, active_player_names: List[str]) -> Dict:
        """
        Calculates the average stats for a group of players to seed a new player's stats.
        Solves the ML cold-start problem.
        """
        user_id = self._ensure_uuid(user_id)
        if not active_player_names:
            return default_dynamic_features()

        # Query stats for existing players at the table
        results = self.db.query(OpponentStats).join(Opponent).filter(
            Opponent.user_id == user_id,
            Opponent.player_name.in_(active_player_names)
        ).all()

        if not results:
            return default_dynamic_features()

        # Average the features
        count = len(results)
        
        def get_stat(r, key):
            val = (r.dynamic_features.get(key, 0) if r.dynamic_features else 0) or 0
            hands = r.hands_played if r.hands_played is not None else 0
            return val / max(1, hands)

        avg_vpip = sum(get_stat(r, "vpip_count") for r in results) / count
        avg_pfr = sum(get_stat(r, "pfr_count") for r in results) / count
        avg_bluff = sum(get_stat(r, "strict_bluff_showdowns") for r in results) / count
        
        # Seed with 10 hands worth of "average" data to provide stability for ML
        return {
            "vpip_count": int(avg_vpip * 10),
            "pfr_count": int(avg_pfr * 10),
            "aggression_ip": 0.0,
            "aggression_oop": 0.0,
            "strict_bluff_showdowns": int(avg_bluff * 10)
        }

    def get_all_stats(self, user_id: uuid.UUID) -> Dict[str, Dict]:
        user_id = self._ensure_uuid(user_id)
        results = self.db.query(Opponent, OpponentStats).join(OpponentStats).filter(
            Opponent.user_id == user_id
        ).all()
        
        result = {}
        for opp, stats in results:
            hands = stats.hands_played if stats.hands_played is not None else 0
            features = stats.dynamic_features if stats.dynamic_features else {}
            
            vpip = (features.get("vpip_count", 0) or 0) / hands if hands > 0 else 0
            pfr = (features.get("pfr_count", 0) or 0) / hands if hands > 0 else 0
            
            result[opp.player_name] = {
                "total_hands": hands,
                "vpip": vpip,
                "pfr": pfr,
                "bluffs": features.get("strict_bluff_showdowns", 0) or 0
            }
        return result


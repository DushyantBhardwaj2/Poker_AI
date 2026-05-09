import uuid
from typing import Optional, Dict, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from .db_models import (
    User, Opponent, OpponentStats, GameSession,
    SessionOpponent, default_dynamic_features, default_session_features,
    HandHistory
)

# Archetype thresholds based on poker theory
ARCHETYPE_THRESHOLDS = {
    "Rock": { "vpip_max": 15, "pfr_max": 12 },
    "Nit": { "vpip_max": 20, "pfr_max": 16 },
    "TAG": { "vpip_min": 20, "vpip_max": 28, "pfr_min": 16, "pfr_max": 24 },
    "LAG": { "vpip_min": 35, "pfr_min": 28 },
    "Maniac": { "vpip_min": 45 },
    "Tight Passive": { "vpip_max": 25, "aggression_max": 1.5 },
    "Loose Passive": { "vpip_min": 30, "aggression_max": 1.5 },
    "Unknown": {}
}


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
            if email: user.email = email
            if name: user.name = name
            self.db.flush()

    def calculate_archetype(self, vpip: float, pfr: float, aggression: float) -> str:
        """Calculate playstyle archetype based on tracked stats"""
        # High VPIP + High aggression = LAG/Maniac
        if vpip >= 45:
            return "Maniac"
        if vpip >= 35 and aggression >= 3.0:
            return "LAG"
        if vpip >= 35:
            return "Loose Active"

        # Low VPIP + low aggression = Rock/Nit
        if vpip <= 15 and aggression <= 1.0:
            return "Rock"
        if vpip <= 20 and aggression <= 1.5:
            return "Nit"
        if vpip <= 20 and pfr <= 16:
            return "Tight"

        # Standard TAG/LAG
        if 20 <= vpip <= 30 and 15 <= pfr <= 25:
            return "TAG"

        # Loose passive
        if vpip >= 30 and aggression <= 1.5:
            return "Loose Passive"

        return "Unknown"

    def calculate_reliability(self, hands_played: int) -> str:
        """Calculate reliability score based on sample size"""
        if hands_played >= 500:
            return "High"
        elif hands_played >= 100:
            return "Medium"
        else:
            return "Low"

    def calculate_behavioral_description(
        self,
        vpip: float = 0.25,
        pfr: float = 0.18,
        agg_freq: float = 0.30,
        cbet_rate: float = 0.65,
        wtsd: float = 0.30,
        bluff_river_rate: float = 0.15,
        fold_to_river: float = 0.40
    ) -> str:
        """
        Convert numeric stats to human-readable behavioral description.
        Used for frontend display instead of raw VPIP/PFR/AGG numbers.

        Examples: "Likes to bluff", "Tight and passive", "Hand-focused player", "Aggressive post-flop"
        """
        descriptions = []

        # Bluffing tendency
        if bluff_river_rate > 0.35:
            descriptions.append("frequently bluffs")
        elif bluff_river_rate > 0.20:
            descriptions.append("likes to bluff")
        elif bluff_river_rate < 0.10:
            descriptions.append("rarely bluffs")

        # Playing style (tight vs loose)
        if vpip > 0.40:
            descriptions.append("loose player")
        elif vpip < 0.18:
            descriptions.append("tight player")

        # Aggression (passive vs aggressive)
        if agg_freq > 0.50:
            descriptions.append("very aggressive")
        elif agg_freq > 0.35:
            descriptions.append("aggressive")
        elif agg_freq < 0.20:
            descriptions.append("passive")

        # Showdown tendency
        if wtsd > 0.40:
            descriptions.append("shows up often")
        elif wtsd < 0.22:
            descriptions.append("folds often")

        # C-bet behavior
        if cbet_rate > 0.80:
            descriptions.append("continuous barrels")
        elif cbet_rate < 0.45:
            descriptions.append("checked back")

        # Street-specific insights
        if fold_to_river > 0.55:
            descriptions.append("folds to river bets")

        if not descriptions:
            return "Unknown"

        # Return most descriptive 2 characteristics
        return ", ".join(descriptions[:2])

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
            self.db.flush()

            # Initialize stats with table-averaged baseline or defaults
            features = self.get_table_averaged_baseline(user_id, active_table_names) if active_table_names else None
            initial_features = features if features else default_dynamic_features()

            stats = OpponentStats(
                opponent_id=opponent.opponent_id,
                hands_played=10 if features else 0,
                dynamic_features=initial_features,
                session_features=default_session_features(),
                reliability_score=self.calculate_reliability(10 if features else 0)
            )
            self.db.add(stats)
            self.db.commit()
            self.db.refresh(opponent)

        # Update last seen
        opponent.last_seen = datetime.utcnow()
        self.db.commit()

        return opponent

    def update_player_stats(
        self,
        user_id: uuid.UUID,
        name: str,
        vpip_this_hand: bool,
        pfr_this_hand: bool,
        is_bluff: bool = False,
        made_cbet: bool = False,
        cbet_succeeded: bool = False,
        made_three_bet: bool = False,
        three_bet_succeeded: bool = False,
        fold_to_river: bool = False,
        called_showdown: bool = False,
        won_showdown: bool = False,
        bet_amount: float = 0,
        call_amount: float = 0
    ):
        """Enhanced stat tracking for Phase 3"""
        user_id = self._ensure_uuid(user_id)
        opponent = self.get_or_create_opponent(user_id, name)
        stats = opponent.stats

        if not stats:
            stats = OpponentStats(opponent_id=opponent.opponent_id)
            self.db.add(stats)

        features = dict(stats.dynamic_features) if stats.dynamic_features else default_dynamic_features()
        session_features = dict(stats.session_features) if stats.session_features else default_session_features()

        # Update hand count
        if stats.hands_played is None:
            stats.hands_played = 0
        stats.hands_played += 1

        # Update session features
        session_features["hands_played"] = session_features.get("hands_played", 0) + 1
        
        recent_history = session_features.get("recent_history", [])
        recent_history.append({
            "vpip": vpip_this_hand,
            "pfr": pfr_this_hand,
            "bets": bet_amount,
            "calls": call_amount
        })
        if len(recent_history) > 10:
            recent_history = recent_history[-10:]
        session_features["recent_history"] = recent_history

        # Core stats
        features["vpip_count"] = features.get("vpip_count", 0) + (1 if vpip_this_hand else 0)
        features["pfr_count"] = features.get("pfr_count", 0) + (1 if pfr_this_hand else 0)

        # Session tracking
        if vpip_this_hand:
            session_features["vpip_count"] = session_features.get("vpip_count", 0) + 1
        if pfr_this_hand:
            session_features["pfr_count"] = session_features.get("pfr_count", 0) + 1

        # C-bet tracking
        if made_cbet:
            features["cbet_count"] = features.get("cbet_count", 0) + 1
            session_features["cbet_count"] = session_features.get("cbet_count", 0) + 1
            if cbet_succeeded:
                features["cbet_success"] = features.get("cbet_success", 0) + 1

        # 3-bet tracking
        if made_three_bet:
            features["three_bet_count"] = features.get("three_bet_count", 0) + 1
            session_features["three_bet_count"] = session_features.get("three_bet_count", 0) + 1
            if three_bet_succeeded:
                features["three_bet_success"] = features.get("three_bet_success", 0) + 1

        # Fold tracking
        if fold_to_river:
            features["fold_to_river_bet"] = features.get("fold_to_river_bet", 0) + 1

        # Showdown tracking
        if called_showdown:
            features["calls_showdown"] = features.get("calls_showdown", 0) + 1
        if won_showdown:
            features["wins_at_showdown"] = features.get("wins_at_showdown", 0) + 1

        # Bet/Call totals for aggression calculation
        features["total_bets"] = features.get("total_bets", 0) + bet_amount
        features["total_calls"] = features.get("total_calls", 0) + call_amount

        # Session aggression
        session_features["session_bets"] = session_features.get("session_bets", 0.0) + bet_amount
        session_features["session_calls"] = session_features.get("session_calls", 0.0) + call_amount

        # Bluff tracking
        if is_bluff:
            features["strict_bluff_showdowns"] = features.get("strict_bluff_showdowns", 0) + 1

        # Update reliability
        stats.reliability_score = self.calculate_reliability(stats.hands_played)

        # Update archetype
        vpip = (features.get("vpip_count", 0) or 0) / max(1, stats.hands_played) * 100
        pfr = (features.get("pfr_count", 0) or 0) / max(1, stats.hands_played) * 100
        aggression = (features.get("total_bets", 0) or 0) / max(1, features.get("total_calls", 1))

        if stats.hands_played >= 20:  # Only classify after 20 hands
            new_archetype = self.calculate_archetype(vpip, pfr, aggression)
            if new_archetype != "Unknown":
                opponent.playstyle_archetype = new_archetype

            # Calculate behavioral description after sufficient sample
            cbet_rate = (features.get("cbet_success", 0) or 0) / max(1, features.get("cbet_count", 1))
            wtsd = (features.get("wins_at_showdown", 0) or 0) / max(1, features.get("calls_showdown", 1))
            fold_to_river = (features.get("fold_to_river_bet", 0) or 0) / max(1, stats.hands_played)
            bluff_rate = (features.get("strict_bluff_showdowns", 0) or 0) / max(1, stats.hands_played)

            stats.behavioral_description = self.calculate_behavioral_description(
                vpip=vpip / 100,
                pfr=pfr / 100,
                agg_freq=aggression if aggression < 1 else aggression / 100,
                cbet_rate=cbet_rate,
                wtsd=wtsd,
                bluff_river_rate=bluff_rate,
                fold_to_river=fold_to_river
            )

        # Assign back to trigger SQLAlchemy detection
        stats.dynamic_features = features
        stats.session_features = session_features
        stats.last_hand_timestamp = datetime.utcnow()

        self.db.commit()
        self.db.refresh(stats)
        return stats

    def get_table_averaged_baseline(self, user_id: uuid.UUID, active_player_names: List[str]) -> Dict:
        """Calculates the average stats for a group of players to seed a new player's stats."""
        user_id = self._ensure_uuid(user_id)
        if not active_player_names:
            return default_dynamic_features()

        results = self.db.query(OpponentStats).join(Opponent).filter(
            Opponent.user_id == user_id,
            Opponent.player_name.in_(active_player_names)
        ).all()

        if not results:
            return default_dynamic_features()

        count = len(results)

        def get_stat(r, key):
            val = (r.dynamic_features.get(key, 0) if r.dynamic_features else 0) or 0
            hands = r.hands_played if r.hands_played is not None else 0
            return val / max(1, hands)

        avg_vpip = sum(get_stat(r, "vpip_count") for r in results) / count
        avg_pfr = sum(get_stat(r, "pfr_count") for r in results) / count
        avg_bluff = sum(get_stat(r, "strict_bluff_showdowns") for r in results) / count

        return {
            "vpip_count": int(avg_vpip * 10),
            "pfr_count": int(avg_pfr * 10),
            "aggression_ip": 0.0,
            "aggression_oop": 0.0,
            "strict_bluff_showdowns": int(avg_bluff * 10),
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

    def get_all_stats(self, user_id: uuid.UUID) -> Dict[str, Dict]:
        """Get comprehensive stats for all opponents"""
        user_id = self._ensure_uuid(user_id)
        results = self.db.query(Opponent, OpponentStats).outerjoin(OpponentStats).filter(
            Opponent.user_id == user_id
        ).all()

        result = {}
        for opp, stats in results:
            hands = stats.hands_played if stats and stats.hands_played is not None else 0
            features = stats.dynamic_features if stats and stats.dynamic_features else {}

            vpip = (features.get("vpip_count", 0) or 0) / hands * 100 if hands > 0 else 0
            pfr = (features.get("pfr_count", 0) or 0) / hands * 100 if hands > 0 else 0
            cbet_rate = (features.get("cbet_success", 0) or 0) / max(1, features.get("cbet_count", 1)) * 100
            three_bet_rate = (features.get("three_bet_success", 0) or 0) / max(1, features.get("three_bet_count", 1)) * 100

            # Calculate aggression
            total_bets = features.get("total_bets", 0) or 0
            total_calls = features.get("total_calls", 0) or 0
            aggression = total_bets / max(1, total_calls)

            result[opp.player_name] = {
                "total_hands": hands,
                "vpip": round(vpip, 1),
                "pfr": round(pfr, 1),
                "aggression": round(aggression, 2),
                "bluffs": features.get("strict_bluff_showdowns", 0) or 0,
                "cbet_success_rate": round(cbet_rate, 1),
                "three_bet_rate": round(three_bet_rate, 1),
                "wtsd": round((features.get("wins_at_showdown", 0) or 0) / max(1, features.get("calls_showdown", 1)) * 100, 1),
                "archetype": opp.playstyle_archetype or "Unknown",
                "reliability": stats.reliability_score if stats else "Low",
                "notes": opp.notes or "",
                "last_seen": opp.last_seen.isoformat() if opp.last_seen else None
            }
        return result

    def get_opponent_profile(self, user_id: uuid.UUID, player_name: str) -> Optional[Dict]:
        """Get detailed profile for a single opponent"""
        user_id = self._ensure_uuid(user_id)
        opponent = self.db.query(Opponent).filter(
            Opponent.user_id == user_id,
            Opponent.player_name == player_name
        ).first()

        if not opponent:
            return None

        stats = opponent.stats
        hands = stats.hands_played if stats and stats.hands_played else 0
        features = stats.dynamic_features if stats and stats.dynamic_features else {}

        # Calculate session vs baseline comparison
        session_features = stats.session_features if stats and stats.session_features else {}

        # Rolling window: last 10 hands from session (more responsive than lifetime)
        recent_history = session_features.get("recent_history", [])
        rolling_hands = len(recent_history)

        # VPIP Drift - use rolling window instead of requiring 50+ lifetime hands
        baseline_vpip = (features.get("vpip_count", 0) or 0) / max(1, hands) * 100 if hands > 0 else 0
        if rolling_hands > 0:
            session_vpip = sum(1 for h in recent_history if h.get("vpip")) / rolling_hands * 100
        else:
            session_vpip = 0

        # Require smaller sample for shift detection: 10 rolling vs 50 lifetime, 3+ session vs 10
        vpip_shifting = abs(session_vpip - baseline_vpip) > 10 if rolling_hands >= 3 else False

        # Aggression Drift
        baseline_agg = (features.get("total_bets", 0) or 0) / max(1, features.get("total_calls", 1))
        if rolling_hands > 0:
            session_bets = sum(h.get("bets", 0) for h in recent_history)
            session_calls = sum(h.get("calls", 0) for h in recent_history)
            session_agg = session_bets / max(1, session_calls)
        else:
            session_agg = baseline_agg
            
        agg_shifting = (session_agg > baseline_agg * 1.5 or session_agg < baseline_agg * 0.5) if rolling_hands >= 3 else False

        is_shifting = vpip_shifting or agg_shifting
        
        direction = "stable"
        if is_shifting:
            if session_vpip > baseline_vpip + 10 or session_agg > baseline_agg * 1.5:
                direction = "more_aggressive"
            else:
                direction = "more_passive"

        return {
            "player_name": player_name,
            "archetype": opponent.playstyle_archetype or "Unknown",
            "behavioral_description": stats.behavioral_description if stats and stats.behavioral_description else "Unknown",
            "notes": opponent.notes or "",
            "hands_played": hands,
            "reliability": stats.reliability_score if stats else "Low",
            "vpip": round(baseline_vpip, 1),
            "pfr": round((features.get("pfr_count", 0) or 0) / max(1, hands) * 100, 1),
            "aggression": round(baseline_agg, 2),
            "cbet_rate": round((features.get("cbet_success", 0) or 0) / max(1, features.get("cbet_count", 1)) * 100, 1),
            "three_bet_rate": round((features.get("three_bet_success", 0) or 0) / max(1, features.get("three_bet_count", 1)) * 100, 1),
            "wtsd": round((features.get("wins_at_showdown", 0) or 0) / max(1, features.get("calls_showdown", 1)) * 100, 1),
            "fold_to_river": features.get("fold_to_river_bet", 0) or 0,
            "session_vpip": round(session_vpip, 1),
            "session_aggression": round(session_agg, 2),
            "is_shifting": is_shifting,
            "shift_direction": direction,
            "last_seen": opponent.last_seen.isoformat() if opponent.last_seen else None
        }

    def update_opponent_notes(self, user_id: uuid.UUID, player_name: str, notes: str) -> bool:
        """Update opponent notes"""
        user_id = self._ensure_uuid(user_id)
        opponent = self.db.query(Opponent).filter(
            Opponent.user_id == user_id,
            Opponent.player_name == player_name
        ).first()

        if not opponent:
            return False

        opponent.notes = notes
        self.db.commit()
        return True

    def reset_session_stats(self, user_id: uuid.UUID):
        """Reset session-only features for baseline comparison at session start"""
        user_id = self._ensure_uuid(user_id)
        results = self.db.query(OpponentStats).join(Opponent).filter(
            Opponent.user_id == user_id
        ).all()

        for stats in results:
            stats.session_features = default_session_features()

        self.db.commit()

    def get_recent_opponents(self, user_id: uuid.UUID, limit: int = 10) -> List[Dict]:
        """Get list of most recently played opponents"""
        user_id = self._ensure_uuid(user_id)
        results = self.db.query(Opponent).filter(
            Opponent.user_id == user_id
        ).order_by(Opponent.last_seen.desc()).limit(limit).all()

        return [
            {
                "player_name": opp.player_name,
                "archetype": opp.playstyle_archetype or "Unknown",
                "last_seen": opp.last_seen.isoformat() if opp.last_seen else None,
                "hands_played": opp.stats.hands_played if opp.stats else 0
            }
            for opp in results
        ]

    # --- Phase 6: Session Analytics & Post-Game Review ---

    def record_hand_result(
        self,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        street: str,
        pot_size: float,
        your_cards: List[Dict] = None,
        community_cards: List[Dict] = None,
        result: str = None,
        amount_won: float = 0.0,
        action_count: int = 0,
        duration_seconds: int = 0,
        tactical_data: Dict = None
    ) -> HandHistory:
        """Record the result of a hand for session analytics and leak detection"""
        user_id = self._ensure_uuid(user_id)
        session_id = self._ensure_uuid(session_id)

        # Basic Leak Detection
        leak_detected = False
        leak_description = None
        
        if tactical_data:
            win_prob = tactical_data.get("adjusted_win_probability", 0)
            pot_odds = tactical_data.get("pot_odds", 0)
            verdict = tactical_data.get("verdict", "")
            
            # Leak 1: -EV Call (Equity < Pot Odds)
            if verdict == "CALL" and win_prob < (pot_odds / 100) and win_prob > 0:
                leak_detected = True
                leak_description = f"-EV Call: Needed {pot_odds}% equity, but only had {round(win_prob * 100, 1)}%."
            
            # Leak 2: Over-Aggression (Bluffing into high-strength boards or against nits)
            # (Requires more complex logic, but we can flag high-variance bluffs)
            elif verdict == "RAISE" and tactical_data.get("bluff_probability", 0) > 0.7 and result == "loss":
                 leak_detected = True
                 leak_description = "High Variance Bluff: Attempted a major bluff that failed to get through."

        hand = HandHistory(
            session_id=session_id,
            street=street,
            pot_size=pot_size,
            your_cards=your_cards,
            community_cards=community_cards,
            result=result,
            amount_won=amount_won,
            action_count=action_count,
            duration_seconds=duration_seconds,
            tactical_data=tactical_data,
            leak_detected=leak_detected,
            leak_description=leak_description
        )
        self.db.add(hand)

        # Update session totals
        session = self.db.query(GameSession).filter(
            GameSession.session_id == session_id
        ).first()
        if session:
            session.total_hands = (session.total_hands or 0) + 1
            session.total_winnings = (session.total_winnings or 0.0) + amount_won

        self.db.commit()
        self.db.refresh(hand)
        return hand

    def get_session_analytics(self, user_id: uuid.UUID, session_id: uuid.UUID = None) -> Dict:
        """Get comprehensive session analytics"""
        user_id = self._ensure_uuid(user_id)

        # Get the most recent session if not specified
        if session_id:
            session_id = self._ensure_uuid(session_id)
            session = self.db.query(GameSession).filter(
                GameSession.session_id == session_id,
                GameSession.user_id == user_id
            ).first()
        else:
            session = self.db.query(GameSession).filter(
                GameSession.user_id == user_id
            ).order_by(GameSession.started_at.desc()).first()

        if not session:
            return {
                "summary": {
                    "session_id": "",
                    "start_time": "",
                    "end_time": None,
                    "total_hands": 0,
                    "hands_played": 0,
                    "vpip_hands": 0,
                    "pfr_hands": 0,
                    "total_winnings": 0,
                    "biggest_pot": 0,
                    "biggest_loss": 0,
                    "showdown_wins": 0,
                    "showdown_losses": 0,
                    "folds": 0,
                    "avg_position": 0
                },
                "recent_hands": [],
                "vpip_percentage": 0,
                "pfr_percentage": 0,
                "win_rate": 0,
                "showdown_rate": 0,
                "avg_hand_duration": 0,
                "most_played_opponent": None
            }

        # Get hand history for this session
        hands = self.db.query(HandHistory).filter(
            HandHistory.session_id == session.session_id
        ).order_by(HandHistory.created_at.desc()).limit(20).all()

        # Calculate metrics
        total_hands = len(hands)
        if total_hands == 0:
            return {
                "summary": {
                    "session_id": str(session.session_id),
                    "start_time": session.started_at.isoformat() if session.started_at else "",
                    "end_time": session.ended_at.isoformat() if session.ended_at else None,
                    "total_hands": 0,
                    "hands_played": 0,
                    "vpip_hands": 0,
                    "pfr_hands": 0,
                    "total_winnings": session.total_winnings or 0,
                    "biggest_pot": 0,
                    "biggest_loss": 0,
                    "showdown_wins": 0,
                    "showdown_losses": 0,
                    "folds": 0,
                    "avg_position": 0
                },
                "recent_hands": [],
                "vpip_percentage": 0,
                "pfr_percentage": 0,
                "win_rate": 0,
                "showdown_rate": 0,
                "avg_hand_duration": 0,
                "most_played_opponent": None
            }

        win_count = sum(1 for h in hands if h.result == "win")
        loss_count = sum(1 for h in hands if h.result == "loss")
        tie_count = sum(1 for h in hands if h.result == "tie")
        biggest_pot = max((h.amount_won for h in hands if h.amount_won > 0), default=0)
        biggest_loss = min((h.amount_won for h in hands if h.amount_won < 0), default=0)
        total_duration = sum(h.duration_seconds or 0 for h in hands)

        # Get opponent stats from session
        session_opponents = self.db.query(SessionOpponent).filter(
            SessionOpponent.session_id == session.session_id
        ).all()

        most_played = None
        if session_opponents:
            most_played = max(session_opponents, key=lambda x: x.hands_played)
            if most_played and most_played.opponent:
                most_played = most_played.opponent.player_name

        return {
            "summary": {
                "session_id": str(session.session_id),
                "start_time": session.started_at.isoformat() if session.started_at else "",
                "end_time": session.ended_at.isoformat() if session.ended_at else None,
                "total_hands": total_hands,
                "hands_played": total_hands,  # Simplified - counted from hand_history
                "vpip_hands": 0,  # Would require integration with game state
                "pfr_hands": 0,
                "total_winnings": session.total_winnings or 0,
                "biggest_pot": biggest_pot,
                "biggest_loss": biggest_loss,
                "showdown_wins": win_count,
                "showdown_losses": loss_count,
                "folds": 0,
                "avg_position": 0
            },
                "recent_hands": [
                    {
                        "hand_id": str(h.hand_id),
                        "street": h.street,
                        "pot_size": h.pot_size or 0,
                        "your_cards": h.your_cards or [],
                        "community_cards": h.community_cards or [],
                        "result": h.result,
                        "amount_won": h.amount_won or 0,
                        "action_count": h.action_count or 0,
                        "duration_seconds": h.duration_seconds or 0,
                        "tactical_data": h.tactical_data or {},
                        "leak_detected": h.leak_detected or False,
                        "leak_description": h.leak_description or "",
                        "timestamp": h.created_at.isoformat() if h.created_at else ""
                    }
                    for h in hands
                ],
            "vpip_percentage": 0,  # Requires game state integration
            "pfr_percentage": 0,
            "win_rate": (win_count / total_hands * 100) if total_hands > 0 else 0,
            "showdown_rate": ((win_count + loss_count) / total_hands * 100) if total_hands > 0 else 0,
            "avg_hand_duration": int(total_duration / total_hands) if total_hands > 0 else 0,
            "most_played_opponent": most_played
        }

    def get_hand_history(self, user_id: uuid.UUID, limit: int = 50) -> List[Dict]:
        """Get overall hand history across all sessions"""
        user_id = self._ensure_uuid(user_id)

        # Get all sessions for user
        sessions = self.db.query(GameSession).filter(
            GameSession.user_id == user_id
        ).order_by(GameSession.started_at.desc()).limit(10).all()

        all_hands = []
        for session in sessions:
            hands = self.db.query(HandHistory).filter(
                HandHistory.session_id == session.session_id
            ).order_by(HandHistory.created_at.desc()).limit(limit).all()

            for hand in hands:
                all_hands.append({
                    "hand_id": str(hand.hand_id),
                    "street": hand.street,
                    "pot_size": hand.pot_size or 0,
                    "your_cards": hand.your_cards or [],
                    "community_cards": hand.community_cards or [],
                    "result": hand.result,
                    "amount_won": hand.amount_won or 0,
                    "action_count": hand.action_count or 0,
                    "duration_seconds": hand.duration_seconds or 0,
                    "tactical_data": hand.tactical_data or {},
                    "leak_detected": hand.leak_detected or False,
                    "leak_description": hand.leak_description or "",
                    "timestamp": hand.created_at.isoformat() if hand.created_at else ""
                })

        return all_hands[:limit]

    def end_session(self, user_id: uuid.UUID, session_id: uuid.UUID) -> bool:
        """Mark a session as ended"""
        user_id = self._ensure_uuid(user_id)
        session_id = self._ensure_uuid(session_id)

        session = self.db.query(GameSession).filter(
            GameSession.session_id == session_id,
            GameSession.user_id == user_id
        ).first()

        if session:
            session.ended_at = datetime.utcnow()
            self.db.commit()
            return True
        return False
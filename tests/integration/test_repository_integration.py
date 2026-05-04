import os
import sys
import uuid
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from packages.domain.database import engine, get_db
from packages.domain.stats_repository import StatsRepository
from packages.domain.db_models import User, Opponent, OpponentStats

def test_repository():
    load_dotenv()
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 1. Get our test user
        user = db.query(User).filter(User.email == "admin@pokersense.ai").first()
        if not user:
            print("Error: Run verify_db.py first to create the admin user.")
            return
        
        repo = StatsRepository(db)
        
        # 2. Test get_or_create_opponent (Cold Start)
        print("\n--- Testing Cold Start ---")
        import random
        suffix = random.randint(1000, 9999)
        player_a = f"Alpha_{suffix}"
        player_b = f"Beta_{suffix}"
        opp_a = repo.get_or_create_opponent(user.user_id, player_a)
        print(f"Created/Found {player_a}: {opp_a.opponent_id}")
        print(f"Initial Features: {opp_a.stats.dynamic_features}")
        
        # 3. Test update_player_stats
        print("\n--- Testing Stats Update ---")
        repo.update_player_stats(user.user_id, player_a, vpip_this_hand=True, pfr_this_hand=False, is_bluff=True)
        db.refresh(opp_a.stats)
        print(f"After 1 hand: {opp_a.stats.dynamic_features}")
        print(f"Hands played: {opp_a.stats.hands_played}")
        
        # 4. Test table-averaged baseline
        print("\n--- Testing Table Averaged Baseline ---")
        player_b = "Player Beta"
        # Seed player A with some high stats
        for _ in range(9):
             repo.update_player_stats(user.user_id, player_a, vpip_this_hand=True, pfr_this_hand=True)
        
        # Now create Player B, using Player A's averages
        opp_b = repo.get_or_create_opponent(user.user_id, player_b, active_table_names=[player_a])
        print(f"Created {player_b} with baseline from {player_a}")
        print(f"Player B Initial Features: {opp_b.stats.dynamic_features}")
        
        # Player A has 100% VPIP (10/10), 90% PFR (9/10)
        # Baseline should be ~10 hands worth of that.
        # vpip_count should be around 10, pfr_count around 9.
        
        # Clean up Beta for idempotency in repeat tests if needed, 
        # but for now we'll just leave it or use a random name.
        
    finally:
        db.close()

if __name__ == "__main__":
    test_repository()

"""Behaviour of StatsRepository against a real database.

The interesting property here is the cold start. A brand new opponent has no
stats, so the profiler has nothing to say about them, and the repository seeds
them from the average of the players already at the table instead of from a
global default. This file asserts that; it used to print the numbers and leave
reading them to whoever ran it.

It also used to bail out with `print("Run verify_db.py first")` and `return` when
the admin user was missing, which pytest scores as a pass. The `admin_user`
fixture in tests/conftest.py creates it.
"""

import pytest

from packages.domain.db_models import Opponent, OpponentStats
from packages.domain.stats_repository import StatsRepository

pytestmark = pytest.mark.integration


@pytest.fixture
def repo(db):
    return StatsRepository(db)


def test_a_new_opponent_starts_with_no_history(repo, admin_user):
    opponent = repo.get_or_create_opponent(admin_user.user_id, "Cold Start")

    assert opponent.opponent_id is not None
    assert opponent.stats.hands_played == 0
    assert opponent.stats.dynamic_features["vpip_count"] == 0
    assert opponent.stats.dynamic_features["pfr_count"] == 0
    assert opponent.stats.reliability_score == "Low"


def test_get_or_create_is_idempotent(repo, admin_user):
    first = repo.get_or_create_opponent(admin_user.user_id, "Seen Twice")
    second = repo.get_or_create_opponent(admin_user.user_id, "Seen Twice")

    assert first.opponent_id == second.opponent_id
    rows = (
        repo.db.query(Opponent)
        .filter(Opponent.user_id == admin_user.user_id, Opponent.player_name == "Seen Twice")
        .count()
    )
    assert rows == 1


def test_one_hand_moves_the_counters(repo, admin_user):
    opponent = repo.get_or_create_opponent(admin_user.user_id, "Counter Check")
    repo.update_player_stats(
        admin_user.user_id,
        "Counter Check",
        vpip_this_hand=True,
        pfr_this_hand=False,
        is_bluff=True,
    )
    repo.db.refresh(opponent.stats)

    assert opponent.stats.hands_played == 1
    assert opponent.stats.dynamic_features["vpip_count"] == 1
    assert opponent.stats.dynamic_features["pfr_count"] == 0
    assert opponent.stats.dynamic_features["strict_bluff_showdowns"] == 1


def test_a_new_opponent_inherits_the_table_average(repo, admin_user):
    """A loose table makes the next unknown player a loose prior, not a default one."""
    known = "Table Maniac"
    repo.get_or_create_opponent(admin_user.user_id, known)
    for _ in range(10):
        repo.update_player_stats(
            admin_user.user_id, known, vpip_this_hand=True, pfr_this_hand=True
        )

    seeded = repo.get_or_create_opponent(
        admin_user.user_id, "Fresh Face", active_table_names=[known]
    )
    default = repo.get_or_create_opponent(admin_user.user_id, "Unseeded")

    # The baseline is worth ten notional hands of the table's observed behaviour.
    assert seeded.stats.hands_played == 10
    assert default.stats.hands_played == 0
    assert (
        seeded.stats.dynamic_features["vpip_count"]
        > default.stats.dynamic_features["vpip_count"]
    )
    # Still "Low", and correctly so: reliability turns Medium at 100 hands, and a
    # borrowed prior should not be allowed to look like a real read. The advisor
    # weights the same way, at hands/50.
    assert seeded.stats.reliability_score == "Low"


def test_stats_are_scoped_to_the_user(repo, admin_user, db):
    """Two users tracking a player of the same name must not share a row."""
    from packages.domain.db_models import User

    other = User(email="second-operator@example.com")
    db.add(other)
    db.commit()

    mine = repo.get_or_create_opponent(admin_user.user_id, "Shared Name")
    theirs = repo.get_or_create_opponent(other.user_id, "Shared Name")

    assert mine.opponent_id != theirs.opponent_id
    assert db.query(OpponentStats).filter(OpponentStats.opponent_id == mine.opponent_id).count() == 1

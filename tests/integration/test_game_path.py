"""A full hand through the stateless game endpoints.

The routes take their user from `get_current_user_id`, which verifies a Neon Auth
JWT. This overrides that dependency with a user the test created, which is the
supported way to test an authenticated route and does not need a signing key.

The previous version sent an `X-User-Id` header that no route reads, so it only
passed when `SKIP_AUTH=true` was set in the developer's environment, and the user
it carefully pre-registered was not the one the request ran as.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from apps.api.infrastructure.auth import get_current_user_id
from apps.api.interfaces.main import app
from packages.domain.db_models import User

pytestmark = pytest.mark.integration


@pytest.fixture
def client(db):
    """A client authenticated as a freshly created user."""
    user = User(user_id=uuid.uuid4(), email=f"game-path-{uuid.uuid4().hex[:8]}@example.com")
    db.add(user)
    db.commit()

    app.dependency_overrides[get_current_user_id] = lambda: str(user.user_id)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def act(client, state, player_index, action_type, amount=0):
    response = client.post(
        "/api/v1/game/action",
        json={
            "state": state,
            "action": {
                "player_index": player_index,
                "action_type": action_type,
                "amount": amount,
            },
        },
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_a_hand_plays_from_deal_to_showdown(client):
    """Three-handed: hero raises, one caller, one fold, then checks to the turn."""
    response = client.post(
        "/api/v1/game/start",
        json={
            "player_names": ["You", "Whale", "Nit"],
            "initial_stacks": [1000, 1000, 1000],
            "small_blind": 5,
            "big_blind": 10,
            "dealer_index": 0,
        },
    )
    assert response.status_code == 200, response.text
    state = response.json()

    # Dealer 0, small blind 1, big blind 2, so the first to act pre-flop is 0.
    assert state["round"] == "pre-flop"
    assert state["current_player_index"] == 0

    state = act(client, state, 0, "raise", 30)
    assert state["current_bet"] == 30
    assert state["players"][0]["stack"] == 970

    assert state["current_player_index"] == 1
    state = act(client, state, 1, "call")

    assert state["current_player_index"] == 2
    state = act(client, state, 2, "fold")

    assert state["round"] == "flop"

    # The small blind acts first post-flop.
    for expected_index in (1, 0):
        assert state["current_player_index"] == expected_index
        state = act(client, state, expected_index, "check")

    assert state["round"] == "turn"


def test_analyze_full_answers_for_a_live_state(client):
    response = client.post(
        "/api/v1/game/start",
        json={
            "player_names": ["You", "Whale"],
            "initial_stacks": [1000, 1000],
            "small_blind": 5,
            "big_blind": 10,
            "dealer_index": 0,
        },
    )
    assert response.status_code == 200, response.text
    state = response.json()

    hole_cards = [{"rank": "A", "suit": "s"}, {"rank": "A", "suit": "h"}]
    state["players"][0]["hole_cards"] = hole_cards
    state["community_cards"] = [
        {"rank": "A", "suit": "d"},
        {"rank": "K", "suit": "c"},
        {"rank": "J", "suit": "h"},
    ]

    response = client.post(
        "/api/v1/ai/analyze-full",
        json={
            "state": state,
            "history": [],
            "opponent_name": "Whale",
            "hole_cards": hole_cards,
            # Kept low deliberately: this asserts the endpoint is wired up, and
            # 1000 rollouts would make it the slowest test in the suite.
            "num_simulations": 100,
        },
    )
    assert response.status_code == 200, response.text
    analysis = response.json()

    assert "win_analysis" in analysis
    assert analysis["advice"]["action"] in {"fold", "check", "call", "bet", "raise", "all-in"}
    # Set over a pair of aces on an A-K-J board. Anything but a raise is a bug.
    assert analysis["advice"]["action"] == "raise"


def test_an_unauthenticated_request_is_rejected():
    """No dependency override here, so the real JWT check runs."""
    with TestClient(app) as anonymous:
        response = anonymous.post(
            "/api/v1/game/start",
            json={
                "player_names": ["You", "Whale"],
                "initial_stacks": [1000, 1000],
                "small_blind": 5,
                "big_blind": 10,
                "dealer_index": 0,
            },
        )
    assert response.status_code == 401

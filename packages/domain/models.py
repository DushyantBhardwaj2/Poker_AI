from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import uuid

class Suit(str, Enum):
    SPADES = "s"
    HEARTS = "h"
    DIAMONDS = "d"
    CLUBS = "c"

class Rank(str, Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "T"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

class Card(BaseModel):
    rank: Rank
    suit: Suit

    def __str__(self):
        return f"{self.rank.value}{self.suit.value}"

class ActionType(str, Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    RAISE = "raise"
    ALL_IN = "all-in"

class Action(BaseModel):
    player_index: int
    action_type: ActionType
    amount: float = 0.0

class PlayerStatus(str, Enum):
    ACTIVE = "active"
    FOLDED = "folded"
    ALL_IN = "all-in"
    SITTING_OUT = "sitting-out"

class Player(BaseModel):
    name: str
    stack: float
    hole_cards: List[Card] = Field(default_factory=list)
    current_bet: float = 0.0
    total_contributed: float = 0.0
    is_folded: bool = False # Legacy - kept for compatibility
    is_all_in: bool = False # Legacy - kept for compatibility
    status: PlayerStatus = PlayerStatus.ACTIVE
    has_acted: bool = False
    vpip_this_hand: bool = False
    pfr_this_hand: bool = False

class GameRound(str, Enum):
    PRE_FLOP = "pre-flop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"

class ActionRecord(BaseModel):
    player_name: str
    action_type: ActionType
    amount: float = 0.0
    street: GameRound

class GameSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    players: List[Player] = Field(default_factory=list)
    pot_size: float = 0.0
    current_street: GameRound = GameRound.PRE_FLOP
    actions_history: List[ActionRecord] = Field(default_factory=list)

class HandRank(int, Enum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10

class Pot(BaseModel):
    amount: float = 0.0
    eligible_player_indices: List[int] = Field(default_factory=list)

class GameState(BaseModel):
    players: List[Player]
    community_cards: List[Card] = Field(default_factory=list)
    pots: List[Pot] = Field(default_factory=lambda: [Pot()])
    pot: float = 0.0 # Total pot for convenience
    current_bet: float = 0.0
    last_raise_amount: float = 0.0
    current_player_index: int = 0
    dealer_index: int = 0
    round: GameRound = GameRound.PRE_FLOP
    small_blind: float
    big_blind: float

class LiveGameState(BaseModel):
    """
    Inference-ready snapshot of a hand.
    Combines core GameState with the necessary temporal and behavioral context for ML.
    """
    street: int # 1: Flop, 2: Turn, 3: River
    bet_amount: float
    pot_before: float
    starting_stack: float
    board_cards: List[str] 
    vpip: float
    pfr: float
    prev_street_dryness: float = 1.0
    prev_street_max_bet: float = 0.0
    prev_action_bet_size: float = 0.0 # Relative (bet/pot)


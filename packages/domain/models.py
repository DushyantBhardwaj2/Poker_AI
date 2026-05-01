from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

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

class Player(BaseModel):
    name: str
    stack: float
    hole_cards: List[Card] = Field(default_factory=list)
    current_bet: float = 0.0
    total_contributed: float = 0.0
    is_folded: bool = False
    is_all_in: bool = False
    has_acted: bool = False
    vpip_this_hand: bool = False
    pfr_this_hand: bool = False

class GameRound(str, Enum):
    PRE_FLOP = "pre-flop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"

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

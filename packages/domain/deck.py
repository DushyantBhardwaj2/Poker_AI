import random
from typing import List
from .models import Card, Rank, Suit

class Deck:
    def __init__(self):
        self.cards = [Card(rank=r, suit=s) for r in Rank for s in Suit]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, n: int = 1) -> List[Card]:
        if n > len(self.cards):
            raise ValueError("Not enough cards in deck")
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn

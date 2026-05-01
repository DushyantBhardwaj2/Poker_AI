from pokerkit import Card

try:
    card = list(Card.parse('As'))[0]
    print(f"Card: {card}")
    print(f"Rank: {card.rank}")
    print(f"Rank type: {type(card.rank)}")
    print(f"Rank Attributes: {[attr for attr in dir(card.rank) if not attr.startswith('_')]}")
except Exception as e:
    print(f"Failed: {e}")

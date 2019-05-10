class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return "<Card: suit:{} rank:{}>".format(self.suit, self.rank)

    def __str__(self):
        return "{} of {}".format(self.rank, self.suit)

    def suit(self):
        return self.suit

    def rank(self):
        return self.rank

    def full_card(self):
        return (self.suit, self.rank)

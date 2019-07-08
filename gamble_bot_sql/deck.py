import card
import random


class Deck:
    def __init__(self):
        self.unused_cards = self.make_standard_deck()
        self.used_cards = []

    def __repr__(self):
        return "<Deck: unused_cards:{} used_cards:{}>".format(self.unused_cards, self.used_cards)

    def __str__(self):
        msg = ["Unused cards:\n"]

        for playing_card in self.unused_cards:
            msg.append(f'{playing_card}\n')
        msg.append("Used cards:\n")
        for playing_card in self.used_cards:
            msg.append(f'{playing_card}\n')

        return msg

    # Makes a standard 52 card deck
    # Return a list of cards
    def make_standard_deck(self):
        deck = []
        suits = ["Clubs", "Diamonds", "Hearts", "Spades"]
        ranks = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                 "Jack", "Queen", "King"]

        for suit in suits:
            for rank in ranks:
                playing_card = card.Card(suit, rank)
                deck.append(playing_card)

        return deck

    # Reset the deck
    def reset(self):
        self.unused_cards = self.make_standard_deck()
        self.used_cards = []

    # Shuffle cards
    def shuffle(self):
        random.shuffle(self.unused_cards)

    # Deal the specified number of cards, if available
    # If not enough cards in deck to deal, return empty list
    # Update used_cards and unused_cards
    def deal(self, num_cards):
        if len(self.unused_cards) < num_cards:
            return []
        else:
            dealt = self.unused_cards[:num_cards]
            self.used_cards += dealt
            del self.unused_cards[:num_cards]
            return dealt

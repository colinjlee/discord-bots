import deck

#Closest to 21 without going over wins
#Blackjack = 21 on first 2 cards, gets 1.5x bet amount
class Blackjack:
    def __init__(self, bet):
        self.deck = deck.Deck().shuffle()
        self.in_game = True
        self.player_turn = True
        self.bet = bet
        self.dealer_hand = []
        self.player_hand = []

    #Return an int for the hand value
    #Jack, Queen, King = 10
    #2-10 = 2-10
    #Ace = 1 or 11
    #First 2 dealt cards add up to 21 = black jack
    def hand_value(self, hand):
        faces = {"Jack", "Queen", "King"}
        numbers = {"2", "3", "4", "5", "6", "7", "8", "9", "10"}
        value = aces = 0

        for playing_card in hand:
            rank = playing_card.rank()
            if rank in faces:
                value += 10
            elif rank in numbers:
                value += int(rank)
            else:
                aces += 1

        value_low = value + aces
        value_high = value + 10 + aces

        #Return higher of 2 numbers <= 21
        #If both are > 21 then returns lower value
        if value_high <= 21:
            return value_high
        else:
            return value_low

    #Return dealer's hand value
    def dealer_hand_value(self):
        return hand_value(self.dealer_hand)

    #Return player's hand value
    def player_hand_value(self):
        return hand_value(self.player_hand)

    #Dealer hits until his hand value is > 17
    def dealer_hit(self):
        self.dealer_hand += self.deck.deal(1)

    #Player hit
    def player_hit(self):
        self.player_hand += self.deck.deal(1)

    #Player stand
    def player_stand(self):
        self.player_turn = False

    #TODO: Player double down
    #Only available after initial dealing of 2 cards
    #Bet doubles and player is dealt 1 more card
    #def player_dd(self):

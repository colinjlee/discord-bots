import deck

#Closest to 21 without going over wins
#Blackjack = 21 on first 2 cards, gets 1.5x bet amount
class Blackjack:
    def __init__(self, name, bet):
        #Game state (from player's perspective) of (-1): Ongoing, (0): Won, (1): Lost, (2): Tied
        self.game_state = -1
        self.bj_deck = deck.Deck()
        self.bj_deck.shuffle()

        #Player stuff
        self.player_name = name.title()
        self.player_turn = True
        self.player_bet = bet
        self.player_bj = False
        self.player_hand = self.bj_deck.deal(2)

        #Dealer stuff
        self.dealer_bj = False
        self.dealer_hand = self.bj_deck.deal(1) #Simulate showing 1 card

        #Check for blackjack (natural 21)
        self.check_game()

    def __str__(self):
        msg = "**__{}'s game with bet amount: ${}__**\n\n".format(self.player_name, self.player_bet)
        if self.player_bj == True:
            msg += "**__{} got a blackjack!__**\n".format(self.player_name)
        else:
            msg += "**__{}'s hand with value {}:__**\n".format(self.player_name, self.player_hand_value())
        msg += self.hand_as_str(self.player_hand)

        if self.dealer_bj == True:
            msg += "\n\n**__Dealer got a blackjack!__**\n"
        else:
            msg += "\n\n**__Dealer's hand with value {}:__**\n".format(self.dealer_hand_value())
        msg += self.hand_as_str(self.dealer_hand)

        if self.game_state == 0:
            msg += "\n\n**You won ${}**".format(self.player_bet)
        elif self.game_state == 1:
            msg += "\n\n**You lost ${}**".format(self.player_bet)
        elif self.game_state == 2:
            msg += "\n\n**You tied"

        return msg

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
            rank = playing_card.rank
            if rank in faces:
                value += 10
            elif rank in numbers:
                value += int(rank)
            else:
                aces += 1

        if aces == 0:
            return value
        else:
            value_low = value + aces
            value_high = value + 10 + aces

            #Return higher of 2 numbers <= 21
            #If both are > 21 then returns lower value
            if value_high <= 21:
                return value_high
            else:
                return value_low

    #Return hand as string
    def hand_as_str(self, hand):
        msg = ""
        for player_card in hand:
            msg += player_card.__str__() + "\n"

        return msg[:-1]

    #Print dealer's hand
    def print_dealer_hand(self):
        print(self.hand_as_str(self.dealer_hand))

    #Print player's hand
    def print_player_hand(self):
        print(self.hand_as_str(self.player_hand))

    #Return dealer's hand value
    def dealer_hand_value(self):
        return self.hand_value(self.dealer_hand)

    #Return player's hand value
    def player_hand_value(self):
        return self.hand_value(self.player_hand)

    #Dealer hit
    def dealer_hit(self):
        self.dealer_hand += self.bj_deck.deal(1)

    #Player hit
    def player_hit(self):
        self.player_hand += self.bj_deck.deal(1)
        #Check if player's hand is over 21 after new card
        self.check_game()

    #Player stands so it is dealer's turn
    def player_stand(self):
        self.player_turn = False

        #Dealer hits until his hand value is > 17
        while self.dealer_hand_value() < 17:
            self.dealer_hit()

        self.check_game()

    #Only available after initial dealing of 2 cards
    #Bet doubles and player is dealt 1 more card
    def player_dd(self):
        if len(self.player_hand) == 2:
            self.player_bet *= self.player_bet
            self.player_hit()
            self.player_stand()

    #Calculate who won
    #Game state (from player's perspective) of (-1): Ongoing, (0): Won, (1): Lost, (2): Tied
    def check_game(self):
        val_player = self.player_hand_value()
        val_dealer = self.dealer_hand_value()
        #Initial game check
        #Player got a blackjack
        if len(self.player_hand) == 2 and val_player == 21:
            self.player_bj = True
            self.player_bet = int(round(self.player_bet * 1.5))
            #Draw one more card for dealer since game starts with only 1 and get new value
            self.dealer_hit()
            val_dealer = self.dealer_hand_value()
            #Dealer also got a Blackjack
            if val_dealer == 21:
                self.dealer_bj = True
                self.game_state = 2
            else:
                self.game_state = 0
        #Check if player busted after card draw
        elif self.player_turn == True:
            #Player bust
            if val_player > 21:
                self.game_state = 1
                self.player_turn == False
        #Player turn ended without player busting
        elif self.player_turn == False:
            #Dealer bust
            if val_dealer > 21:
                self.game_state = 0
            #Neither bust, check higher value
            else:
                #Dealer got blackjack
                if len(self.dealer_hand) == 2 and val_dealer == 21:
                    self.dealer_bj = True
                    self.game_state = 1
                elif val_player < val_dealer:
                    self.game_state = 1
                elif val_player > val_dealer:
                    self.game_state = 0
                else:
                    self.game_state = 2

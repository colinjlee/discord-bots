import gspread
from oauth2client.service_account import ServiceAccountCredentials
import asyncio
import sqlite3


#Google sheets things
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
"https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

class Gamble_Bot_Stats_SQL():
    def __init__(self):
        # Connect to database
        self.statsConnector = sqlite3.connect("gbUserStats.db")
        self.statsCursor = self.statsConnector.cursor()

        # Google sheets containing public rates of philosopher book and marvel machine
        # Philo rates: http://maplestory.nexon.net/micro-site/42030
        # Marvel rates: http://maplestory.nexon.net/micro-site/39184
        self.philoSheet = client.open("Philosopher Book Rates").worksheets()[-1]
        self.marvelSheet = client.open("Marvel Machine Rates").worksheets()[-1]

        # List of marvel/philo items to roll from
        self.philoList1 = self.makePhiloList1()
        self.philoList2 = self.makePhiloList2()
        self.marvelList1 = self.makeMarvelList1()
        self.marvelList2 = self.makeMarvelList2()
        self.marvelList3 = self.makeMarvelList3()

        # Mapping of column names to official item name
        self.marvelItemMapping = self.mapMarvelItems() # Includes rolls
        self.philoItemMapping = self.mapPhiloItems() # Includes rolls
        self.bjItemMapping = self.mapBJItems()

        # List of lucky items possible to get in marvel/philo
        self.marvelLuckyList = {k: 0 for k in self.marvelItemMapping.keys()}
        self.philoLuckyList = {k: 0 for k in self.philoItemMapping.keys()}


    # Close the connections
    def __del__(self):
        self.statsConnector.close()


    # Map marvel attributes to official item name
    # Return the mapping
    def mapMarvelItems(self):
        mapping = {}
        self.statsCursor.execute("pragma table_info(marvel_stats)")
        list = self.statsCursor.fetchall()

        for elt in list[2:]: # Skipping id, name
            word = elt[1]
            newWord = word.replace("_", " ")
            newWord = newWord.replace("One", "1")
            newWord = newWord.replace("Hundred Thousand", "100,000")
            newWord = newWord.replace(" Male", " (Male)")
            newWord = newWord.replace(" Female", " (Female)")
            mapping[newWord] = word
        return mapping


    # Map philo attributes to official item name
    # Return the mapping
    def mapPhiloItems(self):
        mapping = {}
        self.statsCursor.execute("pragma table_info(philo_stats)")
        list = self.statsCursor.fetchall()

        for elt in list[2:]: # Skipping id, name
            word = elt[1]
            newWord = word.replace("battle_roid", "battle-roid")
            newWord = newWord.replace("_f_", " (f) ")
            newWord = newWord.replace("_m_", " (m) ")
            newWord = newWord.replace("_", " ")
            mapping[newWord] = word
        return mapping


    # Map bj attributes to prettier text
    # Return the mapping
    def mapBJItems(self):
        mapping = {}
        self.statsCursor.execute("pragma table_info(bj_stats)")
        list = self.statsCursor.fetchall()

        for elt in list[2:]: # Skipping id, name
            word = elt[1]
            newWord = word.replace("_", " ").title()
            mapping[newWord] = word
        return mapping


    # Return list of philo items possible to get from list 1
    def makePhiloList1(self):
        list1 = []
        philoItemList1 = self.philoSheet.col_values(3)
        philoRateList1 = self.philoSheet.col_values(4)

        # Make lists containing the philo items proportionate to their rate
        for i in range(1, len(philoItemList1)):
            # Make the items lowercase for easier matching
            philoItemList1[i] = philoItemList1[i].lower()
            item = philoItemList1[i]
            # Make the %rate an integer with no decimal values
            rate = float(philoRateList1[i][:-1])*100
            # Add the item multiple times proportionate to their rate
            list1 += [item]*int(rate)

        return list1


    # Return list of philo items possible to get from list 2
    def makePhiloList2(self):
        list2 = []
        philoItemList2 = self.philoSheet.col_values(6)
        philoRateList2 = self.philoSheet.col_values(7)

        # Similar to above getPhiloList1()
        for i in range(1, len(philoItemList2)):
            philoItemList2[i] = philoItemList2[i].lower()
            item = philoItemList2[i]
            rate = float(philoRateList2[i][:-1])*100
            list2 += [item]*int(rate)

        return list2


    # Return list of marvel items possible to get from list 1
    def makeMarvelList1(self):
        list1 = []
        marvelItemList1 = self.marvelSheet.col_values(3)
        marvelRateList1 = self.marvelSheet.col_values(4)

        # Similar to philo
        # Note that some item rates from marvel go up to 3 decimal places
        for i in range(1, len(marvelItemList1)):
            marvelItemList1[i] = marvelItemList1[i].lower()
            item = marvelItemList1[i]
            # Accommodate 3 decimal places by *1000
            rate = float(marvelRateList1[i][:-1])*1000
            list1 += [item]*int(rate)

        return list1


    # Return list of marvel items possible to get from list 2
    def makeMarvelList2(self):
        list2 = []
        marvelItemList2 = self.marvelSheet.col_values(6)
        marvelRateList2 = self.marvelSheet.col_values(7)

        for i in range(1, len(marvelItemList2)):
            marvelItemList2[i] = marvelItemList2[i].lower()
            item = marvelItemList2[i]
            rate = float(marvelRateList2[i][:-1])*1000
            list2 += [item]*int(rate)

        return list2


    # Return list of marvel items possible to get from list 3
    def makeMarvelList3(self):
        list3 = []
        marvelItemList3 = self.marvelSheet.col_values(9)
        marvelRateList3 = self.marvelSheet.col_values(10)

        for i in range(1, len(marvelItemList3)):
            marvelItemList3[i] = marvelItemList3[i].lower()
            item = marvelItemList3[i]
            rate = float(marvelRateList3[i][:-1])*1000
            list3 += [item]*int(rate)

        return list3


    # Update user's item stats for philo/marvel
    def updateUserItemStat(self, userName, userID, item, incAmount, strIndicator):
        with self.statsConnector:
            # Update philo item
            if strIndicator == "p":
                self.addNewUser(userName, userID, "p")
                sqlItem = self.philoItemMapping[item]
                self.statsCursor.execute("""UPDATE philo_stats
                                        SET """ + sqlItem + " = IFNULL(" + sqlItem + """, 0) + :amount
                                        WHERE user_id = :id""",
                                        {"amount":incAmount, "id":userID})
                # Update name if needed
                self.statsCursor.execute("""UPDATE philo_stats
                                        SET user_name = :name
                                        WHERE user_id = :id AND user_name <> :name""",
                                        {"id":userID, "name":userName})
            # Update marvel item
            else:
                self.addNewUser(userName, userID, "m")
                sqlItem = self.marvelItemMapping[item]
                self.statsCursor.execute("""UPDATE marvel_stats
                                        SET """ + sqlItem + " = IFNULL(" + sqlItem + """, 0) + :amount
                                        WHERE user_id = :id""",
                                        {"amount":incAmount, "id":userID})
                # Update name if needed
                self.statsCursor.execute("""UPDATE marvel_stats
                                        SET user_name = :name
                                        WHERE user_id = :id AND user_name <> :name""",
                                        {"id":userID, "name":userName})


    # Update user's blackjack stats
    def updateUserBJStat(self, userName, userID, game):
        self.addNewUser(userName, userID, "bj")
        userBetAmount = game.player_bet

        with self.statsConnector:
            # User got blackjack
            if game.player_bj == True:
                self.statsCursor.execute("""UPDATE bj_stats
                                        SET blackjacks = IFNULL(blackjacks, 0) + 1
                                        WHERE user_id = :id""",
                                        {"id":userID})
            # User won
            if game.game_state == 0:
                self.statsCursor.execute("""UPDATE bj_stats
                                        SET games_played = IFNULL(games_played, 0) + 1,
                                        games_won = IFNULL(games_won, 0) + 1,
                                        current_money = IFNULL(current_money, 0) + :bet,
                                        total_earnings = IFNULL(total_earnings, 0) + :bet
                                        WHERE user_id = :id""",
                                        {"bet":userBetAmount, "id":userID})
            # User lost
            elif game.game_state == 1:
                self.statsCursor.execute("""UPDATE bj_stats
                                        SET games_played = IFNULL(games_played, 0) + 1,
                                        games_lost = IFNULL(games_won, 0) + 1,
                                        current_money = IFNULL(current_money, 0) - :bet,
                                        total_earnings = IFNULL(total_earnings, 0) - :bet
                                        WHERE user_id = :id""",
                                        {"bet":userBetAmount, "id":userID})
            # User tied
            elif game.game_state == 2:
                self.statsCursor.execute("""UPDATE bj_stats
                                        SET games_played = IFNULL(games_played, 0) + 1,
                                        games_tied = IFNULL(games_won, 0) + 1
                                        WHERE user_id = :id""",
                                        {"id":userID})
            # Update name if needed
            self.statsCursor.execute("""UPDATE bj_stats
                                    SET user_name = :name
                                    WHERE user_id = :id AND user_name <> :name""",
                                    {"id":userID, "name":userName})


    # Return user's current money
    def getUserMoney(self, userName, userID):
        # Check if data exists
        self.statsCursor.execute("SELECT user_id FROM bj_stats WHERE user_id = :id", {"id":userID})
        if len(self.statsCursor.fetchall()) == 0:
            return 0
        else:
            self.statsCursor.execute("SELECT current_money FROM bj_stats WHERE user_id = :id",
                                    {"id":userID})
            return self.statsCursor.fetchone()[0]


    # Give everyone in blackjack sheet money
    def giveEveryoneMoney(self, amount):
        with self.statsConnector:
            self.statsCursor.execute("UPDATE bj_stats SET current_money = current_money + :amount",
                                {"amount":amount})


    # Calculate philo or marvel spendings
    # Return result through pair
    def pmSpendings(self, numRolls, strIndicator):
        price = -1
        # p for philo, m for marvel
        if strIndicator == "p":
            price = 2.6
        elif strIndicator == "m":
            price = 4.9

        # Calculate and return costs
        low_money = int(numRolls/11)*int(price*10) + (numRolls%11)*price
        high_money = numRolls*price
        return (low_money, high_money)


    # Philo and marvel stats
    # Return result through string
    def pmStats(self, userName, userID):
        self.addNewUser(userName, userID, "m")
        self.addNewUser(userName, userID, "p")
        msg = ""

        # Marvel stats
        self.statsCursor.execute("SELECT rolls FROM marvel_stats WHERE user_id = :id",
                            {"id":userID})
        marvelRolls = self.statsCursor.fetchone()[0]
        costs = self.pmSpendings(marvelRolls, "m")
        low_money = costs[0]
        high_money = costs[1]
        msg += "__{}'s Marvel Machine Statistics:__\nTotal amount of spins: {} ".format(userName.title(), marvelRolls)
        msg += "(${:,.2f} ~ ${:,.2f})\n".format(low_money, high_money)

        self.statsCursor.execute("SELECT * FROM marvel_stats WHERE user_id = :id",
                            {"id":userID})
        userValues = self.statsCursor.fetchone()[3:] # Skip id, name, rolls
        marvelItemRow = [*self.marvelItemMapping][1:] # Skip rolls

        for i in range(0, len(marvelItemRow)):
            item = marvelItemRow[i].title()
            userAmount = userValues[i]
            if userAmount > 0:
                msg += "{}: {:,d}\n".format(item, userAmount)

        # Philo stats
        self.statsCursor.execute("SELECT rolls FROM philo_stats WHERE user_id = :id",
                            {"id":userID})
        philoRolls = self.statsCursor.fetchone()[0]
        costs = self.pmSpendings(philoRolls, "p")
        low_money = costs[0]
        high_money = costs[1]
        msg += "\n__{}'s Philosopher Book Statistics:__\nTotal amount of books: {} ".format(userName.title(), philoRolls)
        msg += "(${:,.2f} ~ ${:,.2f})\n".format(low_money, high_money)

        self.statsCursor.execute("SELECT * FROM philo_stats WHERE user_id = :id",
                            {"id":userID})
        userValues = self.statsCursor.fetchone()[3:] # Skip id, name, rolls
        philoItemRow = [*self.philoItemMapping][1:] # Skip rolls

        for i in range(0, len(philoItemRow)):
            item = philoItemRow[i].title()
            userAmount = userValues[i]
            if userAmount > 0:
                msg += "{}: {:,d}\n".format(item, userAmount)

        return msg


    # Return result through string
    def bjStats(self, userName, userID):
        self.addNewUser(userName, userID, "bj")
        msg = "__{}'s Blackjack Statistics:__\n".format(userName.title())

        # Check if data exists
        self.statsCursor.execute("SELECT user_id FROM bj_stats WHERE user_id = :id", {"id":userID})
        if len(self.statsCursor.fetchall()) == 0:
            msg += "You have not played a game of blackjack yet"
            return msg
        else:
            # Blackjack stats
            self.statsCursor.execute("SELECT * FROM bj_stats WHERE user_id = :id",
                                {"id":userID})
            userValues = self.statsCursor.fetchone()[2:] # Skip id, name
            bjItemRow = [*self.bjItemMapping]

            for i in range(0, len(bjItemRow)):
                item = bjItemRow[i].title()
                userAmount = userValues[i]
                msg += "{}: {:,d}\n".format(item, userAmount)

            return msg


    # Reset user stats for specified data
    # (1) marvel (2) philo (3) blackjack or (4) all
    # Return a string indicating success
    def resetStats(self, userName, userID, statsType):
        # Indicators of which stats to reset
        philoReset = marvelReset = bjReset = False

        if statsType == 4:
            philoReset = marvelReset = bjReset = True
        elif statsType == 3:
            bjReset = True
        elif statsType == 2:
            philoReset = True
        elif statsType == 1:
            marvelReset = True
        else:
            return "Invalid type"

        msg = "**__Attempted to reset {}'s specified stats:__**\n".format(userName.title())
        # Reset desired stats
        if philoReset == True:
            with self.statsConnector:
                self.statsCursor.execute("SELECT user_id FROM philo_stats WHERE user_id = :id", {"id":userID})
                if len(self.statsCursor.fetchall()) == 0:
                    addNewUser(userName, userID, "p")
                    msg += "No philosopher book stats to reset\n"
                else:
                    for var in [*self.philoItemMapping.values()]:
                        self.statsCursor.execute("UPDATE philo_stats SET " + var + " = 0 WHERE user_id = :id",
                                                {"id":userID})
                    msg += "Successfully reset philosopher book stats\n"
        if marvelReset == True:
            with self.statsConnector:
                self.statsCursor.execute("SELECT user_id FROM marvel_stats WHERE user_id = :id", {"id":userID})
                if len(self.statsCursor.fetchall()) == 0:
                    addNewUser(userName, userID, "m")
                    msg += "No marvel machine stats to reset\n"
                else:
                    for var in [*self.marvelItemMapping.values()]:
                        self.statsCursor.execute("UPDATE marvel_stats SET " + var + " = 0 WHERE user_id = :id",
                                                {"id":userID})
                    msg += "Successfully reset marvel machine stats\n"
        if bjReset == True:
            with self.statsConnector:
                self.statsCursor.execute("SELECT user_id FROM bj_stats WHERE user_id = :id", {"id":userID})
                if len(self.statsCursor.fetchall()) == 0:
                    addNewUser(userName, userID, "bj")
                    msg += "No blackjack stats to reset\n"
                else:
                    self.statsCursor.execute("UPDATE bj_stats SET current_money = 100 WHERE user_id = :id",
                                                {"id":userID})
                    for var in [*self.bjItemMapping.values()][1:]: # Skip money
                        self.statsCursor.execute("UPDATE bj_stats SET " + var + " = 0 WHERE user_id = :id",
                                                {"id":userID})
                    msg += "Successfully reset blackjack stats\n"

        return msg[:-1]


    # Add new user to database if not inside already
    # (p) philo (m) marvel (bj) blackjack
    # Idk how to make upsert work...
    def addNewUser(self, userName, userID, strIndicator):
        newUser = str((userID, userName))
        if strIndicator == "p":
            with self.statsConnector:
                self.statsCursor.execute("SELECT user_id FROM philo_stats WHERE user_id = :id", {"id":userID})
                if len(self.statsCursor.fetchall()) == 0:
                    self.statsCursor.execute("INSERT INTO philo_stats(user_id, user_name) VALUES" + newUser)
                    # self.statsCursor.execute("INSERT INTO philo_stats(user_id, user_name) VALUES" + newUser + " ON CONFLICT(user_id) DO UPDATE user_id = user_id")
        elif strIndicator == "m":
            with self.statsConnector:
                self.statsCursor.execute("SELECT user_id FROM marvel_stats WHERE user_id = :id", {"id":userID})
                if len(self.statsCursor.fetchall()) == 0:
                    self.statsCursor.execute("INSERT INTO marvel_stats(user_id, user_name) VALUES" + newUser)
                    # self.statsCursor.execute("INSERT INTO marvel_stats(user_id, user_name) VALUES" + newUser + " ON CONFLICT(user_id) DO UPDATE user_id = user_id")
        elif strIndicator == "bj":
            with self.statsConnector:
                self.statsCursor.execute("SELECT user_id FROM bj_stats WHERE user_id = :id", {"id":userID})
                if len(self.statsCursor.fetchall()) == 0:
                    self.statsCursor.execute("INSERT INTO bj_stats(user_id, user_name) VALUES" + newUser)
                    # self.statsCursor.execute("INSERT INTO bj_stats(user_id, user_name) VALUES" + newUser + " ON CONFLICT(user_id) DO UPDATE user_id = user_id")

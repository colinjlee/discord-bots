import gspread
from oauth2client.service_account import ServiceAccountCredentials
import asyncio

#Google sheets things
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
"https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

class Gamble_Bot_Stats():
    def __init__(self):
        #Google sheets containing user stats
        self.philoStatSheet = client.open("Gamble Bot User Stats").get_worksheet(0)
        self.marvelStatSheet = client.open("Gamble Bot User Stats").get_worksheet(1)
        self.bjStatSheet = client.open("Gamble Bot User Stats").get_worksheet(2)

        #First row containing description of column data
        self.philoItemRow = self.philoStatSheet.row_values(1)
        self.marvelItemRow = self.marvelStatSheet.row_values(1)
        self.bjItemRow = self.bjStatSheet.row_values(1)

        #Google sheets containing public rates of philosopher books and marvel machine
        #Philo rates: http://maplestory.nexon.net/micro-site/42030
        #Marvel rates: http://maplestory.nexon.net/micro-site/39184
        self.philoSheet = client.open("Philosopher Book Rates").worksheets()
        self.philoSheet = self.philoSheet[-1]
        self.marvelSheet = client.open("Marvel Machine Rates").worksheets()
        self.marvelSheet = self.marvelSheet[-1]

        #Mapping of marvel/philo lucky items to their column # on sheets
        self.marvelItemMapping = self.mapMarvelItems()
        self.philoItemMapping = self.mapPhiloItems()

        #List of marvel/philo items to roll from
        self.philoList1 = self.makePhiloList1()
        self.philoList2 = self.makePhiloList2()
        self.marvelList1 = self.makeMarvelList1()
        self.marvelList2 = self.makeMarvelList2()
        self.marvelList3 = self.makeMarvelList3()

        #List of lucky items possible to get in marvel/philo
        self.philoLuckyList = self.makeLuckyList("p")
        self.marvelLuckyList = self.makeLuckyList("m")

        #Align user stats to top row of items
        self.alignUserStats()

    #Token expires after 1 hour
    def checkCreds(self):
        if creds.access_token_expired:
            client.login()

    #Map marvel items to their column # and return the dictionary
    def mapMarvelItems(self):
        mapping = {}
        for i in range(2, len(self.marvelItemRow)):
            mapping[self.marvelItemRow[i]] = i+1

        return mapping

    #Map philo items to their column # and return the dictionary
    def mapPhiloItems(self):
        mapping = {}
        for i in range(2, len(self.philoItemRow)):
            mapping[self.philoItemRow[i]] = i+1

        return mapping

    #Return list of philo items possible to get from list 1
    def makePhiloList1(self):
        list1 = []
        philoItemList1 = self.philoSheet.col_values(3)
        philoRateList1 = self.philoSheet.col_values(4)

        #Make lists containing the philo items proportionate to their rate
        for i in range(1, len(philoItemList1)):
            #Make the items lowercase for easier matching
            philoItemList1[i] = philoItemList1[i].lower()
            item = philoItemList1[i]
            #Make the %rate an integer with no decimal values
            rate = float(philoRateList1[i][:-1])*100
            #Add the item multiple times proportionate to their rate
            list1 += [item]*int(rate)

        return list1

    #Return list of philo items possible to get from list 2
    def makePhiloList2(self):
        list2 = []
        philoItemList2 = self.philoSheet.col_values(6)
        philoRateList2 = self.philoSheet.col_values(7)

        #Similar to above getPhiloList1()
        for i in range(1, len(philoItemList2)):
            philoItemList2[i] = philoItemList2[i].lower()
            item = philoItemList2[i]
            rate = float(philoRateList2[i][:-1])*100
            list2 += [item]*int(rate)

        return list2

    #Return list of marvel items possible to get from list 1
    def makeMarvelList1(self):
        list1 = []
        marvelItemList1 = self.marvelSheet.col_values(3)
        marvelRateList1 = self.marvelSheet.col_values(4)

        #Similar to philo
        #Note that some item rates from marvel go up to 3 decimal places
        for i in range(1, len(marvelItemList1)):
            marvelItemList1[i] = marvelItemList1[i].lower()
            item = marvelItemList1[i]
            #Accommodate 3 decimal places by *1000
            rate = float(marvelRateList1[i][:-1])*1000
            list1 += [item]*int(rate)

        return list1

    #Return list of marvel items possible to get from list 2
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

    #Return list of marvel items possible to get from list 3
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

    #Make a dictionary of lucky items for (0) philo or (1) marvel
    def makeLuckyList(self, strIndicator):
        luckyList = {}
        if strIndicator == "p":
            #Start from 3 to skip name, id, and #rolls column
            for i in range(3, len(self.philoItemRow)):
                item = self.philoItemRow[i]
                luckyList[item] = 0
        else:
            #Start from 3 to skip name, id, and #rolls column
            for i in range(3, len(self.marvelItemRow)):
                item = self.marvelItemRow[i]
                luckyList[item] = 0

        return luckyList

    #Aligns the user's stats to match the first row of items
    def alignUserStats(self):
        #Make sure user stats align with top row, if not then add 0s for new data
        philoUsersList = self.philoStatSheet.col_values(2)
        marvelUsersList = self.marvelStatSheet.col_values(2)
        bjUsersList = self.bjStatSheet.col_values(2)

        #Lengths of first rows, the descriptions
        philoLength = len(self.philoItemRow)
        marvelLength = len(self.marvelItemRow)
        bjLength = len(self.bjItemRow)

        #Make user stats in line with philo items
        for i in range(1, len(philoUsersList)):
            userLength = len(self.philoStatSheet.row_values(i+1))
            if userLength < philoLength:
                for j in range(userLength+1, philoLength+1):
                    self.philoStatSheet.update_cell(i+1, j, 0)
            elif userLength > philoLength:
                for j in range(philoLength+1, userLength+1):
                    self.philoStatSheet.update_cell(i+1, j, "")

        #Make user stats in line with marvel items
        for i in range(1, len(marvelUsersList)):
            userLength = len(self.marvelStatSheet.row_values(i+1))
            if userLength < marvelLength:
                for j in range(userLength+1, marvelLength+1):
                    self.marvelStatSheet.update_cell(i+1, j, 0)
            elif userLength > marvelLength:
                for j in range(marvelLength+1, userLength+1):
                    self.marvelStatSheet.update_cell(i+1, j, "")

        #Make user stats in line with bj items
        for i in range(1, len(bjUsersList)):
            userLength = len(self.bjStatSheet.row_values(i+1))
            if userLength < bjLength:
                for j in range(userLength+1, bjLength+1):
                    self.bjStatSheet.update_cell(i+1, j, 0)
            elif userLength > bjLength:
                for j in range(bjLength+1, userLength+1):
                    self.bjStatSheet.update_cell(i+1, j, "")

    #Get user's row that has their stats for specified stat sheet
    #Initialize them if user doesn't exist in data
    #Return the row number as int
    def getUserRow(self, userName, userID, strIndicator):
        #Get list of user IDs and search for userID
        if strIndicator == "p":
            userIDList = self.philoStatSheet.col_values(2)
            itemRowLength = len(self.philoItemRow)
        elif strIndicator == "m":
            userIDList = self.marvelStatSheet.col_values(2)
            itemRowLength = len(self.marvelItemRow)
        elif strIndicator == "bj":
            userIDList = self.bjStatSheet.col_values(2)
            itemRowLength = len(self.bjItemRow)
        userRow = -1

        #Data is currently not sorted in any way so just linear search
        for i in range(0, len(userIDList)):
            if userID == userIDList[i]:
                userRow = i+1

        #Philo: Update name if different from last time
        if userRow != -1:
            #Get user stats
            if strIndicator == "p":
                userStats = self.philoStatSheet.row_values(userRow)
            elif strIndicator == "m":
                userStats = self.marvelStatSheet.row_values(userRow)
            elif strIndicator == "bj":
                userStats = self.bjStatSheet.row_values(userRow)

            #Compare names
            if userName != userStats[0]:
                if strIndicator == "p":
                    self.philoStatSheet.update_cell(1,userRow, userName)
                elif strIndicator == "m":
                    self.marvelStatSheet.update_cell(1,userRow, userName)
                elif strIndicator == "bj":
                    self.bjStatSheet.update_cell(1,userRow, userName)
        #Add a new row for the new user
        else:
            newUser = [userName, userID]
            if strIndicator == "bj":
                newUser += [100] #Starting money
                newUser += [0]*(itemRowLength-3)
            else:
                newUser += [0]*(itemRowLength-2)
            if strIndicator == "p":
                self.philoStatSheet.append_row(newUser)
            elif strIndicator == "m":
                self.marvelStatSheet.append_row(newUser)
            elif strIndicator == "bj":
                self.bjStatSheet.append_row(newUser)
            userRow = len(userIDList)+1

        return userRow

    #Update user's item stats for philo/marvel
    def updateUserItemStat(self, userRow, item, incAmount, strIndicator):
        #Update philo item
        if strIndicator == "p":
            itemLoc = self.philoItemMapping[item]
            oldVal = int(self.philoStatSheet.cell(userRow, itemLoc).value)
            self.philoStatSheet.update_cell(userRow, itemLoc, oldVal+incAmount)
        #Update marvel item
        else:
            itemLoc = self.marvelItemMapping[item]
            oldVal = int(self.marvelStatSheet.cell(userRow, itemLoc).value)
            self.marvelStatSheet.update_cell(userRow, itemLoc, oldVal+incAmount)

    #Update user's blackjack stats
    #Hard coded column location values...
    def updateUserBJStat(self, userName, userID, game):
        userRow = self.getUserRow(userName, userID, "bj")
        userMoney = int(self.bjStatSheet.cell(userRow, 3).value)
        userEarnings = int(self.bjStatSheet.cell(userRow, 4).value)
        userGamesPlayed = int(self.bjStatSheet.cell(userRow, 6).value)
        userBetAmount = game.player_bet

        #User got blackjack
        if game.player_bj == True:
            userBlackjacks = int(self.bjStatSheet.cell(userRow, 5).value)
            self.bjStatSheet.update_cell(userRow, 5, userBlackjacks+1)
        #User won
        if game.game_state == 0:
            userGamesWon = int(self.bjStatSheet.cell(userRow, 7).value)
            if userBetAmount > 0:
                self.bjStatSheet.update_cell(userRow, 3, userMoney+userBetAmount)
                self.bjStatSheet.update_cell(userRow, 4, userEarnings+userBetAmount)
            self.bjStatSheet.update_cell(userRow, 6, userGamesPlayed+1)
            self.bjStatSheet.update_cell(userRow, 7, userGamesWon+1)
        #User lost
        if game.game_state == 1:
            userGamesLost = int(self.bjStatSheet.cell(userRow, 8).value)
            if userBetAmount > 0:
                self.bjStatSheet.update_cell(userRow, 3, userMoney-userBetAmount)
                self.bjStatSheet.update_cell(userRow, 4, userEarnings-userBetAmount)
            self.bjStatSheet.update_cell(userRow, 6, userGamesPlayed+1)
            self.bjStatSheet.update_cell(userRow, 8, userGamesLost+1)
        #User tied
        if game.game_state == 2:
            userGamesTied = int(self.bjStatSheet.cell(userRow, 9).value)
            self.bjStatSheet.update_cell(userRow, 6, userGamesPlayed+1)
            self.bjStatSheet.update_cell(userRow, 9, userGamesTied+1)

    #Return user's money
    def getUserMoney(self, userName, userID):
        userRow = self.getUserRow(userName, userID, "bj")
        return int(self.bjStatSheet.cell(userRow, 3).value)

    #Give everyone in blackjack sheet money
    def giveEveryoneMoney(self, amount):
        moneyList = self.bjStatSheet.col_values(3)

        for i in range(1, len(moneyList)):
            oldVal = int(self.bjStatSheet.cell(i+1, 3).value)
            self.bjStatSheet.update_cell(i+1, 3, oldVal+amount)

    #Calculate philo or marvel spendings
    #Return result through pair
    def pmSpendings(self, numRolls, strIndicator):
        price = -1
        #0 for philo, 1 for marvel
        if strIndicator == "p":
            price = 2.6
        elif strIndicator == "m":
            price = 4.9

        #Calculate and return costs
        low_money = int(numRolls/11)*int(price*10) + (numRolls%11)*price
        high_money = numRolls*price
        return (low_money, high_money)

    #Philo and marvel stats
    #Return result through string
    def pmStats(self, userName, userID):
        #Retrieve user stats and update userName if necessary
        userRowPhilo = self.getUserRow(userName, userID, "p")
        userRowMarvel = self.getUserRow(userName, userID, "m")
        userStatsPhilo = self.philoStatSheet.row_values(userRowPhilo)
        userStatsMarvel = self.marvelStatSheet.row_values(userRowMarvel)
        msg = "**__" + userName.title() + "\'s marvel and philo stats:__**\n\n"

        #Currently hard coded values of cell locations for marvel/philo
        #Marvel stats
        marvelRolls = int(userStatsMarvel[2])
        costs = self.pmSpendings(marvelRolls, 1)
        low_money = costs[0]
        high_money = costs[1]
        msg += "**__Marvel Machine Statistics:__**\nTotal amount of spins: {} ".format(marvelRolls)
        msg += "(${:,.2f} ~ ${:,.2f})\n".format(low_money, high_money)

        for i in range(3, len(self.marvelItemRow)):
            item = self.marvelItemRow[i].title()
            userAmount = int(userStatsMarvel[i])
            if userAmount > 0:
                msg += "{}: {:,d}\n".format(item, userAmount)

        #Philo stats
        philoRolls = int(userStatsPhilo[2])
        costs = self.pmSpendings(philoRolls, 0)
        low_money = costs[0]
        high_money = costs[1]
        msg += "\n**__Philosopher Book Statistics:__**\nTotal amount of books: {} ".format(philoRolls)
        msg += "(${:,.2f} ~ ${:,.2f})\n".format(low_money, high_money)

        for i in range(3, len(self.philoItemRow)):
            item = self.philoItemRow[i].title()
            userAmount = int(userStatsPhilo[i])
            if userAmount > 0:
                msg += "{}: {:,d}\n".format(item, userAmount)

        return msg

    #Return result through string
    def bjStats(self, userName, userID):
        userRowBJ = self.getUserRow(userName, userID, "bj")
        userStatsBJ = self.bjStatSheet.row_values(userRowBJ)
        msg = "**__" + userName.title() + "\'s blackjack stats:__**\n"

        #Currently hard coded values of cell locations for blackjack
        for i in range(2, len(self.bjItemRow)):
            item = self.bjItemRow[i].title()
            userAmount = int(userStatsBJ[i])
            msg += "{}: {:,d}\n".format(item, userAmount)

        return msg

    #Reset user stats for specified data
    #(1) philo (2) marvel (3) blackjack or (4) all
    #Return a string indicating success
    def resetStats(self, userName, userID, statsType):
        #Indicators of which stats to reset
        philoReset = marvelReset = bjReset = False

        if statsType == 4:
            philoReset = marvelReset = bjReset = True
        elif statsType == 3:
            bjReset = True
        elif statsType == 2:
            marvelReset = True
        elif statsType == 1:
            philoReset = True
        else:
            return "Invalid type"

        msg = ""
        #Reset desired stats, currently deletes entire row and adds new one
        if philoReset == True:
            userRow = self.getUserRow(userName, userID, "p")
            userNew = [userName, userID]
            userNew += [0] * int(len(self.philoItemRow)-2)
            self.philoStatSheet.delete_row(userRow)
            self.philoStatSheet.append_row(userNew)
            msg += "Successfully reset philosopher book stats\n"
        if marvelReset == True:
            userRow = self.getUserRow(userName, userID, "m")
            userNew = [userName, userID]
            userNew += [0] * int(len(self.marvelItemRow)-2)
            self.marvelStatSheet.delete_row(userRow)
            self.marvelStatSheet.append_row(userNew)
            msg += "Successfully reset marvel machine stats\n"
        if bjReset == True:
            userRow = self.getUserRow(userName, userID, "bj")
            userNew = [userName, userID, 100]
            userNew += [0] * int(len(self.bjItemRow)-3)
            self.bjStatSheet.delete_row(userRow)
            self.bjStatSheet.append_row(userNew)
            msg += "Successfully reset blackjack stats\n"

        return msg

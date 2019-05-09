import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

#Google sheets things
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

#Google sheets containing user marvel/philo stats
philoStatSheet = client.open("Gamble Bot User Stats").get_worksheet(0)
philoItemRow = philoStatSheet.row_values(1)
marvelStatSheet = client.open("Gamble Bot User Stats").get_worksheet(1)
marvelItemRow = marvelStatSheet.row_values(1)

#Make a mapping for marvel and philo items to column number
marvelItemMapping = {}
for i in range(2, len(marvelItemRow)):
    marvelItemMapping[marvelItemRow[i]] = i+1

philoItemMapping = {}
for i in range(2, len(philoItemRow)):
    philoItemMapping[philoItemRow[i]] = i+1

#Google sheets containing user blackjack stats
#statSheet2 = client.open("Gamble Bot User Stats").get_worksheet(3)

#Google sheets containing public rates of philosopher books and marvel machine
#Philo rates: http://maplestory.nexon.net/micro-site/42030
#Marvel rates: http://maplestory.nexon.net/micro-site/39184
philoSheet = client.open("Philosopher Book Rates").worksheets()
philoSheet = philoSheet[-1]
marvelSheet = client.open("Marvel Machine Rates").worksheets()
marvelSheet = marvelSheet[-1]

#Get the 2 lists to roll from for philo book items
philoList1 = []
philoList2 = []

philoItemList1 = philoSheet.col_values(3)
philoItemList2 = philoSheet.col_values(6)
philoRateList1 = philoSheet.col_values(4)
philoRateList2 = philoSheet.col_values(7)

#Make lists containing the items proportionate to their rate
for i in range(1, len(philoItemList1)):
    #Make the items lowercase for easier matching
    philoItemList1[i] = philoItemList1[i].lower()
    item = philoItemList1[i]
    #Make the %rate an integer with no decimal values
    rate = float(philoRateList1[i][:-1])*100
    #Add the item multiple times proportionate to their rate
    philoList1 += [item]*int(rate)

#Same as above for the 2nd list of items
for i in range(1, len(philoItemList2)):
    philoItemList2[i] = philoItemList2[i].lower()
    item = philoItemList2[i]
    rate = float(philoRateList2[i][:-1])*100
    philoList2 += [item]*int(rate)

#Similar procedure as above but for marvel items
marvelList1 = []
marvelList2 = []
marvelList3 = []

marvelItemList1 = marvelSheet.col_values(3)
marvelItemList2 = marvelSheet.col_values(6)
marvelItemList3 = marvelSheet.col_values(9)
marvelRateList1 = marvelSheet.col_values(4)
marvelRateList2 = marvelSheet.col_values(7)
marvelRateList3 = marvelSheet.col_values(10)

#Note that some item rates from list 1 and 2 of marvel go up to 3 decimal places
for i in range(1, len(marvelItemList1)):
    marvelItemList1[i] = marvelItemList1[i].lower()
    item = marvelItemList1[i]
    rate = float(marvelRateList1[i][:-1])*1000
    marvelList1 += [item]*int(rate)

for i in range(1, len(marvelItemList2)):
    marvelItemList2[i] = marvelItemList2[i].lower()
    item = marvelItemList2[i]
    rate = float(marvelRateList2[i][:-1])*1000
    marvelList2 += [item]*int(rate)

for i in range(1, len(marvelItemList3)):
    marvelItemList3[i] = marvelItemList3[i].lower()
    item = marvelItemList3[i]
    rate = float(marvelRateList3[i][:-1])*1000
    marvelList3 += [item]*int(rate)

#Calculate philo or marvel spendings
#Return result through pair
def pmSpendings(numRolls, numIndicator):
    price = -1
    #0 for philo, 1 for marvel
    if numIndicator == 0:
        price = 2.6
    elif numIndicator == 1:
        price = 4.9

    #Calculate and return costs
    low_money = int(numRolls/11)*int(price*10) + (numRolls%11)*price
    high_money = numRolls*price
    return (low_money, high_money)

#Get user's row that has their stats, or initialize them if user doesn't exist in data
#Return the row numbers as a pair, first being philo stats then marvel
def getUserRow(userName, userID):
    global marvelStatSheet, philoStatSheet, philoItemRow, marvelItemRow
    #Get list of user IDs and search for userID
    userIDList1 = philoStatSheet.col_values(2)
    userIDList2 = marvelStatSheet.col_values(2)
    userRow1 = -1
    userRow2 = -1

    #Data is currently not sorted in any way so just linear search
    for i in range(0, len(userIDList1)):
        if userID == userIDList1[i]:
            userRow1 = i+1

    for i in range(0, len(userIDList2)):
        if userID == userIDList2[i]:
            userRow2 = i+1

    #Update name if different from last time
    if userRow1 != -1:
        userStats = philoStatSheet.row_values(userRow1)
        if userName != userStats[0]:
            philoStatSheet.update_cell(1,userRow1, userName)
    #Add a new row for the new user in philo stats
    else:
        newUser = [userName, userID]
        newUser += ["0"]*(len(philoItemRow)-2)
        philoStatSheet.append_row(newUser)
        userRow1 = len(userIDList1)+1
    #Update name if different from last time
    if userRow2 != -1:
        userStats = marvelStatSheet.row_values(userRow2)
        if userName != userStats[0]:
            marvelStatSheet.update_cell(1,userRow2, userName)
    #Add a new row for the new user in marvel stats
    else:
        newUser = [userName, userID]
        newUser += ["0"]*(len(marvelItemRow)-2)
        marvelStatSheet.append_row(newUser)
        userRow2 = len(userIDList2)+1

    return (userRow1, userRow2)

#Update user's item stats for philo/marvel
def updateUserItemStat(userRow, item, incAmount, numIndicator):
    global philoStatSheet, marvelStatSheet, philoItemMapping, marvelItemMapping

    #Update philo item
    if numIndicator == 0:
        itemLoc = philoItemMapping[item]
        oldVal = int(philoStatSheet.cell(userRow, itemLoc).value)
        philoStatSheet.update_cell(userRow, itemLoc, str(oldVal+incAmount))
    #Update marvel item
    else:
        itemLoc = marvelItemMapping[item]
        oldVal = int(marvelStatSheet.cell(userRow, itemLoc).value)
        marvelStatSheet.update_cell(userRow, itemLoc, str(oldVal+incAmount))

#Philo and marvel stats
#Return result through string
def pmStats(userName, userID):
    global philoStatSheet, marvelStatSheet, philoItemRow, marvelItemRow

    #Retrieve user stats and update userName if necessary
    userRows = getUserRow(userName, userID)
    userRowPhilo = userRows[0]
    userRowMarvel = userRows[1]
    userStatsPhilo = philoStatSheet.row_values(userRowPhilo)
    userStatsMarvel = marvelStatSheet.row_values(userRowMarvel)
    msg = "**__" + userName + "\'s marvel and philo stats__**\n\n"

    #Currently hard coded values of cell locations for marvel/philo
    #Philo stats
    philoRolls = int(userStatsPhilo[2])
    costs = pmSpendings(philoRolls, 0)
    low_money = costs[0]
    high_money = costs[1]
    msg += "**__Philosopher Book Statistics:__**\nTotal amount of books: {} ".format(philoRolls)
    msg += "(${:,.2f} ~ ${:,.2f})\n".format(low_money, high_money)

    for i in range(3, len(philoItemRow)):
        item = philoItemRow[i].title()
        userAmount = int(userStatsPhilo[i])
        if userAmount > 0:
            msg += "{}: {:,d}\n".format(item, userAmount)

    #Marvel stats
    marvelRolls = int(userStatsMarvel[2])
    costs = pmSpendings(marvelRolls, 1)
    low_money = costs[0]
    high_money = costs[1]
    msg += "\n**__Marvel Machine Statistics:__**\nTotal amount of spins: {} ".format(marvelRolls)
    msg += "(${:,.2f} ~ ${:,.2f})\n".format(low_money, high_money)

    for i in range(3, len(marvelItemRow)):
        item = marvelItemRow[i].title()
        userAmount = int(userStatsMarvel[i])
        if userAmount > 0:
            msg += "{}: {:,d}\n".format(item, userAmount)

    return msg

#TODO: Blackjack stats
#Return result through string
def bjStats(userName, userID):
    return("TODO")

#TODO: reset stats
#Return a string indicating success
def resetStats(userName, userID, statsType):
    return("TODO")

#Returns a string of the notable items won from philo or marvel
def notableItems(luckyList, gotLucky):
    if gotLucky == True:
        msg = "\n**__Notable items:__**\n"
        for item in luckyList:
            if luckyList[item] > 0:
                msg += item.title() + ": " + str(luckyList[item]) + "\n"
    else:
        msg = "\n**__No notable items__**"
    return msg

#Roll a specified number of philosopher books, up to 165
#Return the results through an array
def philoRoll(userName, userID, numRolls):
    global philoList1, philoList2

    #Lucky items in philo
    lucky = {"battle-roid (f) coupon":0, "battle-roid (m) coupon":0, "outlaw heart":0, "frenzy totem":0, "firestarter ring coupon":0, "wolf underling familiar":0}
    gotLucky = False
    messages = []
    msg = ""

    #Get user info to record stats
    userRow = getUserRow(userName, userID)[0]

    #Min roll of 1, max of 165 rolls
    if numRolls < 1:
        messages.append("Amount of rolls must be positive")
        return messages
    elif numRolls > 165:
        msg += "**Max of 165 philo books (15 packs)**\n"
        numRolls = 165

    #Roll the specified amount of books
    for i in range(0, numRolls):
        temp = "**[" + str(i+1) + "]** "
        item1 = random.choice(philoList1)
        item2 = random.choice(philoList2)
        #Discord syntax to bold and underline lucky items
        if item1 in lucky:
            temp += "**__" + item1.title() + "__**, "
            lucky[item1] += 1
            updateUserItemStat(userRow, item1, 1, 0)
            gotLucky = True
        else:
            temp += item1.title() + ", "
        if item2 in lucky:
            temp += "**__" + item2.title() + "__** "
            lucky[item2] += 1
            updateUserItemStat(userRow, item2, 1, 0)
            gotLucky = True
        else:
            temp += item2.title() + " "
        #Check for bot message length limit of 2,000 chars
        if len(msg) + len(temp) > 2000:
            messages.append(msg)
            msg = temp
        else:
            msg += temp

    #Highlight lucky items and update user stat
    temp = notableItems(lucky, gotLucky)
    updateUserItemStat(userRow, "rolls", numRolls, 0)

    #Another final check for message length limit
    if len(msg) + len(temp) > 2000:
        messages.append(msg)
        msg = temp
    else:
        msg += temp
    messages.append(msg)
    return messages

#Roll philo books until the specified item is found
#These rolls are not recorded in stats
#Return the results through a string
def philoFind(item):
    global philoList1, philoList2
    counter = 0
    found = False
    item = item.strip().lower()

    #Roll until item is found
    if item in philoList1 or item in philoList2:
        while found == False:
            counter += 1
            if item in philoList1:
                result = random.choice(philoList1)
            else:
                result = random.choice(philoList2)
            if item == result:
                found = True
    else:
        return "Invalid item"

    #Calculate spending costs and return results
    costs = pmSpendings(counter, 0)
    low_money = costs[0]
    high_money = costs[1]
    msg = "It took {:,d} book(s) to get the item: ".format(counter) + item.title() + "\n"
    msg += "{:,d} book(s) = ${:,.2f} ~ ${:,.2f}".format(counter, low_money, high_money)
    return msg

#Roll marvel a specified number of times, up to 110
#Return the results through an array
def marvelRoll(userName, userID, numRolls):
    global marvelList1, marvelList2, marvelList3

    #Lucky items in marvel
    lucky = {"1 mil maple points":0, "frenzy totem":0, "dark avenger totem":0, "dark doom totem":0, "dark grin totem":0, "dark hellia totem":0,
    "lucid's earrings coupon":0, "firestarter ring":0, "the ring of torment coupon":0, "permanent pendant slot":0, "permanent hyper teleport rock coupon":0,
    "battleroid (male)":0, "battleroid (female)":0, "outlaw heart":0, "100,000 maple points chip":0, "wolf underling familiar":0}
    gotLucky = False
    messages = []
    msg = ""

    #Get user info to record stats
    userRow = getUserRow(userName, userID)[1]

    #Min roll of 1, max roll of 110
    if numRolls < 1:
        messages.append("Amount of rolls must be positive")
        return messages
    elif numRolls > 110:
        msg += "**Max of 110 marvel spins (10 packs)**\n"
        numRolls = 110

    #Roll the specified amount
    for i in range(0, numRolls):
        temp = "**[" + str(i+1) + "]** "
        itemA = random.choice(marvelList1)
        itemB = random.choice(marvelList2)
        itemC = random.choice(marvelList3)
        #Discord syntax to bold and underline lucky items
        if itemA in lucky:
            temp += "**__" + itemA.title() + "__**, "
            lucky[itemA] += 1
            updateUserItemStat(userRow, itemA, 1, 1)
            gotLucky = True
        else:
            temp += itemA.title() + ", "
        if itemB in lucky:
            temp += "**__" + itemB.title() + "__**, "
            lucky[itemB] += 1
            updateUserItemStat(userRow, itemB, 1, 1)
            gotLucky = True
        else:
            temp += itemB.title() + ", "
        if itemC in lucky:
            temp += "**__" + itemC.title() + "__** "
            lucky[itemC] += 1
            updateUserItemStat(userRow, itemC, 1, 1)
            gotLucky = True
        else:
            temp += itemC.title() + " "
        #Check for bot message length limit of 2,000 chars
        if len(msg) + len(temp) > 2000:
            messages.append(msg)
            msg = temp
        else:
            msg += temp

    #Highlight lucky items and update user stats
    temp = notableItems(lucky, gotLucky)
    updateUserItemStat(userRow, "rolls", numRolls, 1)

    #Another final check for message length limit
    if len(msg) + len(temp) > 2000:
        messages.append(msg)
        msg = temp
    else:
        msg += temp
    messages.append(msg)
    return messages

#Roll marvel until the specified item is found
#These rolls are not recorded in stats
#Return results through a string
def marvelFind(item):
    global marvelList1, marvelList2, marvelList3
    counter = 0
    found = False
    item = item.strip().lower()

    #Roll until item is found
    if item in marvelList1 or item in marvelList2 or item in marvelList3:
        while found == False:
            counter += 1
            if item in marvelList1:
                result = random.choice(marvelList1)
            elif item in marvelList2:
                result = random.choice(marvelList2)
            else:
                result = random.choice(marvelList3)
            if item == result:
                found = True
    else:
        return "Invalid item"

    #Calculate spending costs and return results
    costs = pmSpendings(counter, 1)
    low_money = costs[0]
    high_money = costs[1]
    msg = "It took {:,d} spin(s) to get the item: ".format(counter) + item.title() + "\n"
    msg += "{:,d} spin(s) = ${:,.2f} ~ ${:,.2f}".format(counter, low_money, high_money)
    return msg

#Roll a die with specified number of sides, a specified number of times
#Return the results through an array
def roll(numRolls, numSides):
    results = [0] * numSides

    for x in range(0, numRolls):
        rand = random.randint(1, numSides)
        results[rand-1] += 1

    return results

#Flip a coin the specified number of times
#Return the results through a string
def flip(numFlips):
    #Amount of flips must be positive
    if numFlips < 1:
        return "Amount of rolls must be positive or empty to use default value"
    #Flip just once
    elif numFlips == 1:
        rand = random.randint(0,1)
        if rand == 0:
            return "Heads"
        else:
            return "Tails"
    #Different message format for flipping more than once
    else:
        #String to be sent after results
        msg = ""
        if numFlips > 100000:
            msg += "**Max of 100,000 flips**\n"
            numFlips = 100000

        #Get and send results
        results = roll(numFlips, 2)
        head = results[0]
        tail = results[1]
        hRate = head/numFlips*100
        tRate = tail/numFlips*100

        msg += "Heads: {:,d} ({:.2f}%)\nTails: {:,d} ({:.2f}%)"
        return msg.format(head, hRate, tail, tRate)

#Flip a coin with an initial guess
#Return the results through a string
def flipGuess(guess):
    #Set of acceptable string values for guess
    allowedGuesses = {"head", "heads", "h", "tail", "tails", "t"}
    guess = guess.strip() #Remove leading and trailing whitespace
    guess = guess.lower() #make all letters lowercase
    msg = "You guessed {} and it flipped {}\n"
    result = ""

    #Valid guess
    if guess in allowedGuesses:
        rand = random.randint(0,1)
        if guess.startswith("h"):
            guess = "heads"
        else:
            guess = "tails"

        if rand == 0:
            result = "heads"
        else:
            result = "tails"

        if guess == result:
            msg += "You were **right**"
        else:
            msg += "You were **wrong**"

        return msg.format(guess, result)
    #Invalid guess
    else:
        return "Invalid guess. Try again with a guess of 'h' or 't'"

#Roll a die with specified number of sides, a specified number of times
#Return the results through an array due to bot message length
def rollDie(numRolls, numSides):
    #array of results to be sent
    messages = []
    #Amount of flips and face count must be positive
    if numRolls < 1 or numSides < 1:
        messages.append("Amount of rolls and die side count must be positive or empty to use default values")
    #Roll just once
    elif numRolls == 1:
        rand = random.randint(1,numSides)
        messages.append(rand)
    #Different message format for rolling more than once
    else:
        #String of results to be sent
        msg = ""
        if numSides > 100:
            msg += "**Max of 100 sided die**\n"
            numSides = 100
        if numRolls > 100000:
            msg += "**Max of 100,000 rolls**\n"
            numRolls = 100000

        #Get and send results. Note bots have max length of 2,000 chars per msg
        results = roll(numRolls, numSides)
        for x in range(0, numSides):
            if results[x] > 0:
                res = "{:,d}: {:,d} ({:.2f}%)\n".format(x+1, results[x], (results[x]/numRolls*100))
                if len(msg) + len(res) > 2000:
                    messages.append(msg)
                    msg = res
                else:
                    msg += res
        messages.append(msg)
    return messages

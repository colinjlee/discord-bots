import random
import blackjack
import asyncio
import gamble_bot_stats

#Things to do with stats on sheets
stats = gamble_bot_stats.Gamble_Bot_Stats()

#Check gspread creds
def checkCreds():
    stats.checkCreds()

#Dictionary mapping unique user ID to a blackjack game
bjGames = {}

#Starforcing stuff
normal_sf_succ = [0.95, 0.90, 0.85, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.45,
0.35, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.03, 0.02, 0.01]

destroy_sf_succ = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.007, 0.014, 0.014, 0.021,
0.021, 0.021, 0.028, 0.028, 0.07, 0.07, 0.194, 0.294, 0.396]

keep_if_fail = {0, 1, 2, 3, 4, 5, 10, 15, 20}

#Calculate meso cost and boom count for starforcing from 0 up to specified star
#Return pair for meso cost and number of times the item boomed
async def starforceCost(startStar, endStar, itemLevel):
    global normal_sf_succ, destroy_sf_succ, keep_if_fail

    numFailed = 0
    numBoomed = 0
    mesoCost = 0
    currStar = startStar

    #Start starforcing
    while currStar < endStar:
        #Avoid crashing...stop at 250tril
        if mesoCost >= 250000000000000:
            return (mesoCost, numBoomed, -1)
        #Calculate meso cost
        #Formula for 0 to 10 stars is specifically for lvl 150 items since idk general one
        #But cost of 0 to 10 is relatively low/negligible compared to 10+
        if currStar < 10:
            mesoCost += (136000 * (currStar + 1)) - (1000 * currStar)
        elif currStar < 15:
            mesoCost += 1000 + (itemLevel)**3 * (currStar + 1)**2.7 / 400
        elif currStar < 18:
            mesoCost += 1000 + (itemLevel)**3 * (currStar + 1)**2.7 / 120
        elif currStar < 20:
            mesoCost += 1000 + (itemLevel)**3 * (currStar + 1)**2.7 / 110
        else:
            mesoCost += 1000 + (itemLevel)**3 * (currStar + 1)**2.7 / 100

        boom_if_greater = 1-destroy_sf_succ[currStar]
        succAttempt = random.uniform(0,1)
        #Failed twice in a row, 100% for next star
        if numFailed == 2:
            currStar += 1
            numFailed = 0
        #Success
        elif succAttempt < normal_sf_succ[currStar]:
            currStar += 1
            numFailed = 0
        #Fail, no boom
        elif succAttempt < boom_if_greater:
            #Keep current star or not
            if not currStar in keep_if_fail:
                currStar -= 1
                numFailed += 1
            else:
                numFailed = 0
        #Boom
        else:
            currStar = 0
            numFailed = 0
            numBoomed += 1
        await asyncio.sleep(0.01)

    return (mesoCost, numBoomed, 1)

#String message for starforcing
async def starforceMessage(startStar, endStar, itemLevel):
    msg = ""

    #Check legitimate starting star number
    if startStar < 0:
        #msg += "Starting star value must be non-negative\n"
        startStar = 0

    #Check item level correspondence with max star count
    if itemLevel < 95 and endStar > 5:
        msg += "**__Max number of stars for an item of level {} is 5__**\n".format(itemLevel)
        endStar = 5
    elif itemLevel < 108 and endStar > 8:
        msg += "**__Max number of stars for an item of level {} is 8__**\n".format(itemLevel)
        endStar = 8
    elif itemLevel < 118 and endStar > 10:
        msg += "**__Max number of stars for an item of level {} is 10__**\n".format(itemLevel)
        endStar = 10
    elif itemLevel < 128 and endStar > 15:
        msg += "**__Max number of stars for an item of level {} is 15__**\n".format(itemLevel)
        endStar = 15
    elif itemLevel < 138 and endStar > 20:
        msg += "**__Max number of stars for an item of level {} is 20__**\n".format(itemLevel)
        endStar = 20
    else:
        #Check legitimate ending star number
        if endStar > 25:
            msg += "**__Max number of stars for an item of level {} is 25__**\n".format(itemLevel)
            endStar = 25

    #Check if anything to starforce
    if startStar > 24 or startStar >= endStar:
        return "Nothing more to starforce"

    info = await starforceCost(startStar, endStar, itemLevel)
    mesoCost = info[0]
    numBoomed = info[1]

    suf = ""
    #Trillion
    if mesoCost >= 1000000000000:
        suf = "(trillion)"
    #Billion
    elif mesoCost >= 1000000000:
        suf = "(billion)"
    #Million
    elif mesoCost >= 1000000:
        suf = "(million)"

    if info[2] < 0:
        msg += "**Note: Computation stopped early**\n"
    else:
        msg += "__Your stats to go from {} to {} star on a level {} item:__\n".format(startStar, endStar, itemLevel)
    msg += "Meso cost: {:,.0f} ".format(mesoCost) + suf + "\n"
    msg += "Boom count: {:,.0f}\n".format(numBoomed)
    return msg

#Start a blackjack game for the user
def bj(userName, userID, betAmount):
    global bjGames

    if userID in bjGames:
        msg = "**__You're already in a game!__**\n"
        msg += bjGames[userID].__str__()
        return (msg, bjGames[userID])
    else:
        if betAmount < 0:
            betAmount = 0

        #Make sure player has enough money to bet
        userMoney = stats.getUserMoney(userName, userID)
        if userMoney < betAmount:
            msg = "You do not have enough money to bet ${}\n".format(betAmount)
            msg += "You currently have ${}".format(userMoney)
            return (msg, None)
        else:
            newGame = blackjack.Blackjack(userName, betAmount)
            bjGames[userID] = newGame
            msg = newGame.__str__()

            #Check game state after player move
            if newGame.game_state != -1:
                del bjGames[userID]
                gameState = 1
                msg += "\n**You currently have ${}**".format(userMoney)
            return (msg, newGame)

#Hit during a game of blackjack
def bjHit(userName, userID):
    if userID in bjGames:
        game = bjGames[userID]
        game.player_hit()
        msg = game.__str__()

        #Check game state after player move
        if game.game_state != -1:
            del bjGames[userID]
            userMoney = stats.getUserMoney(userName, userID)
            msg += "\n**You currently have ${}**".format(userMoney)
    else:
        msg = "You are currently not in a game of blackjack"
    return (msg, game)

#Stand during a game of blackjack
def bjStand(userName, userID):
    if userID in bjGames:
        game = bjGames[userID]
        game.player_stand()
        msg = game.__str__()

        #Check game state after player move
        if game.game_state != -1:
            del bjGames[userID]
            userMoney = stats.getUserMoney(userName, userID)
            msg += "\n**You currently have ${}**".format(userMoney)
    else:
        msg = "You are currently not in a game of blackjack"
    return (msg, game)

#Double down during a game of blackjack
def bjDoubleDown(userName, userID):
    if userID in bjGames:
        game = bjGames[userID]
        userMoney = stats.getUserMoney(userName, userID)
        userBet = game.player_bet

        #Make sure player has enough money to double bet
        if userMoney < userBet*2:
            msg = "You do not have enough money to double your current bet of ${}".format(userBet)
        else:
            game.player_dd()
            msg = game.__str__()

            #Check game state after player move
            if game.game_state != -1:
                del bjGames[userID]
                msg += "\n**You currently have ${}**".format(userMoney)
    else:
        msg = "You are currently not in a game of blackjack"
    return (msg, game)

#Update blackjack stats
def bjUpdate(userName, userID, game):
    if game.game_state != -1:
        stats.updateUserBJStat(userName, userID, game)

#Return marvel/philo stats result through string
def pmStats(userName, userID):
    return stats.pmStats(userName, userID)

#Return blackjack stats result through string
def bjStats(userName, userID):
    return stats.bjStats(userName, userID)

#Reset user stats for specified data
#(1) philo (2) marvel (3) blackjack or (4) all
#Return a string indicating success
def resetStats(userName, userID, statsType):
    return stats.resetStats(userName, userID, statsType)

#Give everyone in blackjack sheet money
def giveEveryoneMoney(amount):
    stats.giveEveryoneMoney(amount)

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
    philoList1 = stats.philoList1
    philoList2 = stats.philoList2

    #Lucky items in philo
    lucky = stats.philoLuckyList
    gotLucky = False
    messages = []
    msg = "**__{}'s philo run:__**\n".format(userName.title())

    #Get user info to record stats
    userRow = stats.getUserRow(userName, userID, "p")

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
            stats.updateUserItemStat(userRow, item1, 1, "p")
            gotLucky = True
        else:
            temp += item1.title() + ", "
        if item2 in lucky:
            temp += "**__" + item2.title() + "__** "
            lucky[item2] += 1
            stats.updateUserItemStat(userRow, item2, 1, "p")
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
    stats.updateUserItemStat(userRow, "rolls", numRolls, "p")

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
    philoList1 = stats.philoList1
    philoList2 = stats.philoList2
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
    costs = stats.pmSpendings(counter, 0)
    low_money = costs[0]
    high_money = costs[1]
    msg = "It took {:,d} book(s) to get the item: ".format(counter) + item.title() + "\n"
    msg += "{:,d} book(s) = ${:,.2f} ~ ${:,.2f}".format(counter, low_money, high_money)
    return msg

#Roll marvel a specified number of times, up to 110
#Return the results through an array
def marvelRoll(userName, userID, numRolls):
    marvelList1 = stats.marvelList1
    marvelList2 = stats.marvelList2
    marvelList3 = stats.marvelList3

    #Lucky items in marvel
    lucky = stats.marvelLuckyList
    gotLucky = False
    messages = []
    msg = "**__{}'s marvel run:__**\n".format(userName.title())

    #Get user info to record stats
    userRow = stats.getUserRow(userName, userID, "m")

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
            stats.updateUserItemStat(userRow, itemA, 1, "m")
            gotLucky = True
        else:
            temp += itemA.title() + ", "
        if itemB in lucky:
            temp += "**__" + itemB.title() + "__**, "
            lucky[itemB] += 1
            stats.updateUserItemStat(userRow, itemB, 1, "m")
            gotLucky = True
        else:
            temp += itemB.title() + ", "
        if itemC in lucky:
            temp += "**__" + itemC.title() + "__** "
            lucky[itemC] += 1
            stats.updateUserItemStat(userRow, itemC, 1, "m")
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
    stats.updateUserItemStat(userRow, "rolls", numRolls, "m")

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
    marvelList1 = stats.marvelList1
    marvelList2 = stats.marvelList2
    marvelList3 = stats.marvelList3
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
    costs = stats.pmSpendings(counter, 1)
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

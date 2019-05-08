import random

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

from discord.ext import commands
import discord
import random
import typing
import gamble_bot_methods

bot = commands.Bot(command_prefix = "g!")

@bot.event
async def on_ready():
    print("Everything is ready to go")

#List of commands for the bot
@bot.command()
async def halp(ctx):
    msg = """__Arguments with \* are optional, they come with default values__
g!flip [\*numFlips=1] [\*guess=None]: Flips a coin 'numFlips' amount of times or once with an initial guess
g!roll [\*numRolls=1] [\*numSides=6]: Rolls a die with 'numSides' amount of sides 'numRolls' amount of times
g!philo [\*numRolls=11] [\*findItem=None]: Open 'numRolls' amount of philosopher books or open until 'findItem' is rolled
g!marvel [\*numRolls=11] [\*findItem=None]: Roll the marvel machine 'numRolls' amount of times or roll until 'findItem' is rolled
g!stats [\*statsType=1]: Get your stats for (1) philo and marvel or (2) blackjack
g!reset [statsType]: Reset your stats for (1) philo (2) marvel (3) blackjack or (4) all"""
    await ctx.send(msg)

#Get user stats for marvel and philo or blackjack
#(1) for marvel/philo and (2) for blackjack, with default value of 1
@bot.command()
async def stats(ctx, statsType:typing.Optional[int] = 1):
    #Get user's name and unique ID
    userName = ctx.author.name
    userID = str(ctx.author.id)

    if statsType == 1:
        msg = gamble_bot_methods.pmStats(userName, userID)
    elif statsType == 2:
        msg = gamble_bot_methods.bjStats(userName, userID)
    else:
        msg = "Invalid type"
    await ctx.send(msg)

#Reset user stats for specified data
#(1) philo (2) marvel (3) blackjack or (4) all
@bot.command()
async def reset(ctx, statsType:int = None):
    #Get user's name and unique ID
    userName = ctx.author.name
    userID = str(ctx.author.id)

    if statsType == 1 or statsType == 2 or statsType == 3 or statsType == 4:
        msg = gamble_bot_methods.resetStats(userName, userID, statsType)
    else:
        msg = "Invalid type"
    await ctx.send(msg)

#Check the bot ping
@bot.command()
async def ping(ctx):
    latency = bot.latency
    rounded = round(latency, 5)
    await ctx.send("{}s".format(rounded))

#Flip a fair coin up to 100,000 times at once with default flip amount of 1
#Or flip a coin once with an initial guess
#Note that giving both arguments calls flipGuess
@bot.command()
async def flip(ctx, numFlips:typing.Optional[int] = 1, *, guess:str = None):
    if guess == None:
        msg = gamble_bot_methods.flip(numFlips)
    else:
        msg = gamble_bot_methods.flipGuess(guess)
    await ctx.send(msg)

#Roll a die with default number of sides of 6 and roll amount of 1
#Maximum number of sides of 100 and roll amount of 100,000
@bot.command()
async def roll(ctx, numRolls:typing.Optional[int] = 1, numSides:typing.Optional[int] = 6):
    #Note bots have max length of 2,000 chars per msg
    results = gamble_bot_methods.rollDie(numRolls, numSides)
    for msg in results:
        await ctx.send(msg)

#Roll the specified amount of philosopher books, up to 165
#Or roll for a specific item
#Note that giving both arguments calls philoFind
@bot.command()
async def philo(ctx, numRolls:typing.Optional[int] = 11, *, find_item:str = None):
    #Get user's name and unique ID
    userName = ctx.author.name
    userID = str(ctx.author.id)

    if find_item == None:
        results = gamble_bot_methods.philoRoll(userName, userID, numRolls)
        for msg in results:
            await ctx.send(msg)
    else:
        #These rolls are not recorded in stats
        msg = gamble_bot_methods.philoFind(find_item)
        await ctx.send(msg)

#Roll marvel marchine the specified amount of times, up to 110
#Or roll for a specific item
#Note that giving both arguments calls marvelFind
@bot.command()
async def marvel(ctx, numRolls:typing.Optional[int] = 11, *, find_item:str = None):
    #Get user's name and unique ID
    userName = ctx.author.name
    userID = str(ctx.author.id)

    if find_item == None:
        results = gamble_bot_methods.marvelRoll(userName, userID, numRolls)
        for msg in results:
            await ctx.send(msg)
    else:
        #These rolls are not recorded in stats
        msg = gamble_bot_methods.marvelFind(find_item)
        await ctx.send(msg)

#Read in the unique bot ID and run bot
def read_ID():
    with open("gamble_bot_ID.txt", "r") as file:
        return file.readline()

bot_id = read_ID()
bot.run(bot_id)

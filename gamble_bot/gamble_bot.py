from discord.ext import commands
import discord
import random
import typing
#import schedule
import asyncio
import gamble_bot_methods
import gamble_bot_stats
import datetime

bot = commands.Bot(command_prefix = "g!", case_insensitive = True)
bot.remove_command("help")
startTime = None

@bot.event
async def on_ready():
    global startTime

    startTime = datetime.datetime.now().replace(microsecond=0)
    print("Gamble bot started running at", end=": ")
    print(startTime)
    print("Gamble bot is ready to go")
    await passiveIncome()

@bot.command()
async def sTime(ctx):
    msg = "Gamble bot has been live since "
    msg += str(startTime)
    await ctx.send(msg)

@bot.command()
async def lTime(ctx):
    timeNow = datetime.datetime.now().replace(microsecond=0)
    timeDiff = timeNow - startTime
    timer = datetime.timedelta(seconds=timeDiff.total_seconds())
    d = timer.days
    m, s = divmod(timer.seconds, 60)
    h, m = divmod(m, 60)
    msg = "Gamble bot has been live for "
    msg += "{:.0f} days, {:.0f} hours, {:.0f} minutes, and {:.0f} seconds".format(d, h, m, s)
    await ctx.send(msg)

@bot.command()
async def money(ctx, amount):
    userID = ctx.author.id
    if userID == bot.owner_id:
        gamble_bot_methods.giveEveryoneMoney(amount)

#Passively give everyone (that has data) money for blackjack
async def passiveIncome():
    await bot.wait_until_ready()
    while not bot.is_closed():
        gamble_bot_methods.checkCreds()
        gamble_bot_methods.giveEveryoneMoney(25)
        #Idk how to get schedule to work
        #schedule.every(2).minutes.do(gamble_bot_methods.giveEveryoneMoney, 50)
        #schedule.run_continuously(60) #in seconds
        await asyncio.sleep(3600) #1 hour

#List of commands for the bot
@bot.command()
async def help(ctx):
    embed = discord.Embed(color = discord.Color.red())
    embed.set_author(name = "Gamble Bot's Command List: Prefix 'g!'")
    embed.add_field(name = "blackjack <Optional: betAmount=0>", value = "Start a game of blackjack")
    embed.add_field(name = "flip <Optional: numFlips=1> <Optional: guess=None>", value = "Flips a coin 'numFlips' amount of times or once with an initial guess")
    embed.add_field(name = "marvel <Optional: numRolls=11> <Optional: findItem=None>", value = "Roll the marvel machine 'numRolls' amount of times or roll until 'findItem' is rolled")
    embed.add_field(name = "philo <Optional: numRolls=11> <Optional: findItem=None>", value = "Open 'numRolls' amount of philosopher books or open until 'findItem' is rolled")
    embed.add_field(name = "reset <statsType>", value = "Reset your stats for (1) philo (2) marvel (3) blackjack or (4) all")
    embed.add_field(name = "roll <Optional: numRolls=1> <Optional: numSides=6>", value = "Rolls a die with 'numSides' amount of sides 'numRolls' amount of times")
    embed.add_field(name = "star <startStar> <endStar> <Optional: itemLevel=150>", value = "Starforce an item from 'startStar' to 'endStar'")
    embed.add_field(name = "stats <Optional: statsType=1>", value = "Get your stats for (1) marvel and philo or (2) blackjack")
    await ctx.send(embed=embed)

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

#Start a game of blackjack
@bot.command()
async def blackjack(ctx, betAmount:typing.Optional[int] = 0):
    #Get user's name and unique ID
    userName = ctx.author.name
    userID = str(ctx.author.id)

    msg = gamble_bot_methods.bj(userName, userID, betAmount)
    await ctx.send(msg)

#Hit during a game of blackjack
@bot.command()
async def hit(ctx):
    #Get user's name and unique ID
    userName = ctx.author.name
    userID = str(ctx.author.id)

    msg = gamble_bot_methods.bjHit(userName, userID)
    await ctx.send(msg)

#Stand during a game of blackjack
@bot.command()
async def stand(ctx):
    #Get user's name and unique ID
    userName = ctx.author.name
    userID = str(ctx.author.id)

    msg = gamble_bot_methods.bjStand(userName, userID)
    await ctx.send(msg)

#Double down during a game of blackjack
@bot.command()
async def dd(ctx):
    #Get user's name and unique ID
    userName = ctx.author.name
    userID = str(ctx.author.id)

    msg = gamble_bot_methods.bjDoubleDown(userName, userID)
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

#Star an item of specified level from the specified starting star to ending star
@bot.command()
async def star(ctx, startStar:int=None, endStar:int=None, itemLevel:typing.Optional[int]=150):
    if startStar == None or endStar == None:
        await ctx.send("Must provide star numbers to start and end at")
    else:
        msg = await gamble_bot_methods.starforceMessage(startStar, endStar, itemLevel)
        await ctx.send(msg)

#Read in the unique bot ID and run bot
def read_ID():
    with open("gamble_bot_ID.txt", "r") as file:
        return file.readline()

bot_id = read_ID()
bot.run(bot_id)

from discord.ext import commands
import discord
import random
import typing
#import schedule
import asyncio
import gamble_bot_methods_sql
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
        gamble_bot_methods_sql.giveEveryoneMoney(amount)

#Passively give everyone (that has data) money for blackjack
async def passiveIncome():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await asyncio.sleep(1800) #Check creds every 30 mins
        gamble_bot_methods_sql.checkCreds()
        await asyncio.sleep(1800) #Give everyone money every hour
        gamble_bot_methods_sql.checkCreds()
        gamble_bot_methods_sql.giveEveryoneMoney(25)
        #Idk how to get schedule to work
        #schedule.every(2).minutes.do(gamble_bot_methods.giveEveryoneMoney, 50)
        #schedule.run_continuously(60) #in seconds

#List of commands for the bot
@bot.command()
async def help(ctx):
    embed = discord.Embed(color = discord.Color.red())
    embed.set_author(name = "Gamble Bot's Command List: Prefix 'g!'")
    embed.add_field(name = "af <startLvl> <endLvl> <currProgress> <dailyRate>", value = "Calculate days needed to max arcane force symbols", inline = False)
    embed.add_field(name = "blackjack <Optional: betAmount=0>", value = "Start a game of blackjack", inline = False)
    embed.add_field(name = "hit:", value = "During a game of blackjack, hit (draw a card)", inline = False)
    embed.add_field(name = "stand:", value = "During a game of blackjack, stand (end your turn)", inline = False)
    embed.add_field(name = "dd:", value = "During a game of blackjack (only after your initial 2 cards), double down (double your bet and draw one more card)", inline = False)
    embed.add_field(name = "flip <Optional: numFlips=1> <Optional: guess=None>", value = "Flips a coin 'numFlips' amount of times or once with an initial guess", inline = False)
    embed.add_field(name = "marvel <Optional: numRolls=11> <Optional: findItem=None>", value = "Roll the marvel machine 'numRolls' amount of times or roll until 'findItem' is rolled", inline = False)
    embed.add_field(name = "philo <Optional: numRolls=11> <Optional: findItem=None>", value = "Open 'numRolls' amount of philosopher books or open until 'findItem' is rolled", inline = False)
    embed.add_field(name = "reset <statsType>", value = "Reset your stats for (1) philo (2) marvel (3) blackjack or (4) all", inline = False)
    embed.add_field(name = "roll <Optional: numRolls=1> <Optional: numSides=6>", value = "Rolls a die with 'numSides' amount of sides 'numRolls' amount of times", inline = False)
    embed.add_field(name = "star <startStar> <endStar> <Optional: itemLevel=150> <Optional: safeGuard=n>", value = "Starforce an item from 'startStar' to 'endStar'", inline = False)
    embed.add_field(name = "stats <Optional: statsType=1>", value = "Get your stats for (1) marvel and philo or (2) blackjack", inline = False)
    embed.set_footer(text = "Note: Commands aren't case sensitive")
    await ctx.send(embed=embed)

# Calculate days needed to max arcane force symbols
@bot.command()
async def af(ctx, startLvl:int, endLvl:int, currProgress:int, dailyRate:int):
    msg = gamble_bot_methods_sql.af(startLvl, endLvl, currProgress, dailyRate)
    await ctx.send(msg)

#Get user stats for marvel and philo or blackjack
#(1) for marvel/philo and (2) for blackjack, with default value of 1
@bot.command()
async def stats(ctx, statsType:typing.Optional[int] = 1):
    #Get user's name and unique ID
    userName = ctx.author.name
    userID = str(ctx.author.id)

    if statsType == 1:
        msg = gamble_bot_methods_sql.pmStats(userName, userID)
    elif statsType == 2:
        msg = gamble_bot_methods_sql.bjStats(userName, userID)
    else:
        msg = "Invalid type"
    await ctx.send(msg)

#Start a game of blackjack
@bot.command()
async def blackjack(ctx, betAmount:typing.Optional[int] = 0):
    #Get user's name and unique ID
    userName = ctx.author.name
    userID = str(ctx.author.id)

    msg, game = gamble_bot_methods_sql.bj(userName, userID, betAmount)
    await ctx.send(msg)
    if game != None:
        gamble_bot_methods_sql.bjUpdate(userName, userID, game)

#Hit during a game of blackjack
@bot.command()
async def hit(ctx):
    #Get user's name and unique ID
    userName = ctx.author.name
    userID = str(ctx.author.id)

    msg, game = gamble_bot_methods_sql.bjHit(userName, userID)
    await ctx.send(msg)
    gamble_bot_methods_sql.bjUpdate(userName, userID, game)

#Stand during a game of blackjack
@bot.command()
async def stand(ctx):
    #Get user's name and unique ID
    userName = ctx.author.name
    userID = str(ctx.author.id)

    msg, game = gamble_bot_methods_sql.bjStand(userName, userID)
    await ctx.send(msg)
    gamble_bot_methods_sql.bjUpdate(userName, userID, game)

#Double down during a game of blackjack
@bot.command()
async def dd(ctx):
    #Get user's name and unique ID
    userName = ctx.author.name
    userID = str(ctx.author.id)

    msg, game = gamble_bot_methods_sql.bjDoubleDown(userName, userID)
    await ctx.send(msg)
    gamble_bot_methods_sql.bjUpdate(userName, userID, game)

#Reset user stats for specified data
#(1) marvel (2) philo (3) blackjack or (4) all
@bot.command()
async def reset(ctx, statsType:int = None):
    #Get user's name and unique ID
    userName = ctx.author.name
    userID = str(ctx.author.id)

    if statsType == 1 or statsType == 2 or statsType == 3 or statsType == 4:
        msg = gamble_bot_methods_sql.resetStats(userName, userID, statsType)
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
        msg = gamble_bot_methods_sql.flip(numFlips)
    else:
        msg = gamble_bot_methods_sql.flipGuess(guess)
    await ctx.send(msg)

#Roll a die with default number of sides of 6 and roll amount of 1
#Maximum number of sides of 100 and roll amount of 100,000
@bot.command()
async def roll(ctx, numRolls:typing.Optional[int] = 1, numSides:typing.Optional[int] = 6):
    #Note bots have max length of 2,000 chars per msg
    results = gamble_bot_methods_sql.rollDie(numRolls, numSides)
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
        results = gamble_bot_methods_sql.philoRoll(userName, userID, numRolls)
        for msg in results:
            await ctx.send(msg)
    else:
        #These rolls are not recorded in stats
        msg = gamble_bot_methods_sql.philoFind(find_item)
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
        results = gamble_bot_methods_sql.marvelRoll(userName, userID, numRolls)
        for msg in results:
            await ctx.send(msg)
    else:
        #These rolls are not recorded in stats
        msg = gamble_bot_methods_sql.marvelFind(find_item)
        await ctx.send(msg)

#Star an item of specified level from the specified starting star to ending star
@bot.command()
async def star(ctx, startStar:int=None, endStar:int=None, itemLevel:typing.Optional[int]=150, *, safeGuard:typing.Optional[str]="n"):
    if startStar == None or endStar == None:
        await ctx.send("Must provide star numbers to start and end at")
    else:
        userName = ctx.author.name
        msg = await gamble_bot_methods_sql.starforceMessage(userName, startStar, endStar, itemLevel, safeGuard)
        await ctx.send(msg)

#Read in the unique bot ID and run bot
def read_ID():
    with open("gamble_bot_ID.txt", "r") as file:
        return file.readline()

bot_id = read_ID()
bot.run(bot_id)

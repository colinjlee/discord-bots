from discord.ext import commands
import discord
import random
import asyncio
import datetime

bot = commands.Bot(command_prefix = "!", case_insensitive = True)
botName = "Compliment bot"
channel = None
count = 0

#Names to choose from
names = ["John", "Jane"]

#Compliments to choose from
#List of pairs that has the message and a number to indicate if it needs a name
compliments = [("Hi {}, you look beautiful!",0),
               ("You look incredible!",1)]
usedCompliments = []
random.shuffle(compliments)

@bot.event
async def on_ready():
    global botName

    startTime = datetime.datetime.now().replace(microsecond=0)
    print("{} started running at".format(botName), end=": ")
    print(startTime)
    print("{} is ready to go".format(botName))
    await passiveCompliment()

#Calls autoCompliment every hour
async def passiveCompliment():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await autoCompliment()
        await asyncio.sleep(3600) #1 hour in seconds

#Picks a compliment and name at random if needed
#Puts compliments in usedCompliments after
#Resets the lists after every compliment is used
#Replys in the channel with given channel_id
async def autoCompliment():
    global channel

    msg = getCompliment()
    if channel == None:
        # TODO: Add unique channel_id
        # channel = bot.get_channel(channel_id)
    await channel.send(msg)

#Returns a compliment
#Same as above but triggered from user command
#Replies in channel that user typed in
@bot.command()
async def compliment(ctx):
    msg = getCompliment()
    await ctx.send(msg)

#Return a string containing a random compliment
def getCompliment():
    global compliments, usedCompliments, count
    count += 1

    #Empty list so reset the lists
    if not compliments:
        compliments = usedCompliments
        random.shuffle(compliments)
        usedCompliments = []

    msg, num = compliments.pop()
    usedCompliments += [(msg, num)]
    #Add a name if needed
    if num == 0:
        name = random.choice(names)
        msg = msg.format(name)
    return msg

#Return compliment count for this session
@bot.command()
async def count(ctx):
    global count, botName

    msg = "{} has given {} compliments during this session!".format(botName, count)

# TODO: Add unique bot_id
#bot.run(bot_id)

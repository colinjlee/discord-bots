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
    msg = """g!flip: Flips a fair coin once"""
    await ctx.send(msg)

#Check the bot ping
@bot.command()
async def ping(ctx):
    latency = bot.latency
    rounded = round(latency, 5)
    await ctx.send("{}s".format(rounded))

#Flip a fair coin up to 100,000 times at once with default flip amount of 1
@bot.command()
async def flip(ctx, numFlips:typing.Optional[int] = 1):
    #Amount of flips must be positive
    if numFlips < 1:
        await ctx.send("Amount of rolls must be positive or empty to use default value")
    #Flip just once
    elif numFlips == 1:
        rand = random.randint(0,1)
        if rand == 0:
            await ctx.send("Heads")
        else:
            await ctx.send("Tails")
    #Different message format for flipping more than once
    else:
        #String to be sent after results
        msg = ""
        if numFlips > 100000:
            msg += "**Max of 100,000 flips**\n"
            numFlips = 100000

        #Get and send results
        results = gamble_bot_methods.roll(numFlips, 2)
        head = results[0]
        tail = results[1]
        hRate = head/numFlips*100
        tRate = tail/numFlips*100

        msg += "Heads: {:,d} ({:.2f}%)\nTails: {:,d} ({:.2f}%)"
        await ctx.send(msg.format(head, hRate, tail, tRate))

#Roll a die with default face value of 6 and roll amount of 1
#Maximum face value of 100 and roll amount of 100,000
@bot.command()
async def roll(ctx, numRolls:typing.Optional[int] = 1, numSides:typing.Optional[int] = 6):
    #Amount of flips and face count must be positive
    if numRolls < 1 or numSides < 1:
        await ctx.send("Amount of rolls and die side count must be positive or empty to use default values")
    #Roll just once
    elif numRolls == 1:
        rand = random.randint(1,numSides)
        await ctx.send(rand)
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
        results = gamble_bot_methods.roll(numRolls, numSides)
        for x in range(0, numSides):
            if results[x] > 0:
                res = "{:,d}: {:,d} ({:.2f}%)\n".format(x+1, results[x], (results[x]/numRolls*100))
                if len(msg) + len(res) > 2000:
                    await ctx.send(msg)
                    msg = res
                else:
                    msg += res
        await ctx.send(msg)

#Read in the unique bot ID and run bot
def read_ID():
    with open("gamble_bot_ID.txt", "r") as file:
        return file.readline()

bot_id = read_ID()
bot.run(bot_id)

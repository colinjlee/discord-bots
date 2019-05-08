from discord.ext import commands
import discord
import random
import typing

bot = commands.Bot(command_prefix = "g!")

@bot.event
async def on_ready():
    print("Everything is ready to go")

#List of commands for the bot
@bot.command()
async def halp(ctx):
    mes = """g!flip: Flips a fair coin once"""
    await ctx.send(mes)

#Check the bot ping
@bot.command()
async def ping(ctx):
    latency = bot.latency
    rounded = round(latency, 5)
    await ctx.send("{}s".format(rounded))

#Flip a fair coin up to 100,000 times at once with default flip amount of 1
@bot.command()
async def flip(ctx, amount:typing.Optional[int] = 1):
    #Counters for head and tail flips
    head = tail = 0

    #Amount of flips must be positive
    if amount < 1:
        await ctx.send("Amount of rolls must be positive or empty to use default value")
    #Flip just once
    elif amount == 1:
        rand = random.randint(0,1)
        if rand == 0:
            await ctx.send("Heads")
        else:
            await ctx.send("Tails")
    #Different message format for flipping more than once
    else:
        #String to be sent after results
        mes = ""

        if amount > 100000:
            mes += "Max of 100,000 flips at once\n"
            amount = 100000

        #Start flipping
        for x in range(0, amount):
            rand = random.randint(0,1)
            if rand == 0:
                head += 1
            else:
                tail += 1

        #Send results
        mes += "Heads: {:,d} ({:.2f}%)\nTails: {:,d} ({:.2f}%)"
        hRate = head/amount*100
        tRate = tail/amount*100
        await ctx.send(mes.format(head, hRate, tail, tRate))

#Roll a die with default face value of 6 and roll amount of 1
#Maximum face value of 100 and roll amount of 100,000
@bot.command()
async def roll(ctx, amount:typing.Optional[int] = 1, numSides:typing.Optional[int] = 6):
    #Amount of flips and face count must be positive
    if amount < 1 or numSides < 1:
        await ctx.send("Amount of rolls and die side count must be positive or empty to use default values")
    #Roll just once
    elif amount == 1:
        rand = random.randint(1,numSides)
        await ctx.send(rand)
    #Different message format for rolling more than once
    else:
        #String and results to be sent
        mes = ""
        result = [0] * numSides

        if numSides > 100:
            str += "Max of 100 sided die\n"
            die = 100
        if amount > 100000:
            str += "Max of 100,000 rolls at once\n"
            amount = 100000

        #Start rolling
        for x in range(0, amount):
            rand = random.randint(1,numSides)
            result[rand-1] += 1

        #Send results. Note bots have max length of 2000 per message
        for x in range(0, numSides):
            if result[x] > 0:
                res = "{:,d}: {:,d} ({:.2f}%)\n".format(x+1, result[x], (result[x]/amount*100))
                if len(mes) + len(res) > 2000:
                    await ctx.send(mes)
                    mes = res
                else:
                    mes += res
        await ctx.send(mes)

#Read in the unique bot ID and run bot
def read_ID():
    with open("gamble_bot_ID.txt", "r") as file:
        return file.readline()

bot_id = read_ID()
bot.run(bot_id)

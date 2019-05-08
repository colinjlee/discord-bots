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
    msg = """Arguments with \* are optional
g!flip  [\*numFlips]: Flips a coin 'numFlips' amount of times
g!flip2 [guess]: Flip a coin with a guess of 'h' or 't'
g!roll  [\*numRolls] [\*numSides]: Rolls a die with 'numSides' amount of sides 'numRolls' amount of times"""
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
    msg = gamble_bot_methods.flip(numFlips)
    await ctx.send(msg)

#Flip a fair coin once with an initial guess
@bot.command()
async def flip2(ctx, guess:str = ""):
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

#Read in the unique bot ID and run bot
def read_ID():
    with open("gamble_bot_ID.txt", "r") as file:
        return file.readline()

bot_id = read_ID()
bot.run(bot_id)

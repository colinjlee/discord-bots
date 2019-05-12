from discord.ext import commands
import discord
import random
import asyncio
import datetime

bot = commands.Bot(command_prefix = "!", case_insensitive = True)
bot.remove_command("help")

#Globals
botName = "Compliment bot"
complimentFile = "compliment_list.txt"
nameFile = "name_list.txt"
channel = None
interval = 3600
counter = 0
rawList = []
compliments = []
usedCompliments = []
names = []

#Read in compliments and shuffle it
def makeComplimentList():
    global compliments, usedCompliments, rawList, complimentFile
    compliments = []
    usedCompliments = []

    with open(complimentFile, "r") as text:
        for line in text:
            msg, num = line.split("@%")
            rawList += [str(msg)]
            compliments += [(str(msg),int(num))]
    random.shuffle(compliments)

#Read in names
def makeNameList():
    global names, nameFile

    with open(nameFile, "r") as text:
        for line in text:
            name = line.rstrip()
            names += [str(name)]

#Calls autoCompliment every hour
async def passiveCompliment():
    global interval

    await bot.wait_until_ready()
    while not bot.is_closed():
        #Not an ideal way to do this......
        #Sleep for 1 second, for default 3600 times (1 hour)
        oldInterval = interval
        timeUp = False
        for i in range(interval):
            if oldInterval != interval:
                break
            else:
                if i+1 == interval:
                    timeUp = True
                await asyncio.sleep(1)
        if timeUp == True:
            await autoCompliment()

#To compliment automatically
async def autoCompliment():
    global channel

    msg = getCompliment()
    if channel == None:
        #TODO: Put in unique channel id as an int for default channel
        #channel = bot.get_channel(channelid)
    await channel.send(msg)

#Get compliment message
def getCompliment():
    global compliments, usedCompliments, counter
    counter += 1

    if not compliments: #Empty list
        compliments = usedCompliments
        random.shuffle(compliments)
        usedCompliments = []

    msg, num = compliments.pop()
    usedCompliments += [(msg, num)]
    if num == 0:
        name = random.choice(names)
        msg = msg.format(name)
    return msg

@bot.event
async def on_ready():
    global botName

    makeComplimentList()
    makeNameList()

    startTime = datetime.datetime.now().replace(microsecond=0)
    print("{} started running at".format(botName), end=": ")
    print(startTime)
    print("{} is ready to go".format(botName))
    await passiveCompliment()

#List of commands
@bot.command()
async def help(ctx):
    embed = discord.Embed(color = discord.Color.green())
    embed.set_author(name = "Command List:")
    embed.add_field(name = "!addC:", value = "Add a compliment to the list", inline=False)
    embed.add_field(name = "!addN:", value = "Add a name to the list", inline=False)
    embed.add_field(name = "!cc:", value = "Type this in the channel you want the messages to switch to", inline=False)
    embed.add_field(name = "!ci <number>:", value = "Change the interval of auto-compliments (in seconds)", inline=False)
    embed.add_field(name = "!compliment:", value = "Get a random compliment", inline=False)
    embed.add_field(name = "!count:", value = "Get the number of compliments given", inline=False)
    embed.add_field(name = "!delC <number>:", value = "Delete the 'nth' compliment from the list then restarts the list", inline=False)
    embed.add_field(name = "!delN <number>:", value = "Delete the 'nth' name from the list", inline=False)
    embed.add_field(name = "!listC:", value = "Get the list of compliments", inline=False)
    embed.add_field(name = "!listN:", value = "Get the list of names", inline=False)
    await ctx.send(embed=embed)

#Compliment manually
@bot.command()
async def compliment(ctx):
    msg = getCompliment()
    await ctx.send(msg)

#Change channel the auto compliments goes to
@bot.command()
async def cc(ctx):
    global channel
    channel = ctx.channel
    await ctx.send("Successfully changed to this channel")

#Change time interval for auto compliments
@bot.command()
async def ci(ctx, num:int=None):
    global interval

    if num == None:
        msg = "Add a number to change the time interval (in seconds)"
    elif num > 0:
        old = interval
        interval = num
        msg = "Successfully changed the interval from {}s to {}s".format(old,num)
    else:
        msg = "Invalid interval"
    await ctx.send(msg)

#Add a compliment
@bot.command()
async def addC(ctx, *, compliment:str=None):
    global compliments, rawList, complimentFile

    if compliment == None:
        msg = "Write a compliment to add to the list"
    else:
        #Add to local list
        rawList += [compliment]

        #New compliment will use a random name
        if "{}" in compliment:
            num = 0
            compliments += [(compliment,num)]
        else:
            num = 1
            compliments += [(compliment,num)]

        #Add to file
        with open(complimentFile, "a") as f:
            f.write(compliment + "@%" + str(num) + "\n")

        msg = "Successfully added '{}' to the list of compliments".format(compliment)

    await ctx.send(msg)

#Add a name
@bot.command()
async def addN(ctx, name:str=None):
    global names, nameFile

    if name == None:
        msg = "Write a name to add to the list"
    else:
        #Add to local list
        names += [name]

        #Add to file
        with open(nameFile, "a") as f:
            f.write(name + "\n")

        msg = "Successfully added '{}' to the list of names".format(name)
    await ctx.send(msg)

#Delete a compliment
@bot.command()
async def delC(ctx, num:int=-1):
    global rawList, complimentFile, compliments, usedCompliments

    #Delete if valid index
    if num-1 in range(0,len(rawList)):
        #Delete in local lists
        deleted = rawList[num-1]
        del(rawList[num-1])

        hasDeleted = False
        #Delete in compliments list
        for i in range(0, len(compliments)):
            pair = compliments[i]
            compliment = pair[0]
            if compliment == deleted:
                del(compliments[i])
                hasDeleted = True
                break
        #Delete in used compliments list if not in compliments
        if hasDeleted == False:
            for i in range(0, len(usedCompliments)):
                pair = usedCompliments[i]
                compliment = pair[0]
                if compliment == deleted:
                    del(usedCompliments[i])
                    break

        #Delete in file
        i = 1
        with open(complimentFile,"r+") as f:
            new_f = f.readlines()
            f.seek(0)
            for line in new_f:
                if i != num:
                    f.write(line)
                i += 1
            f.truncate()

        msg = "Successfully deleted '{}' from the list of compliments".format(deleted)
    #Invalid index
    else:
        msg = "Invalid line number"
    await ctx.send(msg)

#Delete a name
@bot.command()
async def delN(ctx, num:int=-1):
    global names, nameFile

    #Delete if valid index
    if num-1 in range(0,len(names)):
        #Delete in local list
        del(names[num-1])

        #Delete in file
        i = 1
        with open(nameFile,"r+") as f:
            new_f = f.readlines()
            f.seek(0)
            for line in new_f:
                if i != num:
                    f.write(line)
                else:
                    deleted = line[:-1]
                i += 1
            f.truncate()

        msg = "Successfully deleted '{}' from the list of names".format(deleted)
    #Invalid index
    else:
        msg = "Invalid line number"
    await ctx.send(msg)

#List the names
@bot.command()
async def listN(ctx):
    global names

    msg = ""
    temp = ""
    for i in range(0, len(names)):
        temp = "{}: {}\n".format(i+1, names[i])
        if len(msg) + len(temp) > 2000:
            msg = msg[:-1]
            await ctx.send(msg)
            msg = temp
        else:
            msg += temp
    msg = msg[:-1]
    await ctx.send(msg)

#List the compliments
@bot.command()
async def listC(ctx):
    global rawList

    msg = ""
    temp = ""
    for i in range(0, len(rawList)):
        temp = "{}: {}\n".format(i+1, rawList[i])
        if len(msg) + len(temp) > 2000:
            msg = msg[:-1]
            await ctx.send(msg)
            msg = temp
        else:
            msg += temp
    msg = msg[:-1]
    await ctx.send(msg)

#Compliment count for session
@bot.command()
async def count(ctx):
    global counter, botName

    if counter == 0:
        msg = "{} hasn't given any compliments yet".format(botName)
    elif counter == 1:
        msg = "{} has given {} compliment!".format(botName, counter)
    else:
        msg = "{} has given {} compliments!".format(botName, counter)
    await ctx.send(msg)

#TODO: Put in unique bot id as str
#bot.run(botid)

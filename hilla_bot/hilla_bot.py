from discord.ext import commands
import discord
import datetime
import asyncio
import ffmpeg

bot_name = "Hilla Bot"
phase = 0
bot = commands.Bot(command_prefix = "!", case_insensitive = True)


@bot.event
async def on_ready():
    global bot_name

    startTime = datetime.datetime.now().replace(microsecond=0)
    print("{} started running at".format(bot_name), end=": ")
    print(startTime)


@bot.command()
async def join(ctx):
    voice_state = ctx.author.voice

    if voice_state is not None and voice_state.channel is not None:
        voice_channel = voice_state.channel
        await voice_channel.connect()
    else:
        await ctx.send("You must be in a voice channel for the bot to join")


@bot.command()
async def leave(ctx):
    global phase

    phase = 0
    voice_client = ctx.voice_client

    if voice_client is not None:
        await voice_client.disconnect()
    else:
        await ctx.send("Bot is not in a voice channel")


@bot.command(aliases=["phase1", "1"])
async def p1(ctx):
    time = datetime.datetime.now().time().replace(microsecond=0)

    # await ctx.send("Started phase 1 at {}. Phase 1 checks are approximately 2 minutes and 32 seconds.".format(time), tts=True)
    await timer(ctx, 1)


@bot.command(aliases=["phase2", "2"])
async def p2(ctx):
    time = datetime.datetime.now().time().replace(microsecond=0)

    # await ctx.send("Started phase 2 at {}. Phase 2 checks are approximately 2 minutes and 2 seconds.".format(time), tts=True)
    await timer(ctx, 2)


@bot.command(aliases=["phase3", "3"])
async def p3(ctx):
    time = datetime.datetime.now().time().replace(microsecond=0)

    # await ctx.send("Started phase 3 at {}. Phase 3 checks are approximately 1 minute and 40 seconds.".format(time), tts=True)
    await timer(ctx, 3)


@bot.command(aliases=["phase4", "4"])
async def p4(ctx):
    time = datetime.datetime.now().time().replace(microsecond=0)

    # await ctx.send("Started phase 4 at {}. Phase 4 checks are approximately 1 minute and 40 seconds.".format(time), tts=True)
    await timer(ctx, 4)


# 1: ~2 min 32 sec
# 2: ~2 min 32 sec
# 3: ~1 min 40 sec. Same for p4?
async def timer(ctx, num):
    global phase

    # Maps phases to list of times at 30s remaining, 5s remaining, and 0s remaining
    map = {1:[122, 147, 152], 2:[92, 117, 122], 3:[70, 95, 100], 4:[70, 95, 100]}
    list = map[num]
    phase = num
    counter = 0
    guild = ctx.guild
    voice_client = discord.utils.get(bot.voice_clients, guild=guild)

    while phase == num:
        await asyncio.sleep(1)
        counter += 1

        if counter == list[0]:
            if not voice_client.is_playing():
                audio_30s = discord.FFmpegPCMAudio(executable="C:\\ffmpeg\\bin\\ffmpeg.exe", source="30s.mp3")
                voice_client.play(audio_30s, after=None)
        elif counter == list[1]:
            if not voice_client.is_playing():
                audio_5s = discord.FFmpegPCMAudio(executable="C:\\ffmpeg\\bin\\ffmpeg.exe", source="5s.mp3")
                voice_client.play(audio_5s, after=None)
        elif counter == list[2]:
            counter = 0


bot.run("TOKEN")

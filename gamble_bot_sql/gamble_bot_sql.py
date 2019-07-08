from discord.ext import commands
import discord
import logging
import asyncio
import typing

import gamble_bot_methods_sql as gbm_sql
import datetime

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='gamble_bot_sql.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix='g!', case_insensitive=True)
bot.remove_command('help')
startTime = None


@bot.event
async def on_ready():
    global startTime

    startTime = datetime.datetime.now().replace(microsecond=0)
    print('Gamble bot started running at', end=': ')
    print(startTime)
    print('Gamble bot is ready to go')
    await passive_income()


@bot.command()
async def start_time(ctx):
    msg = 'Gamble bot has been live since '
    msg += str(startTime)
    await ctx.send(msg)


@bot.command()
async def live_time(ctx):
    time_now = datetime.datetime.now().replace(microsecond=0)
    time_diff = time_now - start_time
    timer = datetime.timedelta(seconds=time_diff.total_seconds())
    d = timer.days
    m, s = divmod(timer.seconds, 60)
    h, m = divmod(m, 60)
    msg = 'Gamble bot has been live for '
    msg += f'{d:.0f} days, {h:.0f} hours, {m:.0f} minutes, and {s:.0f} seconds'
    await ctx.send(msg)


@bot.command()
async def money(ctx, amount):
    user_id = ctx.author.id
    if user_id == bot.owner_id:
        gbm_sql.give_everyone_money(amount)


# Passively give everyone (that has data) money for blackjack
# Give everyone money every hour
async def passive_income():
    money_amount = 25
    time_interval = 3600
    
    await bot.wait_until_ready()
    while not bot.is_closed():
        await asyncio.sleep(time_interval)
        gbm_sql.give_everyone_money(money_amount)


# List of commands for the bot
@bot.command()
async def help(ctx):
    embed = discord.Embed(color=discord.Color.red())
    embed.set_author(name="Gamble Bot's Command List: Prefix 'g!'")
    embed.add_field(name='af <start_lvl> <end_lvl> <curr_progress> <Optional: daily_rate=8>', 
                    value='Calculate days needed to max arcane force symbols', inline=False)
    embed.add_field(name='blackjack <Optional: bet_amt=0>', value='Start a game of blackjack', inline=False)
    embed.add_field(name='hit:', value='During a game of blackjack, hit (draw a card)', inline=False)
    embed.add_field(name='stand:', value='During a game of blackjack, stand (end your turn)', inline=False)
    embed.add_field(name='dd:', 
                    value='During a game of blackjack (only after your initial 2 cards), double down', inline=False)
    embed.add_field(name='flip <Optional: num_flips=1> <Optional: guess=None>', 
                    value="Flips a coin 'num_flips' amount of times or once with an initial guess", inline=False)
    embed.add_field(name='marvel <Optional: num_rolls=11> <Optional: findItem=None>', 
                    value="""Roll the marvel machine 'num_rolls' amount of times or roll until 'findItem' is rolled
                    Current rates: http://maplestory.nexon.net/micro-site/39184""", inline=False)
    embed.add_field(name='philo <Optional: num_rolls=11> <Optional: findItem=None>', 
                    value="""Open 'num_rolls' amount of philosopher books or open until 'findItem' is rolled
                    Current rates: http://maplestory.nexon.net/micro-site/42030""", inline=False)
    embed.add_field(name='reset <stats_type>',
                    value='Reset your stats for (1) marvel (2) philo (3) blackjack or (4) all', inline=False)
    embed.add_field(name='roll <Optional: num_rolls=1> <Optional: num_sides=6>', 
                    value="Rolls a die with 'num_sides' amount of sides 'num_rolls' amount of times", inline=False)
    embed.add_field(name='star <startStar> <endStar> <Optional: itemLevel=150> <Optional: safeGuard=n>', 
                    value="Starforce an item from 'startStar' to 'endStar'", inline=False)
    embed.add_field(name='stats <Optional: stats_type=1>', 
                    value='Get your stats for (1) marvel and philo or (2) blackjack', inline=False)
    embed.set_footer(text="Note: Commands aren't case sensitive")
    await ctx.send(embed=embed)


#  Calculate days needed to max arcane force symbols
@bot.command()
async def af(ctx, start_lvl: int, end_lvl: int, curr_progress: int, daily_rate: typing.Optional[int] = 8):
    msg = gbm_sql.af(start_lvl, end_lvl, curr_progress, daily_rate)
    await ctx.send(msg)


# Get user stats for marvel and philo or blackjack
# (1) for marvel/philo and (2) for blackjack, with default value of 1
@bot.command()
async def stats(ctx, stats_type: int = 1):
    # Get user's name and unique ID
    username = ctx.author.name
    user_id = str(ctx.author.id)

    if stats_type == 1:
        msg = gbm_sql.philo_marvel_stats(username, user_id)
    elif stats_type == 2:
        msg = gbm_sql.bj_stats(username, user_id)
    else:
        msg = 'Invalid type'
    await ctx.send(msg)


# Start a game of blackjack
@bot.command()
async def blackjack(ctx, bet_amt: typing.Optional[int] = 0):
    # Get user's name and unique ID
    username = ctx.author.name
    user_id = str(ctx.author.id)

    msg, game = gbm_sql.bj(username, user_id, bet_amt)
    await ctx.send(msg)
    if game is not None:
        gbm_sql.bj_update(username, user_id, game)


# Hit during a game of blackjack
@bot.command()
async def hit(ctx):
    # Get user's name and unique ID
    username = ctx.author.name
    user_id = str(ctx.author.id)

    msg, game = gbm_sql.bj_hit(username, user_id)
    await ctx.send(msg)
    gbm_sql.bj_update(username, user_id, game)


# Stand during a game of blackjack
@bot.command()
async def stand(ctx):
    # Get user's name and unique ID
    username = ctx.author.name
    user_id = str(ctx.author.id)

    msg, game = gbm_sql.bj_stand(username, user_id)
    await ctx.send(msg)
    gbm_sql.bj_update(username, user_id, game)


# Double down during a game of blackjack
@bot.command()
async def dd(ctx):
    # Get user's name and unique ID
    username = ctx.author.name
    user_id = str(ctx.author.id)

    msg, game = gbm_sql.bj_double_down(username, user_id)
    await ctx.send(msg)
    gbm_sql.bj_update(username, user_id, game)


# Reset user stats for specified data
# (1) marvel (2) philo (3) blackjack or (4) all
@bot.command()
async def reset(ctx, stats_type: int = None):
    # Get user's name and unique ID
    username = ctx.author.name
    user_id = str(ctx.author.id)

    if stats_type == 1 or stats_type == 2 or stats_type == 3 or stats_type == 4:
        msg = gbm_sql.reset_stats(username, user_id, stats_type)
    else:
        msg = 'Invalid type'
    await ctx.send(msg)


# Check the bot ping
@bot.command()
async def ping(ctx):
    latency = bot.latency
    rounded = round(latency, 5)
    await ctx.send('{}s'.format(rounded))


# Flip a fair coin up to 100,000 times at once with default flip amount of 1
# Or flip a coin once with an initial guess
# Note that giving both arguments calls flip_guess
@bot.command()
async def flip(ctx, num_flips: typing.Optional[int] = 1, *, guess: typing.Optional[str] = None):
    if guess is None:
        msg = gbm_sql.flip(num_flips)
    else:
        msg = gbm_sql.flip_guess(guess)
    await ctx.send(msg)


# Roll a die with default number of sides of 6 and roll amount of 1
# Maximum number of sides of 100 and roll amount of 100,000
@bot.command()
async def roll(ctx, num_rolls: typing.Optional[int] = 1, num_sides: typing.Optional[int] = 6):
    # Note bots have max length of 2,000 chars per msg
    results = gbm_sql.roll_die(num_rolls, num_sides)
    for msg in results:
        await ctx.send(msg)


# Roll the specified amount of philosopher books, up to 165
# Or roll for a specific item
# Note that giving both arguments calls philo_find
@bot.command()
async def philo(ctx, num_rolls: typing.Optional[int] = 11, *, find_item: typing.Optional[str] = None):
    # Get user's name and unique ID
    username = ctx.author.name
    user_id = str(ctx.author.id)

    if find_item is None:
        results = gbm_sql.philo_roll(username, user_id, num_rolls)
        for msg in results:
            await ctx.send(msg)
    else:
        # These rolls are not recorded in stats
        msg = gbm_sql.philo_find(find_item)
        await ctx.send(msg)


# Roll marvel marchine the specified amount of times, up to 110
# Or roll for a specific item
# Note that giving both arguments calls marvel_find
@bot.command()
async def marvel(ctx, num_rolls: typing.Optional[int] = 11, *, find_item: typing.Optional[str] = None):
    # Get user's name and unique ID
    username = ctx.author.name
    user_id = str(ctx.author.id)

    if find_item is None:
        results = gbm_sql.marvel_roll(username, user_id, num_rolls)
        for msg in results:
            await ctx.send(msg)
    else:
        # These rolls are not recorded in stats
        msg = gbm_sql.marvel_find(find_item)
        await ctx.send(msg)


# Star an item of specified level from the specified starting star to ending star
@bot.command(aliases=['sf', 'starforce'])
async def star(ctx, start_star: int = None, end_star: int = None, item_level: typing.Optional[int] = 150, *, safeguard: typing.Optional[str] = 'n'):
    if start_star is None or end_star is None:
        await ctx.send('Must provide star numbers to start and end at')
    else:
        username = ctx.author.name
        msg = await gbm_sql.starforce_message(username, start_star, end_star, item_level, safeguard)
        await ctx.send(msg)


# Read in the unique bot ID and run bot
def read_id():
    with open('gamble_bot_ID.txt', 'r') as file:
        return file.readline()


bot_id = read_id()
bot.run(bot_id)

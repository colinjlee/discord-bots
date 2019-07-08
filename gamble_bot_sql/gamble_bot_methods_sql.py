import random
import blackjack
import asyncio
from math import ceil
from gamble_bot_stats_sql import GambleBotStatsSQL


# Things to do with stats
stats = GambleBotStatsSQL()

# Dictionary mapping unique user ID to a blackjack game
bjGames = {}

# Starforcing stuff
normal_sf_succ = [0.95, 0.90, 0.85, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60, 0.55, 0.45,
                  0.35, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.30, 0.03, 0.02, 0.01]

destroy_sf_succ = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.007, 0.014, 0.014, 0.021,
                   0.021, 0.021, 0.028, 0.028, 0.07, 0.07, 0.194, 0.294, 0.396]

guard_boom_sf_succ = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 16
                      0, 0.021, 0.028, 0.028, 0.07, 0.07, 0.194, 0.294, 0.396]

keep_if_fail = {0, 1, 2, 3, 4, 5, 10, 15, 20}


# Calculate meso cost and boom count for starforcing from 0 up to specified star
# Return pair for meso cost and number of times the item boomed
async def starforce_cost(start_star, end_star, item_level, safeguard_bool):
    global normal_sf_succ, destroy_sf_succ, keep_if_fail

    meso_limit = 250000000000000  # 250 tril
    num_failed = 0
    num_boomed = 0
    meso_cost = 0
    total_fail = 0
    total_succ = 0
    curr_star = start_star

    # Start starforcing
    while curr_star < end_star:
        # Avoid crashing...
        if meso_cost >= meso_limit:
            return meso_cost, num_boomed, total_succ, total_fail, -1
        # Calculate meso cost
        # Formula for 0 to 10 stars is specifically for lvl 150 items since idk general one
        # But cost of 0 to 10 is relatively low/negligible compared to 10+
        if curr_star < 10:
            cost = (136000 * (curr_star + 1)) - (1000 * curr_star)
        elif curr_star < 15:
            cost = 1000 + item_level**3 * (curr_star + 1)**2.7 / 400
        elif curr_star < 18:
            cost = 1000 + item_level**3 * (curr_star + 1)**2.7 / 120
        elif curr_star < 20:
            cost = 1000 + item_level**3 * (curr_star + 1)**2.7 / 110
        else:
            cost = 1000 + item_level**3 * (curr_star + 1)**2.7 / 100
        # Safeguard from 12 to 17 doubles cost
        if 12 <= curr_star <= 16 and safeguard_bool:
            cost *= 2
        meso_cost += cost

        # Safeguarding until 17 or not
        if safeguard_bool:
            boom_if_greater = 1 - guard_boom_sf_succ[curr_star]
        else:
            boom_if_greater = 1 - destroy_sf_succ[curr_star]
        succ_attempt = random.uniform(0, 1)
        # Failed twice in a row, 100% for next star
        if num_failed == 2:
            curr_star += 1
            num_failed = 0
        # Success
        elif succ_attempt < normal_sf_succ[curr_star]:
            curr_star += 1
            num_failed = 0
            total_succ += 1
        # Fail, no boom
        elif succ_attempt < boom_if_greater:
            total_fail += 1
            # Keep current star or not
            if curr_star not in keep_if_fail:
                curr_star -= 1
                num_failed += 1
            else:
                num_failed = 0
        # Boom
        else:
            curr_star = 0
            num_failed = 0
            num_boomed += 1
        await asyncio.sleep(0.01)

    return meso_cost, num_boomed, total_succ, total_fail, 1


# String message for starforcing
async def starforce_message(username, start_star, end_star, item_level, safeguard):
    msg = []

    # Check legitimate starting star number
    if start_star < 0:
        start_star = 0

    # Check item level correspondence with max star count
    if item_level < 95 and end_star > 5:
        end_star = 5
    elif item_level < 108 and end_star > 8:
        end_star = 8
    elif item_level < 118 and end_star > 10:
        end_star = 10
    elif item_level < 128 and end_star > 15:
        end_star = 15
    elif item_level < 138 and end_star > 20:
        end_star = 20
    else:
        # Check legitimate ending star number
        if end_star > 25:
            end_star = 25
            
    msg.append(f'**__Max number of stars for an item of level {item_level} is {end_star}__**\n')
    
    # Check if anything to starforce
    if start_star > 24 or start_star >= end_star:
        return 'Nothing more to starforce'

    if safeguard == 'y':
        info = await starforce_cost(start_star, end_star, item_level, True)
    else:
        info = await starforce_cost(start_star, end_star, item_level, False)
    meso_cost = info[0]
    num_boomed = info[1]
    total_succ = info[2]
    total_fail = info[3]
    total_tries = total_succ + total_fail

    suffix = ''
    # Trillion
    if meso_cost >= 1000000000000:
        suffix = '(trillion)'
    # Billion
    elif meso_cost >= 1000000000:
        suffix = '(billion)'
    # Million
    elif meso_cost >= 1000000:
        suffix = '(million)'

    # Check if meso cap reached
    if info[4] < 0:
        msg.append('**Note: Computation stopped early**\n')
    else:
        msg.append(f"__{username.title()}'s stats to go from {start_star} to {end_star} star on a level {item_level} item")
        if safeguard == 'y':
            msg.append(' while safeguarding:__\n')
        else:
            msg.append(' without safeguarding:__\n')
    msg.append(f'Meso cost: {meso_cost:,.0f} {suffix}\n')
    msg.append(f'Boom count: {num_boomed:,.0f}\n')
    msg.append(f'Total successes: {total_succ:,.0f}\n')
    msg.append(f'Total failures: {total_fail:,.0f}\n')
    msg.append(f'Total tries: {total_tries:,.0f}\n')
    return ''.join(msg)


# Start a blackjack game for the user
def bj(username, user_id, bet_amt):
    global bjGames

    if user_id in bjGames:
        msg = ["**__You're already in a game!__**\n", str(bjGames[user_id])]
        return ''.join(msg), bjGames[user_id]
    else:
        if bet_amt < 0:
            bet_amt = 0

        # Make sure player has enough money to bet
        user_money = stats.get_user_money(username, user_id)
        if user_money < bet_amt:
            msg = [f'You do not have enough money to bet ${bet_amt}\n', f'You currently have ${user_money}']
            return ''.join(msg), None
        else:
            new_bj_game = blackjack.Blackjack(username, bet_amt)
            bjGames[user_id] = new_bj_game
            msg = [str(new_bj_game)]

            # Check game state after player move
            if new_bj_game.game_state != -1:
                del bjGames[user_id]
                new_bj_game.game_state = 1
                msg.append(f'\n**You currently have ${user_money}**')
            return ''.join(msg), new_bj_game


# Hit during a game of blackjack
def bj_hit(username, user_id):
    game = bjGames.get(user_id)
    
    if user_id in bjGames:
        game.player_hit()
        msg = [str(game)]

        # Check game state after player move
        if game.game_state != -1:
            del bjGames[user_id]
            user_money = stats.get_user_money(username, user_id)
            msg.append(f'\n**You currently have ${user_money}**')
    else:
        msg = ['You are currently not in a game of blackjack']
    return ''.join(msg), game


# Stand during a game of blackjack
def bj_stand(username, user_id):
    game = bjGames.get(user_id)
    
    if user_id in bjGames:
        game.player_stand()
        msg = [str(game)]

        # Check game state after player move
        if game.game_state != -1:
            del bjGames[user_id]
            user_money = stats.get_user_money(username, user_id)
            msg.append(f'\n**You currently have ${user_money}**')
    else:
        msg = ['You are currently not in a game of blackjack']
    return ''.join(msg), game


# Double down during a game of blackjack
def bj_double_down(username, user_id):
    game = bjGames.get(user_id)
    
    if user_id in bjGames:
        user_money = stats.get_user_money(username, user_id)
        user_bet = game.player_bet

        # Make sure player has enough money to double bet
        if user_money < user_bet * 2:
            msg = [f'You do not have enough money to double your current bet of ${user_bet}']
        else:
            game.player_dd()
            msg = [str(game)]

            # Check game state after player move
            if game.game_state != -1:
                del bjGames[user_id]
                msg.append(f'\n**You currently have ${user_money}**')
    else:
        msg = ['You are currently not in a game of blackjack']
    return ''.join(msg), game


# Update blackjack stats
def bj_update(username, user_id, game):
    if game.game_state != -1:
        stats.update_user_bj_stat(username, user_id, game)


# Return marvel/philo stats result through string
def philo_marvel_stats(username, user_id):
    return stats.philo_marvel_stats(username, user_id)


# Return blackjack stats result through string
def bj_stats(username, user_id):
    return stats.bj_stats(username, user_id)


# Reset user stats for specified data
# (1) philo (2) marvel (3) blackjack or (4) all
# Return a string indicating success
def reset_stats(username, user_id, stats_type):
    return stats.reset_stats(username, user_id, stats_type)


# Give everyone in blackjack sheet money
def give_everyone_money(amount):
    stats.give_everyone_money(amount)


# Returns a string of the notable items won from philo or marvel
def notable_items(lucky_list, got_lucky):
    if got_lucky:
        msg = ['\n**__Notable items:__**\n']
        for item in lucky_list:
            if lucky_list[item] > 0:
                msg.append(item.title().replace("'S", "'s") + ': ' + str(lucky_list[item]) + '\n')
        return ''.join(msg)
    else:
        return '\n**__No notable items__**'


# Roll a specified number of philosopher books, up to 165
# Return the results through an array
def philo_roll(username, user_id, num_rolls):
    philo_list1 = stats.philo_list1
    philo_list2 = stats.philo_list2

    # Lucky items in philo
    lucky = stats.philoLuckyList
    got_lucky = False
    messages = []
    msg = [f"**__{username.title()}'s philo run:__**\n"]

    # Min roll of 1, max of 165 rolls
    if num_rolls < 1:
        messages.append('Amount of rolls must be positive')
        return messages
    elif num_rolls > 165:
        msg.append('**Max of 165 philo books (15 packs)**\n')
        num_rolls = 165

    # Roll the specified amount of books
    for i in range(1, num_rolls + 1):
        temp = f'**[{str(i)}]** '
        item1 = random.choice(philo_list1)
        item2 = random.choice(philo_list2)
        item1_name = item1.title().replace("'S", "'s").replace('9Th', '9th')
        item2_name = item2.title().replace("'S", "'s").replace('9Th', '9th')
        # Discord syntax to bold and underline lucky items
        if item1 in lucky:
            temp += '**__' + item1_name + '__**, '
            lucky[item1] += 1
            stats.update_user_item_stat(username, user_id, item1, 1, 'p')
            got_lucky = True
        else:
            temp += item1_name + ', '
        if item2 in lucky:
            temp += '**__' + item2_name + '__** '
            lucky[item2] += 1
            stats.update_user_item_stat(username, user_id, item2, 1, 'p')
            got_lucky = True
        else:
            temp += item2_name + ' '
        # Check for bot message length limit of 2,000 chars
        if sum(len(s) for s in msg) + len(temp) > 2000:
            messages.append(''.join(msg))
            msg = [temp]
        else:
            msg.append(temp)

    # Highlight lucky items and update user stat
    temp = notable_items(lucky, got_lucky)
    stats.update_user_item_stat(username, user_id, 'rolls', num_rolls, 'p')

    # Another final check for message length limit
    if sum(len(s) for s in msg) + len(temp) > 2000:
        messages.append(''.join(msg))
        msg = [temp]
    else:
        msg.append(temp)
    messages.append(''.join(msg))
    return messages


# Roll philo books until the specified item is found
# These rolls are not recorded in stats
# Return the results through a string
def philo_find(item):
    philo_list1 = stats.philo_list1
    philo_list2 = stats.philo_list2
    counter = 0
    found = False
    item = item.strip().lower()

    # Roll until item is found
    if item in philo_list1 or item in philo_list2:
        while not found:
            counter += 1
            if item in philo_list1:
                result = random.choice(philo_list1)
            else:
                result = random.choice(philo_list2)
            if item == result:
                found = True
    else:
        return 'Invalid item'

    # Calculate spending costs and return results
    costs = stats.philo_marvel_spendings(counter, 0)
    low_money = costs[0]
    high_money = costs[1]
    item_name = item.title().replace("'S", "'s").replace('9Th', '9th')
    msg = [f'It took {counter:,d} book(s) to get the item: {item_name}\n',
           f'{counter:,d} book(s) = ${low_money:,.2f} ~ ${high_money:,.2f}']
    return ''.join(msg)


# Roll marvel a specified number of times, up to 110
# Return the results through an array
def marvel_roll(username, user_id, num_rolls):
    marvel_list1 = stats.marvel_list1
    marvel_list2 = stats.marvel_list2
    marvel_list3 = stats.marvel_list3

    # Lucky items in marvel
    lucky = stats.marvelLuckyList
    got_lucky = False
    messages = []
    msg = [f"**__{username.title()}'s marvel run:__**\n"]

    # Min roll of 1, max roll of 110
    if num_rolls < 1:
        messages.append('Amount of rolls must be positive')
        return messages
    elif num_rolls > 110:
        msg.append('**Max of 110 marvel spins (10 packs)**\n')
        num_rolls = 110

    # Roll the specified amount
    for i in range(1, num_rolls + 1):
        temp = f'**[{str(i)}]** '
        item1 = random.choice(marvel_list1)
        item2 = random.choice(marvel_list2)
        item3 = random.choice(marvel_list3)
        item1_name = item1.title().replace("'S", "'s").replace('9Th', '9th')
        item2_name = item2.title().replace("'S", "'s").replace('9Th', '9th')
        item3_name = item3.title().replace("'S", "'s").replace('9Th', '9th')
        # Discord syntax to bold and underline lucky items
        if item1 in lucky:
            temp += '**__' + item1_name + '__**, '
            lucky[item1] += 1
            stats.update_user_item_stat(username, user_id, item1, 1, 'm')
            got_lucky = True
        else:
            temp += item1_name + ', '
        if item2 in lucky:
            temp += '**__' + item2_name + '__**, '
            lucky[item2] += 1
            stats.update_user_item_stat(username, user_id, item2, 1, 'm')
            got_lucky = True
        else:
            temp += item2_name + ', '
        if item3 in lucky:
            temp += '**__' + item3_name + '__** '
            lucky[item3] += 1
            stats.update_user_item_stat(username, user_id, item3, 1, 'm')
            got_lucky = True
        else:
            temp += item3_name + ' '
        # Check for bot message length limit of 2,000 chars
        if sum(len(s) for s in msg) + len(temp) > 2000:
            messages.append(''.join(msg))
            msg = [temp]
        else:
            msg.append(temp)

    # Highlight lucky items and update user stats
    temp = notable_items(lucky, got_lucky)
    stats.update_user_item_stat(username, user_id, 'rolls', num_rolls, 'm')

    # Another final check for message length limit
    if sum(len(s) for s in msg) + len(temp) > 2000:
        messages.append(''.join(msg))
        messages.append(temp)
    else:
        msg.append(temp)
        messages.append(''.join(msg))
    return messages


# Roll marvel until the specified item is found
# These rolls are not recorded in stats
# Return results through a string
def marvel_find(item):
    marvel_list1 = stats.marvel_list1
    marvel_list2 = stats.marvel_list2
    marvel_list3 = stats.marvel_list3
    counter = 0
    found = False
    item = item.strip().lower()

    # Roll until item is found
    if item in marvel_list1 or item in marvel_list2 or item in marvel_list3:
        while not found:
            counter += 1
            if item in marvel_list1:
                result = random.choice(marvel_list1)
            elif item in marvel_list2:
                result = random.choice(marvel_list2)
            else:
                result = random.choice(marvel_list3)
            if item == result:
                found = True
    else:
        return 'Invalid item'

    # Calculate spending costs and return results
    costs = stats.philo_marvel_spendings(counter, 1)
    low_money = costs[0]
    high_money = costs[1]
    item_name = item.title().replace("'S", "'s").replace('9Th', '9th')
    msg = [f'It took {counter:,d} spin(s) to get the item: {item_name}\n',
           f'{counter:,d} spin(s) = ${low_money:,.2f} ~ ${high_money:,.2f}']
    return ''.join(msg)


# Roll a die with specified number of sides, a specified number of times
# Return the results through an array
def roll(num_rolls, num_sides):
    results = [0] * num_sides

    for x in range(num_rolls):
        rand = random.randint(1, num_sides)
        results[rand - 1] += 1

    return results


# Flip a coin the specified number of times
# Return the results through a string
def flip(num_flips):
    # Amount of flips must be positive
    if num_flips < 1:
        return 'Amount of rolls must be positive or empty to use default value'
    # Flip just once
    elif num_flips == 1:
        rand = random.randint(0, 1)
        if rand == 0:
            return 'Heads'
        else:
            return 'Tails'
    # Different message format for flipping more than once
    else:
        # String to be sent after results
        msg = []
        if num_flips > 100000:
            msg.append('**Max of 100,000 flips**\n')
            num_flips = 100000

        # Get and send results
        results = roll(num_flips, 2)
        head = results[0]
        tail = results[1]
        h_rate = head / num_flips * 100
        t_rate = tail / num_flips * 100

        msg.append(f'Heads: {head:,d} ({h_rate:.2f}%)\nTails: {tail:,d} ({t_rate:.2f}%)')
        return ''.join(msg)


# Flip a coin with an initial guess
# Return the results through a string
def flip_guess(guess):
    # Set of acceptable string values for guess
    allowed_guesses = {'head', 'heads', 'h', 'tail', 'tails', 't'}
    guess = guess.strip()  # Remove leading and trailing whitespace
    guess = guess.lower()  # make all letters lowercase
    msg = ['You guessed {} and it flipped {}\n']

    # Valid guess
    if guess in allowed_guesses:
        rand = random.randint(0, 1)
        if guess.startswith('h'):
            guess = 'heads'
        else:
            guess = 'tails'

        if rand == 0:
            result = 'heads'
        else:
            result = 'tails'

        if guess == result:
            msg.append('You were **right**')
        else:
            msg.append('You were **wrong**')

        return ''.join(msg).format(guess, result)
    # Invalid guess
    else:
        return "Invalid guess. Try again with a guess of 'h' or 't'"


# Roll a die with specified number of sides, a specified number of times
# Return the results through an array due to bot message length
def roll_die(num_rolls, num_sides):
    # Array of results to be sent
    messages = []
    # Amount of flips and face count must be positive
    if num_rolls < 1 or num_sides < 1:
        messages.append('Amount of rolls and die side count must be positive or empty to use default values')
    # Roll just once
    elif num_rolls == 1:
        rand = random.randint(1, num_sides)
        messages.append(rand)
    # Different message format for rolling more than once
    else:
        # String of results to be sent
        msg = []
        if num_sides > 100:
            msg.append('**Max of 100 sided die**\n')
            num_sides = 100
        if num_rolls > 100000:
            msg.append('**Max of 100,000 rolls**\n')
            num_rolls = 100000

        # Get and send results. Note bots have max length of 2,000 chars per msg
        results = roll(num_rolls, num_sides)
        for x in range(0, num_sides):
            if results[x] > 0:
                res = f'{x + 1:,d}: {results[x]:,d} ({(results[x] / num_rolls * 100):.2f}%)\n'
                if sum(len(s) for s in msg) + len(res) > 2000:
                    messages.append(''.join(msg))
                    msg = [res]
                else:
                    msg.append(res)
        messages.append(''.join(msg))
    return messages


# Calculate days needed to max arcane force symbols
def af(start_lvl, end_lvl, curr_progress, daily_rate):
    cap_progress = start_lvl * start_lvl + 11
    if end_lvl < 1 or start_lvl < 1 or end_lvl > 20 or start_lvl >= 20:
        return 'Starting and ending levels must be positive and at most 20'
    elif end_lvl < start_lvl:
        return 'Ending level must be greater than or equal to the starting level'
    elif curr_progress < 0 or curr_progress > cap_progress:
        return f'Current number of symbols used must be non-negative and less than {cap_progress}'
    elif daily_rate < 0:
        return 'Daily rate must be non-negative'
    else:
        symbols_needed = 0
        for i in range(start_lvl, end_lvl):
            symbols_needed += i * i + 11
        symbols_needed -= curr_progress
        days_needed = symbols_needed / daily_rate
        msg = [f'Leveling up from lvl {start_lvl} ({curr_progress}/{cap_progress}) to lvl {end_lvl} needs {symbols_needed} total symbols\n',
               f'With a rate of {daily_rate} symbols per day, {ceil(days_needed)} ({days_needed:.2f}) days are needed']
        return ''.join(msg)

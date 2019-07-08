import gspread
from oauth2client.service_account import ServiceAccountCredentials
import sqlite3


# Google sheets things
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets', 
         'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
client = gspread.authorize(creds)


class GambleBotStatsSQL:
    def __init__(self):
        # Connect to database
        self.stats_connector = sqlite3.connect('gbUserStats.db')
        self.stats_cursor = self.stats_connector.cursor()

        # Google sheets containing public rates of philosopher book and marvel machine
        # Philo rates: http://maplestory.nexon.net/micro-site/42030
        # Marvel rates: http://maplestory.nexon.net/micro-site/39184
        self.philo_sheet = client.open('Philosopher Book Rates').worksheets()[-1]
        self.marvel_sheet = client.open('Marvel Machine Rates').worksheets()[-1]

        # List of marvel/philo items to roll from
        self.marvel_list1 = self.make_marvel_list1()
        self.marvel_list2 = self.make_marvel_list2()
        self.marvel_list3 = self.make_marvel_list3()
        self.philo_list1 = self.make_philo_list1()
        self.philo_list2 = self.make_philo_list2()

        # Mapping of column names to official item name
        self.marvel_item_mapping = self.map_marvel_items()  # Includes num rolls
        self.philo_item_mapping = self.map_philo_items()    # Includes num rolls
        self.bjItemMapping = self.map_bj_items()

        # List of lucky items possible to get in marvel/philo
        self.marvelLuckyList = {k: 0 for k in self.marvel_item_mapping.keys()}
        self.philoLuckyList = {k: 0 for k in self.philo_item_mapping.keys()}

    # Close the connections
    def __del__(self):
        self.stats_connector.close()

    # Map marvel attributes to official item name
    # Return the mapping
    def map_marvel_items(self):
        mapping = {}
        self.stats_cursor.execute('pragma table_info(marvel_stats)')
        item_list = self.stats_cursor.fetchall()

        for elt in item_list[2:]:  # Skipping id, name
            word = elt[1]
            new_word = word.replace('_', ' ')
            new_word = new_word.replace('One', '1')
            new_word = new_word.replace('Hundred Thousand', '100,000')
            new_word = new_word.replace(' Male', ' (Male)')
            new_word = new_word.replace(' Female', ' (Female)')
            mapping[new_word] = word
        return mapping

    # Map philo attributes to official item name
    # Return the mapping
    def map_philo_items(self):
        mapping = {}
        self.stats_cursor.execute('pragma table_info(philo_stats)')
        item_list = self.stats_cursor.fetchall()

        for elt in item_list[2:]:  # Skipping id, name
            word = elt[1]
            new_word = word.replace('battle_roid', 'battle-roid')
            new_word = new_word.replace('_f_', ' (f) ')
            new_word = new_word.replace('_m_', ' (m) ')
            new_word = new_word.replace('_', ' ')
            mapping[new_word] = word
        return mapping

    # Map bj attributes to prettier text
    # Return the mapping
    def map_bj_items(self):
        mapping = {}
        self.stats_cursor.execute('pragma table_info(bj_stats)')
        item_list = self.stats_cursor.fetchall()

        for elt in item_list[2:]:  # Skipping id, name
            word = elt[1]
            new_word = word.replace('_', ' ').title()
            mapping[new_word] = word
        return mapping

    # Return list of philo items possible to get from list 1
    def make_philo_list1(self):
        list1 = []
        philo_item_list1 = self.philo_sheet.col_values(3)
        philo_rate_list1 = self.philo_sheet.col_values(4)

        # Make lists containing the philo items proportionate to their rate
        for i in range(1, len(philo_item_list1)):
            # Make the items lowercase for easier matching
            philo_item_list1[i] = philo_item_list1[i].lower()
            item = philo_item_list1[i]
            # Make the %rate an integer with no decimal values
            rate = float(philo_rate_list1[i][:-1])*100
            # Add the item multiple times proportionate to their rate
            list1 += [item]*int(rate)

        return list1

    # Return list of philo items possible to get from list 2
    def make_philo_list2(self):
        list2 = []
        philo_item_list2 = self.philo_sheet.col_values(6)
        philo_rate_list2 = self.philo_sheet.col_values(7)

        for i in range(1, len(philo_item_list2)):
            philo_item_list2[i] = philo_item_list2[i].lower()
            item = philo_item_list2[i]
            rate = float(philo_rate_list2[i][:-1])*100
            list2 += [item]*int(rate)

        return list2

    # Return list of marvel items possible to get from list 1
    def make_marvel_list1(self):
        list1 = []
        marvel_item_list1 = self.marvel_sheet.col_values(3)
        marvel_rate_list1 = self.marvel_sheet.col_values(4)

        # Similar to philo
        # Note that some item rates from marvel go up to 3 decimal places
        for i in range(1, len(marvel_item_list1)):
            marvel_item_list1[i] = marvel_item_list1[i].lower()
            item = marvel_item_list1[i]
            # Accommodate 3 decimal places by *1000
            rate = float(marvel_rate_list1[i][:-1])*1000
            list1 += [item]*int(rate)

        return list1

    # Return list of marvel items possible to get from list 2
    def make_marvel_list2(self):
        list2 = []
        marvel_item_list2 = self.marvel_sheet.col_values(6)
        marvel_rate_list2 = self.marvel_sheet.col_values(7)

        for i in range(1, len(marvel_item_list2)):
            marvel_item_list2[i] = marvel_item_list2[i].lower()
            item = marvel_item_list2[i]
            rate = float(marvel_rate_list2[i][:-1])*1000
            list2 += [item]*int(rate)

        return list2

    # Return list of marvel items possible to get from list 3
    def make_marvel_list3(self):
        list3 = []
        marvel_item_list3 = self.marvel_sheet.col_values(9)
        marvel_rate_list3 = self.marvel_sheet.col_values(10)

        for i in range(1, len(marvel_item_list3)):
            marvel_item_list3[i] = marvel_item_list3[i].lower()
            item = marvel_item_list3[i]
            rate = float(marvel_rate_list3[i][:-1])*1000
            list3 += [item]*int(rate)

        return list3

    # Update user's item stats for philo/marvel
    def update_user_item_stat(self, username, user_id, item, inc_amt, str_indicator):
        with self.stats_connector:
            # Update philo item
            if str_indicator == 'p':
                self.add_new_user(username, user_id, 'p')
                sql_item = self.philo_item_mapping[item]
                self.stats_cursor.execute('''UPDATE philo_stats
                                        SET ''' + sql_item + ' = IFNULL(' + sql_item + ''', 0) + :amount
                                        WHERE user_id = :id''', 
                                          {'amount': inc_amt, 'id': user_id})
                # Update name if needed
                self.stats_cursor.execute('''UPDATE philo_stats
                                        SET user_name = :name
                                        WHERE user_id = :id AND user_name <> :name''', 
                                          {'id': user_id, 'name': username})
            # Update marvel item
            else:
                self.add_new_user(username, user_id, 'm')
                sql_item = self.marvel_item_mapping[item]
                self.stats_cursor.execute('''UPDATE marvel_stats
                                        SET ''' + sql_item + ' = IFNULL(' + sql_item + ''', 0) + :amount
                                        WHERE user_id = :id''', 
                                          {'amount': inc_amt, 'id': user_id})
                # Update name if needed
                self.stats_cursor.execute('''UPDATE marvel_stats
                                        SET user_name = :name
                                        WHERE user_id = :id AND user_name <> :name''', 
                                          {'id': user_id, 'name': username})

    # Update user's blackjack stats
    def update_user_bj_stat(self, username, user_id, game):
        self.add_new_user(username, user_id, 'bj')
        user_bet_amt = game.player_bet

        with self.stats_connector:
            # User got blackjack
            if game.player_bj:
                self.stats_cursor.execute('''UPDATE bj_stats
                                        SET blackjacks = IFNULL(blackjacks, 0) + 1
                                        WHERE user_id = :id''', 
                                          {'id': user_id})
            # User won
            if game.game_state == 0:
                self.stats_cursor.execute('''UPDATE bj_stats
                                        SET games_played = IFNULL(games_played, 0) + 1,
                                        games_won = IFNULL(games_won, 0) + 1,
                                        current_money = IFNULL(current_money, 0) + :bet,
                                        total_earnings = IFNULL(total_earnings, 0) + :bet
                                        WHERE user_id = :id''', 
                                          {'bet': user_bet_amt, 'id': user_id})
            # User lost
            elif game.game_state == 1:
                self.stats_cursor.execute('''UPDATE bj_stats
                                        SET games_played = IFNULL(games_played, 0) + 1,
                                        games_lost = IFNULL(games_won, 0) + 1,
                                        current_money = IFNULL(current_money, 0) - :bet,
                                        total_earnings = IFNULL(total_earnings, 0) - :bet
                                        WHERE user_id = :id''', 
                                          {'bet': user_bet_amt, 'id': user_id})
            # User tied
            elif game.game_state == 2:
                self.stats_cursor.execute('''UPDATE bj_stats
                                        SET games_played = IFNULL(games_played, 0) + 1,
                                        games_tied = IFNULL(games_won, 0) + 1
                                        WHERE user_id = :id''', 
                                          {'id': user_id})
            # Update name if needed
            self.stats_cursor.execute('''UPDATE bj_stats
                                    SET user_name = :name
                                    WHERE user_id = :id AND user_name <> :name''', 
                                      {'id': user_id, 'name': username})

    # Return user's current money
    def get_user_money(self, username, user_id):
        # Check if data exists
        self.stats_cursor.execute('SELECT user_id FROM bj_stats WHERE user_id = :id', {'id': user_id})
        if len(self.stats_cursor.fetchall()) == 0:
            return 0
        else:
            self.stats_cursor.execute('SELECT current_money FROM bj_stats WHERE user_id = :id', 
                                      {'id': user_id})
            return self.stats_cursor.fetchone()[0]

    # Give everyone in blackjack sheet money
    def give_everyone_money(self, amount):
        with self.stats_connector:
            self.stats_cursor.execute('UPDATE bj_stats SET current_money = current_money + :amount', 
                                      {'amount': amount})

    # Calculate philo or marvel spendings
    # Return result through pair
    def philo_marvel_spendings(self, num_rolls, str_indicator):
        price = -1
        # p for philo, m for marvel
        if str_indicator == 'p':
            price = 2.6
        elif str_indicator == 'm':
            price = 4.9

        # Calculate and return costs
        low_money = int(num_rolls / 11) * int(price * 10) + (num_rolls % 11) * price
        high_money = num_rolls*price
        return low_money, high_money

    # Philo and marvel stats 
    # Return result through string 
    def philo_marvel_stats(self, username, user_id):
        self.add_new_user(username, user_id, 'm')
        self.add_new_user(username, user_id, 'p')
        msg = ''

        # Marvel stats
        self.stats_cursor.execute('SELECT rolls FROM marvel_stats WHERE user_id = :id', {'id': user_id})
        marvel_rolls = self.stats_cursor.fetchone()[0]
        costs = self.philo_marvel_spendings(marvel_rolls, 'm')
        low_money = costs[0]
        high_money = costs[1]
        msg += f"__{username.title()}'s Marvel Machine Statistics:__\nTotal amount of spins: {marvel_rolls} "
        msg += f'(${low_money:,.2f} ~ ${high_money:,.2f})\n'

        self.stats_cursor.execute('SELECT * FROM marvel_stats WHERE user_id = :id', {'id': user_id})
        user_values = self.stats_cursor.fetchone()[3:]     # Skip id, name, rolls
        marvel_item_row = [*self.marvel_item_mapping][1:]  # Skip rolls

        for i in range(0, len(marvel_item_row)):
            item = marvel_item_row[i].title().replace("'s", "'s")
            user_amount = user_values[i]
            if user_amount > 0:
                msg += f'{item}: {user_amount:,d}\n'

        # Philo stats
        self.stats_cursor.execute('SELECT rolls FROM philo_stats WHERE user_id = :id', {'id': user_id})
        philo_rolls = self.stats_cursor.fetchone()[0]
        costs = self.philo_marvel_spendings(philo_rolls, 'p')
        low_money = costs[0]
        high_money = costs[1]
        msg += f"\n__{username.title()}'s Philosopher Book Statistics:__\nTotal amount of books: {philo_rolls} "
        msg += f'(${low_money:,.2f} ~ ${high_money:,.2f})\n'

        self.stats_cursor.execute('SELECT * FROM philo_stats WHERE user_id = :id', {'id': user_id})
        user_values = self.stats_cursor.fetchone()[3:]     # Skip id, name, rolls
        philo_item_row = [*self.philo_item_mapping][1:]    # Skip rolls

        for i in range(0, len(philo_item_row)):
            item = philo_item_row[i].title().replace("'s", "'s")
            user_amount = user_values[i]
            if user_amount > 0:
                msg += f'{item}: {user_amount:,d}\n'

        return msg

    # Return result through string
    def bj_stats(self, username, user_id):
        self.add_new_user(username, user_id, 'bj')
        msg = f"__{username.title()}'s Blackjack Statistics:__\n"

        # Check if data exists
        self.stats_cursor.execute('SELECT user_id FROM bj_stats WHERE user_id = :id', {'id': user_id})
        if len(self.stats_cursor.fetchall()) == 0:
            msg += 'You have not played a game of blackjack yet'
            return msg
        else:
            # Blackjack stats
            self.stats_cursor.execute('SELECT * FROM bj_stats WHERE user_id = :id', {'id': user_id})
            user_values = self.stats_cursor.fetchone()[2:]  # Skip id, name
            bj_item_row = [*self.bjItemMapping]

            for i in range(0, len(bj_item_row)):
                item = bj_item_row[i].title()
                user_amount = user_values[i]
                msg += f'{item}: {user_amount:,d}\n'

            return msg

    # Reset user stats for specified data
    # (1) marvel (2) philo (3) blackjack or (4) all
    # Return a string indicating success
    def reset_stats(self, username, user_id, stats_type):
        # Indicators of which stats to reset
        philo_reset = marvel_reset = bj_reset = False

        if stats_type == 4:
            philo_reset = marvel_reset = bj_reset = True
        elif stats_type == 3:
            bj_reset = True
        elif stats_type == 2:
            philo_reset = True
        elif stats_type == 1:
            marvel_reset = True
        else:
            return 'Invalid type'

        msg = f"**__Attempted to reset {username.title()}'s specified stats:__**\n"
        # Reset desired stats
        if philo_reset:
            with self.stats_connector:
                self.stats_cursor.execute('SELECT user_id FROM philo_stats WHERE user_id = :id', {'id': user_id})
                if len(self.stats_cursor.fetchall()) == 0:
                    self.add_new_user(username, user_id, 'p')
                    msg += 'No philosopher book stats to reset\n'
                else:
                    for var in [*self.philo_item_mapping.values()]:
                        self.stats_cursor.execute('UPDATE philo_stats SET ' + var + ' = 0 WHERE user_id = :id', 
                                                  {'id': user_id})
                    msg += 'Successfully reset philosopher book stats\n'
        if marvel_reset:
            with self.stats_connector:
                self.stats_cursor.execute('SELECT user_id FROM marvel_stats WHERE user_id = :id', {'id': user_id})
                if len(self.stats_cursor.fetchall()) == 0:
                    self.add_new_user(username, user_id, 'm')
                    msg += 'No marvel machine stats to reset\n'
                else:
                    for var in [*self.marvel_item_mapping.values()]:
                        self.stats_cursor.execute('UPDATE marvel_stats SET ' + var + ' = 0 WHERE user_id = :id', 
                                                  {'id': user_id})
                    msg += 'Successfully reset marvel machine stats\n'
        if bj_reset:
            with self.stats_connector:
                self.stats_cursor.execute('SELECT user_id FROM bj_stats WHERE user_id = :id', {'id': user_id})
                if len(self.stats_cursor.fetchall()) == 0:
                    self.add_new_user(username, user_id, 'bj')
                    msg += 'No blackjack stats to reset\n'
                else:
                    self.stats_cursor.execute('UPDATE bj_stats SET current_money = 100 WHERE user_id = :id', 
                                              {'id': user_id})
                    for var in [*self.bjItemMapping.values()][1:]:  # Skip money
                        self.stats_cursor.execute('UPDATE bj_stats SET ' + var + ' = 0 WHERE user_id = :id', 
                                                  {'id': user_id})
                    msg += 'Successfully reset blackjack stats\n'

        return msg[:-1]

    # Add new user to database if not inside already
    # (p) philo (m) marvel (bj) blackjack
    # Idk how to make upsert work...
    def add_new_user(self, username, user_id, str_indicator):
        new_user = str((user_id, username))
        if str_indicator == 'p':
            with self.stats_connector:
                self.stats_cursor.execute('SELECT user_id FROM philo_stats WHERE user_id = :id', {'id': user_id})
                if len(self.stats_cursor.fetchall()) == 0:
                    self.stats_cursor.execute('INSERT INTO philo_stats(user_id, user_name) VALUES' + new_user)
        elif str_indicator == 'm':
            with self.stats_connector:
                self.stats_cursor.execute('SELECT user_id FROM marvel_stats WHERE user_id = :id', {'id': user_id})
                if len(self.stats_cursor.fetchall()) == 0:
                    self.stats_cursor.execute('INSERT INTO marvel_stats(user_id, user_name) VALUES' + new_user)
        elif str_indicator == 'bj':
            with self.stats_connector:
                self.stats_cursor.execute('SELECT user_id FROM bj_stats WHERE user_id = :id', {'id': user_id})
                if len(self.stats_cursor.fetchall()) == 0:
                    self.stats_cursor.execute('INSERT INTO bj_stats(user_id, user_name) VALUES' + new_user)

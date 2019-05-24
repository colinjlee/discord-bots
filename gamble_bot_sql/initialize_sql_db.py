import sqlite3

statsConnector = sqlite3.connect("gbUserStats.db")
statsCursor = statsConnector.cursor()

# Doesn't accept numbers, commas, parentheses,
# hyphens, or apostrophes in attribute name
# with statsConnector:
#     statsCursor.execute("""CREATE TABLE marvel_stats(
#                             user_id BIGINT PRIMARY KEY,
#                             user_name TEXT NOT NULL,
#                             rolls INT DEFAULT 0,
#                             one_mil_maple_points INT DEFAULT 0,
#                             frenzy_totem INT DEFAULT 0,
#                             dark_avenger_totem INT DEFAULT 0,
#                             dark_doom_totem	INT DEFAULT 0,
#                             dark_grin_totem INT DEFAULT 0,
#                             dark_hellia_totem INT DEFAULT 0,
#                             lucids_earrings_coupon INT DEFAULT 0,
#                             firestarter_ring INT DEFAULT 0,
#                             the_ring_of_torment_coupon INT DEFAULT 0,
#                             permanent_pendant_slot INT DEFAULT 0,
#                             permanent_hyper_teleport_rock_coupon INT DEFAULT 0,
#                             battleroid_male INT DEFAULT 0,
#                             battleroid_female INT DEFAULT 0,
#                             outlaw_heart INT DEFAULT 0,
#                             hundred_thousand_maple_points_chip INT DEFAULT 0,
#                             wolf_underling_familiar INT DEFAULT 0
#                         )""")
#
#     statsCursor.execute("""CREATE TABLE philo_stats(
#                             user_id BIGINT PRIMARY KEY,
#                             user_name TEXT NOT NULL,
#                             rolls INT DEFAULT 0,
#                             battle_roid_f_coupon INT DEFAULT 0,
#                             battle_roid_m_coupon INT DEFAULT 0,
#                             outlaw_heart INT DEFAULT 0,
#                             frenzy_totem INT DEFAULT 0,
#                             firestarter_ring_coupon INT DEFAULT 0,
#                             wolf_underling_familiar INT DEFAULT 0
#                         )""")
#
#     statsCursor.execute("""CREATE TABLE bj_stats(
#                             user_id BIGINT PRIMARY KEY,
#                             user_name TEXT NOT NULL,
#                             current_money INT DEFAULT 100,
#                             total_earnings INT DEFAULT 0,
#                             blackjacks INT DEFAULT 0,
#                             games_played INT DEFAULT 0,
#                             games_won INT DEFAULT 0,
#                             games_lost INT DEFAULT 0,
#                             games_tied INT DEFAULT 0
#                         )""")


# with statsConnector:
#     statsCursor.execute("""ALTER TABLE marvel_stats ADD COLUMN breath_of_divinity_ring INT DEFAULT 0;""")
#     statsCursor.execute("""ALTER TABLE marvel_stats ADD COLUMN arcane_umbra_archer_cape INT DEFAULT 0;""")
#     statsCursor.execute("""ALTER TABLE marvel_stats ADD COLUMN arcane_umbra_knight_cape INT DEFAULT 0;""")
#     statsCursor.execute("""ALTER TABLE marvel_stats ADD COLUMN arcane_umbra_mage_cape INT DEFAULT 0;""")
#     statsCursor.execute("""ALTER TABLE marvel_stats ADD COLUMN arcane_umbra_pirate_cape INT DEFAULT 0;""")
#     statsCursor.execute("""ALTER TABLE marvel_stats ADD COLUMN arcane_umbra_thief_cape INT DEFAULT 0;""")
#     statsCursor.execute("""ALTER TABLE marvel_stats ADD COLUMN arcane_umbra_archer_gloves INT DEFAULT 0;""")
#     statsCursor.execute("""ALTER TABLE marvel_stats ADD COLUMN arcane_umbra_knight_gloves INT DEFAULT 0;""")
#     statsCursor.execute("""ALTER TABLE marvel_stats ADD COLUMN arcane_umbra_mage_gloves INT DEFAULT 0;""")
#     statsCursor.execute("""ALTER TABLE marvel_stats ADD COLUMN arcane_umbra_pirate_gloves INT DEFAULT 0;""")
#     statsCursor.execute("""ALTER TABLE marvel_stats ADD COLUMN arcane_umbra_thief_gloves INT DEFAULT 0;""")
#     statsCursor.execute("""ALTER TABLE marvel_stats ADD COLUMN arcane_umbra_knight_shoes INT DEFAULT 0;""")
#     statsCursor.execute("""ALTER TABLE marvel_stats ADD COLUMN arcane_umbra_pirate_shoes INT DEFAULT 0;""")
#     statsCursor.execute("""ALTER TABLE marvel_stats ADD COLUMN arcane_umbra_thief_shoes INT DEFAULT 0;""")

statsCursor.close()

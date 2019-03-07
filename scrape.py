from scrapeMedia import scrapeTV as scrapeTV
from legacy import create_tv_csv

shows = ['better_call_saul', 'the_americans', 'homecoming', 'this_is_us', 'bodyguard', 'all_american', 'escape_at_dannemora', 'true_detective', 'black_earth_rising', 'watership_down']

for show in shows:
    scrapeTV(show)
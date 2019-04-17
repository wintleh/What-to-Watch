from scrapeMedia import scrapeTV as scrapeTV
import datetime

# Timing the script
start = datetime.datetime.now()

data_file = './data/on_RT.txt'
f = open(data_file, 'r')

shows = f.readlines()

for show in shows:
    # Scrape the information, but remove the newline character from the end of the title
    scrapeTV(show[0:len(show)-1])

# Timing the script
end = datetime.datetime.now()
print('Start: ' + str(start) + "\nEnd: " + str(end) + '\nRuntime: ' + str(end - start))

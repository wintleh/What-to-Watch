from urllib.request import urlopen as uReq
from urllib import error as urlError
from bs4 import BeautifulSoup as soup
import http.client as httpError

def _nameToURL(name, media_type):
    '''
    Helper method to get the Rotten Tomatoes URL for the show/film
    '''

    if((media_type != 'tv') and (media_type != 'm')):
        raise ValueError('Invalid media type')
    else:
        return 'https://www.rottentomatoes.com/' + media_type + '/' + name       # TODO: place url

def scrapeTV(name):
    '''
    Attempts to scrape a Rotten Tomatoes page for the show (given by name).
    Finds the general information about the show, as provided by Rotten Tomatoes, along with the critic and audience scores.
    Writes the information to a csv file: tv_shows.csv.
    If the above csv file is not found, then it creates it.
    '''

    print(name)

    # Get page for the show
    url = _nameToURL(name, 'tv')

    # Imitate do while loop
    # Attempt to connect 3 times
    has_error = True
    failed_connections = 0

    while(has_error and (failed_connections < 3)):
        try:                                            # Attempt connection to url
            uClient = uReq(url)                         # Open connection to url
            page_html = uClient.read()                  # Get the html from the page
            uClient.close()
            has_error = False
        except (urlError.URLError, urlError.HTTPError, httpError.IncompleteRead): # Catch all errors
            #!! http.client.IncompleteRead !!
            failed_connections += 1

    page_soup = soup(page_html, 'html.parser')      # Give the html to soup

    # FUNCTION 2
    ########################################################################################
    # Get the containers for all relevant information
    title_container =   page_soup.findAll(              'h1',       {'class':   'title'})

    image_container =   page_soup.findAll(              'img',      {'class':   'posterImage'})

    score_containers =  page_soup.findAll(              'div',      {'id':      'series_score_panel'})
    c_score_container = score_containers[0].findAll(    'span',     {'class':   'meter-value superPageFontColor'})
    a_score_container = score_containers[0].findAll(    'span',     {'class':   'superPageFontColor audience-score-align'})


    # The synopsis, creators, and stars are stored in 3 divs in a row
    # The creators and stars divs have no attributes, so we must call them in a row
    info_container =    page_soup.findAll(              'div',      {'id':      'series_info'})
    synopsis_container = info_container[0].findAll(     'div',      {'id':      'movieSynopsis'})
    creators_stars_container = info_container[0].div.div.find_next_siblings('div')          # index 0 is holding the creators, index 1 is holding the stars
    creators_container = creators_stars_container[0].findAll('a')
    stars_container = creators_stars_container[1].findAll('a')

    detail_container =  page_soup.find(                 'section',  {'id':      'detail_panel'})
    details = detail_container.findAll('tr')

    # FUNCTION 3
    ########################################################################################
    # Extract information from all the containers
    # Try to catch all IndexErrors (indicates that information does not exist on the page)
    # If there is an IndexError, leave that field blank

    years = ''
    poster = ''
    critic_score = ''
    audience_score = ''
    synopsis = ''
    creators = []
    stars = []
    network = ''
    premiere_date = ''
    genre = ''
    exec_producers = []

    # Years
    try:
        years = title_container[0].span.text.strip()
    except IndexError:
        pass

    # Poster
    try:
        poster = image_container[0]['src']
    except IndexError:
        pass

    # Critic Score
    try:
        critic_score = c_score_container[0].text.strip()
    except IndexError:
        pass

    # Audience Score
    try:
        audience_score = a_score_container[0].text.strip()
    except IndexError:
        pass

    # Synopsis
    try:
        synopsis = synopsis_container[0].text.strip()
    except IndexError:
        pass

    # Creators

    # Get all the names of the creators
    # !!NOTE!! The link to the person's profile is stored in the href of the a tag
    for creator in creators_container:
        creators += [creator.text.strip()]
    creators = list(dict.fromkeys(creators))    # Remove duplicates

    # Stars

    for star in stars_container:
        stars += [star.text.strip()]
    stars = list(dict.fromkeys(stars))          # Remove duplicates

    # Network
    # Premiere Date
    # Genre
    # Executive Producers

    # Get each detail from the table
    # details hold a list of all the table rows from the table holding all the series details
    # Each detail in details has two td tags. The first is for the label, and the second is for the content
    # If there is a missing detail, then it is left as its default value as assigned above
    for detail in details:

        detail = detail.findAll('td')

        detail_label = detail[0].text.strip()
        detail_content = detail[1].text.strip()

        if   (detail_label == 'TV Network:'):
            network =       detail_content

        elif (detail_label == 'Premiere Date:'):
            premiere_date = detail_content

        elif (detail_label == 'Genre:'):
            genre =         detail_content

        elif (detail_label == 'Executive Producers:'):
            # Get the a tags for all the producers in the detail content
            exec_prod_list = detail[1].findAll('a')

            for producer in exec_prod_list:
                exec_producers += [producer.text.strip().replace("'", '"')]

            exec_producers = list(dict.fromkeys(exec_producers))  # Remove Duplicates

    # FUNCTION 4
    ########################################################################################
    # Write all information to CSV
    filename = 'data/tv_shows.csv'

    try:                            # Test if the file can be read, indicates if it exists
        test_open = open(filename, 'r')
        test_open.close()

    except FileNotFoundError:       # File was not found, create it now
        print(filename + " could not be found. Creating new file now...")

        headers = "title,years,poster_link,critic_score,audience_score,synopsis,creators,stars,network,premiere_date,genre,exec_producers\n"

        f = open(filename, 'w')
        f.write(headers)
        f.close()

    # Append new data in the file
    f = open(filename, 'a')

    # Add a new entry for this tv show
    # Replace all ',' and '\n' with '|' and '~', respectively, to avoid messing up the CSV
    # Quotes are added so lists can contain commas
    f.write(name.replace(',', '|')                                              + ',' +
            years.replace(',', '|')                                             + ',' +
            poster.replace(',', '|')                                            + ',' +
            critic_score.replace(',', '|').replace('%', '')                     + ',' +
            audience_score.replace(',', '|').replace('%', '')                   + ',' +
            synopsis.replace(',', '|').replace('\r\n', '~').replace('"', "'")   + ',"' +
            str(creators).replace('"', "'")                                     + '","' +
            str(stars).replace('"', "'")                                        + '",' +
            network.replace(',', '|')                                           + ',' +
            premiere_date.replace(',', '|')                                     + ',' +
            genre.replace(',', '|')                                             + ',"' +
            str(exec_producers).replace('"', "'")                               + '"\n')

    f.close()

    '''
    ########################################################################################
    # Print all information
    print(name)
    print(years)
    print(poster)
    print(critic_score)
    print(audience_score)
    print(synopsis)
    print(creators)
    print(stars)
    print(network)
    print(premiere_date)
    print(genre)
    print(exec_producers)
    '''

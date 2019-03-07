from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup

def hello():
    print('hello')

def _nameToURL(name, media_type):
    '''
    Helper method to get the RottenTomatoes URL for the show/film
    '''
    
    if((media_type != 'tv') and (media_type != 'm')):
        raise ValueError('Invalid media type')
    else:
        return 'https://www.rottentomatoes.com/' + media_type + '/' + name       # TODO: place url

def scrapeTV(name):
    '''
    Attempts to scrape a RottenTomatoes page for the name of the given show.
    Writes the information to a csv file: tv_shows.csv.
    If the above csv file is not found, then it creates it.
    '''
    
    # Get page for the show
    url = _nameToURL(name, 'tv')

    try:                                            # Attempt connection to url
        uClient = uReq(url)                         # Open connection to url
        page_html = uClient.read()                  # Get the html from the page
        uClient.close()
    except:                                         # Catch all errors
        # TODO: Write errors to file with name of show
        pass
        
    page_soup = soup(page_html, 'html.parser')      # Give the html to soup

    # -----------------------------
    # Get the containers for all relevant information
    title_container =   page_soup.findAll(              'h1',   {'class':   'title'})

    image_container =   page_soup.findAll(              'img',  {'class':   'posterImage'})

    score_containers =  page_soup.findAll(              'div',  {'id':      'series_score_panel'})
    c_score_container = score_containers[0].findAll(    'span', {'class':   'meter-value superPageFontColor'})
    a_score_container = score_containers[0].findAll(    'span', {'class':   'superPageFontColor audience-score-align'})

    
    # The synopsis, creators, and stars are stored in 3 divs in a row
    # The creators and stars divs have no attributes, so we must call them in a row
    info_container =    page_soup.findAll(              'div',  {'id':      'series_info'})
    synopsis_container = info_container[0].findAll(     'div',  {'id':      'movieSynopsis'})
    creators_stars_container = info_container[0].div.div.find_next_siblings('div')          # index 0 is holding the creators, index 1 is holding the stars
    creators_container = creators_stars_container[0].findAll('a')
    stars_container = creators_stars_container[1].findAll('a')

    detail_container =  page_soup.findAll(              'div',  {'class':      'panel-body content_body'})

    # -----------------------------
    # Extract information from all the containers
    years = title_container[0].span.text.strip()
    poster = image_container[0]['src']
    critic_score = c_score_container[0].text
    audience_score = a_score_container[0].text
    synopsis = synopsis_container[0].text
    creators = []
    stars = []

    # Get all the names of the creators
    # !!NOTE!! The link to the creators profile is stored in the href of the a elements that are holding the creators
    for creator in creators_container:
        creators += [creator.text]

    for star in stars_container:
        stars += [star.text]

    # -----------------------------
    # Write all information to CSV
    filename = 'data/tv_shows.csv'

    try:                            # Test if the file can be read, indicates if it exists
        test_open = open(filename, 'r')
        test_open.close()

    except FileNotFoundError:       # File was not found, create it now
        print(filename + " could not be found. Creating new file now...")

        headers = "title, years, poster_link, critic_score, audience_score, synopsis, creators, stars\n"

        f = open(filename, 'w')
        f.write(headers)
        f.close()

    # Append new data in the file
    # TODO: Avoid redundancy
    f = open(filename, 'a')

    # Add a new entry for this tv show
    f.write(name + ',' + years + ',' + poster + ',' + critic_score + ',' + audience_score + ',' + synopsis.replace(',', '|') + ',' + str(creators).replace(',', '|') + ',' + str(stars).replace(',', '|') + '\n')

    f.close()
    
    # -----------------------------
    # Print all information
    print(name)
    print(years)
    print(poster)
    print(critic_score)
    print(audience_score)
    print(synopsis)
    print(creators)
    print(stars)

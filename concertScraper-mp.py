"""
proj:   Mississippi Pizza concertScraper v1.0
org:    ampmusic.co

author: Jack Sanders
date:   01/05/2020

usage:  scrapy <command> [options] [args]
        scrapy shell kanyewest.com
        scrapy crawl <spider_name> -o kanye.csv

info:   Scraper for Mississippi Pizza (Portland, OR) using Scrapy spider
"""

import scrapy  # Scrapy 1.7.2
import re


class concertSpider_ad(scrapy.Spider):
    name = "mp"  # spider name
    # allowed domain(s) :
    # allowed_domains = ["www.mississippipizza.com"]
    start_urls = ['http://www.mississippipizza.com/events/']  # contains all concert links

    def parse(self, response: 'response object') -> None:
        """
        scrapes URLs and passes them to get_details via 'response' object
        """
        for url in response.css('div.tribe-events-category- a::attr(href)').getall():  # loops through all extracted URLs
            # Construct absolute URL by combining the response’s URL with a possible relative URL
            full_url = url          # don't need to do this because absolute URLs
            yield scrapy.Request(full_url, callback=self.get_details)  # call get_details() on full_url

    def get_details(self, response: 'response object') -> dict:
        """
        called by parse
        scrapes URLs in response.css format

        usage -> yield scrapy.Request(full_url, callback=self.get_details)

        unique_id: varchar
        concert_id: int
        source_id: int
        scraper_id: int
        venue_id: int
        artist: varchar
        artist_short: varchar
        venue: varchar
        venue_short: varchar
        day_of_week: varchar
        date: DATE
        street_address: varchar
        city: varchar
        state_code: varchar
        zip_code: int
        start_time: TIME
        end_time: TIME
        door_time: TIME
        event_free: int
        event_details: varchar
        first_description: TEXT
        second_description: TEXT
        genre: varchar
        quality_score: int
        """

        # initalize IDs
        unique_id = 0
        concert_id = 9
        source_id = 2   # source_id=2 -> scraper
        scraper_id = 9  # JOIN scraper_view ON concerts.scraper_id = scraper_view.id
        venue_id = 9    # JOIN venue_view ON concerts.venue_id = venue_view.id

        # get artists
        artist = str(response.xpath('//title/text()').get())  # scrape artist name
        artist = artist.lstrip()    # remove leading spaces
        artist = artist.rstrip()    # remove trailing spaces

        # parse alternate short artist names  i.e  Kanye West -> Kanye W...
        artist_len_cap = 30         # set max string length for artist names
        if len(artist) < (artist_len_cap - 2):
            artist_short = artist   # if string length under cap
        else:
            artist_short = str(artist[:(artist_len_cap-3)] + '...')

        # get venues
        venue = "Mississippi Pizza"          # hard-coded venue name (make dynamic)

        # parse alternate short venue name  i.e.  Crystal Ballroom -> Crystal Ba...
        venue_len_cap = 30          # set max string length for venue names
        if len(venue) < (venue_len_cap - 2):
            venue_short = venue     # if string length under cap
        else:
            venue_short = str(venue[:(venue_len_cap-3)] + '...')

        # initialize scraped date_raw string which includes date, day_of_week
        date_raw = response.css('abbr.tribe-events-abbr::text').get()

        # extract day_of_week from date_raw
        #day_of_week = date_raw.split(',')[0]
        #day_of_week = day_of_week.lstrip()      # remove leading spaces
        #day_of_week = day_of_week.rstrip()      # remove trailing spaces

        # create DATETIME YYYY-MM-DD from date_raw

        # step_1: extract year (YYYY) from date_raw
        if len(date_raw.split(',')) == 1:
            year = "2020"
        else:
            year = date_raw.split(',')[-1]
        year = year.lstrip()  # remove leading spaces
        year = year.rstrip()  # remove trailing spaces

        # step_2: extract month (MM) from date_raw
        month_dict = {
            'January': '01',
            'February': '02',
            'March': '03',
            'April': '04',
            'May': '05',
            'June': '06',
            'July': '07',
            'August': '08',
            'September': '09',
            'October': '10',
            'November': '11',
            'December': '12'
        }
        month = str(month_dict[date_raw.split()[0]])  # use extracted data as dict key -> int
        month = month.lstrip()      # remove leading spaces
        month = month.rstrip()      # remove trailing spaces

        # step_3: extract day (DD) from date_raw
        if len(date_raw.split(',')) == 1:
            day = str(date_raw.split()[-1])
        else:
            day = str(date_raw.split(',')[0].split()[1])
        day = day.lstrip()          # remove leading spaces
        day = day.rstrip()          # remove trailing spaces

        # step_4: assemble year,month,day (YYYY-MM-DD)
        parsed_date = str(year) + '-' + str(month) + '-' + str(day)
        parsed_date = parsed_date.lstrip()      # remove leading spaces
        parsed_date = parsed_date.rstrip()      # remove trailing spaces


        # hard-code street_address (make dynamic)
        street_address_static = '3552 N.Mississippi Ave.'

        # hard-code city name (make dynamic
        city = 'Portland'

        # hard-code state_code (make dynamic)
        state_code = 'OR'

        # hard-code state_code (make dynamic)
        zip_code = 97227

        # extract and parse start_time & end_time: "7 - 10 pm" -> start_time: "7 pm" & end_time: "10 pm"
        # format converted to DATETIME in excel
        event_info = response.css('div.tribe-events-abbr::text').get()    # scrape event_info(times / ticket prices)
        time = ""
        for ch in event_info.split('\t'):
            if len(ch) > 4:
                time = ch
        print(event_info)
        print(time)
        start_time = time.split('-')[0]
        start_time = start_time.lstrip()      # remove leading spaces
        start_time = start_time.rstrip()      # remove trailing spaces
        end_time = time.split('-')[1]
        end_time = end_time.lstrip()      # remove leading spaces
        end_time = end_time.rstrip()      # remove trailing spaces


        """
        time = event_info[0]
        time_split = time.split()                                   # "7 - 10 pm" -> ["7", "-", "10", "pm"]
        if 'doors' in time:
            door_time = time_split[0] + ' ' + time_split[1]
            start_time = time_split[-3] + ' ' + time_split[-2]
            end_time = ""
        elif '-' in time:                                           # checks if time displayed as range 'start - stop'
            start_time = time_split[0] + ' ' + time_split[-1]       # append pm to start_time val
            end_time = time_split[-2] + ' ' + time_split[-1]        # append pm to end_time val
            door_time = ""                                          # no door_time
        else:
            start_time = start_time = event_info[0]                 # if only start, display as is
            end_time = ""                                           # no end_time
            door_time = ""                                          # no door_time
        """

        """
        # check if event is free  |  event_info = response.css('p.event-info::text').getall()
        event_free = 0
        if event_info[1] == 'Free' or event_info[1] == 'Free Admission':
            event_free = 1

        # extract and parse the event_details
        event_details = event_info[-1]

        # extract and parse the event_description
        html_1 = response.css('div.tm-card-content')    # broad div tag
        html_2 = html_1.css('p::text').getall()         # returns text list of <p> tags in div.tm-card-content
        event_description = ""                          # initialize event_description
        for i in range(len(html_2)):                    # iterate through text list
            if (len(html_2[i]) > 30) and ('\t' not in html_2[i]) and ('     ' not in html_2[i]):
                event_description += str(html_2[i]) + " "      # append to event_info based on specified criteria

        # parse first sentence of the description
        alphabets = "([A-Za-z])"
        prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
        suffixes = "(Inc|Ltd|Jr|Sr|Co)"
        starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
        acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
        websites = "[.](com|net|org|io|gov)"
        text = event_description
        text = " " + text + "  "
        text = text.replace("\n", " ")
        text = re.sub(prefixes, "\\1<prd>", text)
        text = re.sub(websites, "<prd>\\1", text)
        if "Ph.D" in text: text = text.replace("Ph.D.", "Ph<prd>D<prd>")
        text = re.sub("\s" + alphabets + "[.] ", " \\1<prd> ", text)
        text = re.sub(acronyms + " " + starters, "\\1<stop> \\2", text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]", "\\1<prd>\\2<prd>", text)
        text = re.sub(" " + suffixes + "[.] " + starters, " \\1<stop> \\2", text)
        text = re.sub(" " + suffixes + "[.]", " \\1<prd>", text)
        text = re.sub(" " + alphabets + "[.]", " \\1<prd>", text)
        if "”" in text: text = text.replace(".”", "”.")
        if "\"" in text: text = text.replace(".\"", "\".")
        if "!" in text: text = text.replace("!\"", "\"!")
        if "?" in text: text = text.replace("?\"", "\"?")
        text = text.replace(".", ".<stop>")
        text = text.replace("?", "?<stop>")
        text = text.replace("!", "!<stop>")
        text = text.replace("<prd>", ".")
        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        sentences = [s.strip() for s in sentences]
        first_sentence = sentences[0]

        # other sentences
        sentence_length = len(first_sentence)
        second_description = event_description[(sentence_length + 1):]

        # parse event_details_short
        event_description_short = ""                    # initialize event_description_short
        if event_description != "":                     # if no description, short description = ""
            for i in range(len(html_2)):                # iterate through text list
                if (len(html_2[i]) > 30) and ('\t' not in html_2[i]) and ('     ' not in html_2[i]):
                    event_description_short = str(html_2[i]) + " "  # take first paragraph

        # extract & parse genre
        genre = "default"           # if no genres to be found
        genre_list = ['African',
                      'Arabic',
                      'Asian',
                      'East',
                      'Asian',
                      'Avant-garde',
                      'Blues',
                      'Caribbean',
                      'Country',
                      'Electronic',
                      'Folk',
                      'Hip-hop',
                      'Jazz',
                      'Latin',
                      'Pop',
                      'R&B',
                      'Soul',
                      'Rock',
                      'Classical']                          # append additional genres here
        if event_description != "":                         # if there exists an event_description to search
            genre = ""                                      # not default
            for i in range(len(genre_list)):                # check event_description for each genre
                #if genre_list[i] in event_description:
                if re.search(genre_list[i], event_description, re.IGNORECASE):
                    genre += (str(genre_list[i]) + ", ")    # append to string separated by commas
            if len(genre) > 0:                              # if successfully determine at least one genre
                genre = genre[:-2]                          # remove trailing comma
            else:                                           # if no genre detected
                genre = "default"                           # back to default
        """
        # dictionary with all parsed data
        full_dict = {
                'unique_id':                unique_id,
                'concert_id':               concert_id,
                'source_id':                source_id,
                'scraper_id':               scraper_id,
                'venue_id':                 venue_id,
                'artist':                   artist,
                'artist_short':             artist_short,
                'venue':                    venue,
                'venue_short':              venue_short,
                #'day_of_week':              day_of_week,
                'date':                     parsed_date,            #response.css('abbr.tribe-events-abbr::text').get(),
                'street_address':           street_address_static,  #response.css('span.tribe-street-address::text').get(),
                'city':                     city,                   #response.css('span.tribe-locality::text').get(),
                'state_code':               state_code,             #response.css('abbr.tribe-region::text').get(),
                'zip_code':                 zip_code,               #response.css('span.tribe-postal-code::text').get(),
                'start_time':               start_time,             #response.css('div.tribe-events-abbr::text').get(),
                #'country':                 response.css('span.tribe-country-name::text').get()
                'end_time':                 end_time,
                #'door_time':                "",
                #'event_free':               event_free,
                #'event_details':            event_details,
                'total_description':        response.css('p.text-align-center::text').getall(), #event_description,
                'first_description':        response.css('div.tribe-events-single-event-description p::text').getall(), #first_sentence,
                #'second_description':       second_description,
                #'event_description_short':  event_description_short,
                #'genre':                    genre,
                'quality_score':            0
        }
        """
        # filter concerts
        quality_check = 1
        if full_dict["event_free"] != 1:    # quality_check = 0 if event is not free
            quality_check = 0
        # additional filters here
        if quality_check == 1:              # yield concert only if it passes all filters
            yield full_dict                 # export only this yield
        """
        # response.css('abbr.tribe-events-abbr::text').get()
        # response.css('div.tribe-events-abbr::text').get()
        #
        #
        yield full_dict
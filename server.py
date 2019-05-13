from scraper import *
import datetime
import time
import random


def load_websites():
    while True:
        # schedule job, something like:
        general_time_to_scrape = str(datetime.time(12, 28, 0))
        now = str(datetime.datetime.now().time())[:-7]
        # then, when the job runs:
        scrapers = [RavHenScraper]
        if general_time_to_scrape == now:
            for scraper in scrapers:
                scraper_websites = [attr for attr in dir(scraper) if attr[0].isupper()]
                for website in scraper_websites:
                    # a small random delay to start
                    time.sleep(random.randint(1, 5))
                    # scrape to load json
                    scraper.load_website_data_to_json(getattr(scraper, website))
                    # a random delay before going on the next
                    time.sleep(random.randint(8, 30))
            return "Done"



print(load_websites())



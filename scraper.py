from selenium import webdriver
import datetime
import time
import json
from bs4 import BeautifulSoup


class RavHenHerzlyiaScraper:

    WEBSITE_NAME = "Rav_Hen_Herzlyia"

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.load_website_data_to_json()

    @staticmethod
    def get_current_movies_screens_url():

        url = "https://www.rav-hen.co.il/#/buy-tickets-by-cinema?in-cinema=1061&at=%s&view-mode=list" % datetime.date.today()
        return url

    def load_website_data_to_json(self):

        self.driver.get(RavHenHerzlyiaScraper.get_current_movies_screens_url())
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        movies_dict = {}
        movies_blocks = soup.find_all("div", attrs={"class": ["row movie-row", "row movie-row first-movie-row"]})
        for movie_block in movies_blocks:
            movie_name = str(movie_block).split('name">')[1].split('</')[0]
            movies_dict[movie_name] = {}
            screens_data = str(movie_block).replace("amp;", "").split('data-url="')[1:]
            for screen in screens_data:
                data = screen.split('" href="#">')
                screen_url = data[0]
                screen_time = data[1][:5]
                movies_dict[movie_name][screen_time] = screen_url

        with open("bank.json", "r") as json_file:
            data = json.load(json_file)
            data[RavHenHerzlyiaScraper.WEBSITE_NAME] = movies_dict
        with open("bank.json", "w") as outfile:
            json.dump(data, outfile)

    @classmethod
    def go_to_screen(cls, movie_name, screen_time, tickets):

        active_driver = webdriver.Chrome()
        with open("bank.json", "r") as json_file:
            data = json.load(json_file)

        try:
            active_driver.get(data[RavHenHerzlyiaScraper.WEBSITE_NAME][movie_name][screen_time])
        except KeyError:
            raise SystemError("I don't know this screen: '%s' at '%s'" % (movie_name, screen_time))

        active_driver.find_element_by_xpath('//select[@class="ddlTicketQuantity"]/option[@value="%s"]' % str(tickets)).click()
        active_driver.find_element_by_xpath('//a[@id="lbSelectSeats"]').click()
        active_driver.find_element_by_xpath('//a[@class="u1st_accBtn u1st_accBtnText"]').click()
        time.sleep(15)
        active_driver.find_element_by_xpath('//span[@class="slider round"]').click()
        active_driver.find_element_by_xpath('//app-button[@id="applyBtn"]/button').click()


now = RavHenHerzlyiaScraper()
RavHenHerzlyiaScraper.go_to_screen("הנוקמים: סוף המשחק", "21:30", 3)







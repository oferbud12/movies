from selenium import webdriver
import datetime
import time
import json
from bs4 import BeautifulSoup


class RavHenHerzlyiaScraper:

    # Class attributes hold data regarding each site's code for building proper url, and name to be entered to bank.json.
    HERZLYIA = ("1061", "Rav_Hen_Herzlyia")
    GIVATAYIM = ("1058", "Rav_Hen_Givatayim")
    DIZINGOF = ("1071", "Rav_Hen_Dizingof")
    MODIIN = ("1069", "Rav_Hen_Modiin")
    KIRYAT_ONO = ("1062", "Rav_Hen_Kiryat_Ono")

    @classmethod
    def get_current_movies_screens_url(cls, city_code):

        url = "https://www.rav-hen.co.il/#/buy-tickets-by-cinema?in-cinema=%s&at=%s&view-mode=list" % (city_code, datetime.date.today())
        return url

    @classmethod
    def load_website_data_to_json(cls, website):

        driver = webdriver.Chrome()
        driver.get(RavHenHerzlyiaScraper.get_current_movies_screens_url(website[0]))
        soup = BeautifulSoup(driver.page_source, "html.parser")
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
        driver.close()

        with open("bank.json", "r") as json_file:
            data = json.load(json_file)
            data[website[1]] = movies_dict
        with open("bank.json", "w") as outfile:
            json.dump(data, outfile)

    @classmethod
    def go_to_screen(cls, website, movie_name, screen_time, tickets):

        active_driver = webdriver.Chrome()
        with open("bank.json", "r") as json_file:
            data = json.load(json_file)
        try:
            active_driver.get(data[website[1]][movie_name][screen_time])
        except KeyError:
            raise SystemError("I don't know this screen: '%s' at '%s'" % (movie_name, screen_time))

        active_driver.find_element_by_xpath('//select[@class="ddlTicketQuantity"]/option[@value="%s"]' % str(tickets)).click()
        active_driver.find_element_by_xpath('//a[@id="lbSelectSeats"]').click()

        # Fetching seats data

        soup = BeautifulSoup(active_driver.page_source, "html.parser")
        seats_raw_data = soup.find("div", attrs={"id": "accesibleSeatPlanContainer"})
        seats_data = str(seats_raw_data).split('id="s_')[1:]
        seats = []
        valid_char = [str(i) for i in range(50)] + ["_"]
        for seat in seats_data:
            seat_line = "".join(char for char in list(seat[:5]) if char in valid_char).split("_")
            try:
                state = seat.split('data-state="')[1][:1]
                seats.append((seat_line, state))
            except IndexError:
                state = "not available"
                seats.append((seat_line, state))

        last_line = int(seats[-1][0][1])
        parsed_seats = {}
        for i in range(1, last_line + 1):
            parsed_seats[i] = []
        for seat in seats:
            parsed_seats[int(seat[0][1])].append({int(seat[0][0]): seat[1]})

        # What about last seat??

        return parsed_seats





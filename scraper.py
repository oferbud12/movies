from selenium import webdriver
import datetime
import json
from bs4 import BeautifulSoup


class RavHenScraper:

    # Class attributes hold data regarding each site's code for building proper url, and name to be entered to bank.json
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
        driver.get(RavHenScraper.get_current_movies_screens_url(website[0]))
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
    # Gets you all the way to page of choosing seats for a certain movie screen
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

        return active_driver.page_source

    @classmethod
    # Parse seats data from the 'choosing seats' page
    def parse_soup_seats(cls, page_source):

        soup = BeautifulSoup(page_source, "html.parser")
        seats_raw_data = soup.find("div", attrs={"id": "accesibleSeatPlanContainer"})
        seats_splitted_raw_list = str(seats_raw_data).split('td_')[1:]
        seats_splitted_parsed_list = []

        valid_char = [str(i) for i in range(50)] + ["_"]
        offset = 0
        line_info = lambda seat_str: int("".join([char for char in list(seat_str[:5]) if char in valid_char]).split("_")[0])

        for seat in seats_splitted_raw_list:

            # Re-initializing offset when needed:
            line = line_info(seat)
            if seats_splitted_raw_list.index(seat) == 0:
                # First run, no former seats to compare, there should be no offset
                offset = 0
            elif line != line_info(seats_splitted_raw_list[seats_splitted_raw_list.index(seat) - 1]):
                # This seat element is from a new line in the iteration, offset should be re-initialized
                offset = 0

            # Parsing the seat data and adding to 'seats_splitted_parsed_list'
            try:
                actual_data = seat.split('id="s_')[1]
                website_seat_line = "".join([char for char in list(actual_data[:5]) if char in valid_char]).split("_")
                real_seat_line = [int(element) for element in website_seat_line]
                real_seat_line = [real_seat_line[0] - offset, real_seat_line[1]]
                seat_state = "".join(seat.split('data-state="')[1][:1])
                seats_splitted_parsed_list.append((real_seat_line, seat_state, offset))
            except IndexError:
                # this is not a real seat in the line
                offset += 1
                continue

        # Create the parsed_seats_dict
        last_line = seats_splitted_parsed_list[-1][0][1]
        parsed_seats_dict = {}
        for i in range(1, last_line + 1):
            parsed_seats_dict[i] = []
        for seat in seats_splitted_parsed_list:
            parsed_seats_dict[seat[0][1]].append({seat[0][0]: seat[1], "offset": seat[2]})

        return parsed_seats_dict


# Testing

seats = RavHenScraper.parse_soup_seats(RavHenScraper.go_to_screen(RavHenScraper.HERZLYIA, "הנוקמים: סוף המשחק", "20:30", 3))
print(seats)





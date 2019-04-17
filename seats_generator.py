from selenium import webdriver
import time
from bs4 import BeautifulSoup
import math


# After we fetch successfully the source page of a:
# specific movie theater, which plays the wanted movie, and the number of tickets was already ordered.


class Theater:

    def __init__(self, page_source, tickets):
        self.soup = BeautifulSoup(page_source, "html.parser")
        self.tickets = tickets
        self.all_seats = self.fetch_seats_data("class", "aseat")
        self.free_seats = self.get_free_seats()
        self.measures = self.get_max_line_seat()
        self.best_seats = self.get_best_seats()

    def fetch_seats_data(self, attribute, value):
        # Returns a list of all seats that share a specific value for a certain attribute
        # Every element looks like: "seat_line"
        data = self.soup.findAll(attrs={attribute: value})
        data = str(data).split('id="s_')[1:]
        valid_char = [str(i) for i in range(50)] + ["_"]
        data_list = ["".join([char for char in seat[:5] if char in valid_char]) for seat in data]
        return data_list

    def get_free_seats(self):
        # Returns a dictionary of all free seats, formation is: {line_number : [seat1, seat2, seat3..]} - Integers only
        empty_seats_list = self.fetch_seats_data("data-state", "0")
        last_empty_seats_line = int(empty_seats_list[-1].split("_")[1])
        free_seats = {}
        for i in range(1, last_empty_seats_line + 1):
            free_seats[i] = []
        for seat in empty_seats_list:
            seat_line = seat.split("_")
            free_seats[int(seat_line[1])].append(int(seat_line[0]))
        return free_seats

    def get_max_line_seat(self):
        # Returns a tuple of (max line, max seat) - to know the theater measures
        max_line = 1
        max_seat = 1
        for seat in self.all_seats:
            seat_line = seat.split("_")
            if int(seat_line[0]) > max_seat:
                max_seat = int(seat_line[0])
            if int(seat_line[1]) > max_line:
                max_line = int(seat_line[1])
        return max_line, max_seat

    def generate_optional_best_seats(self, best_seat):
        # Returns a list of the possible best seats in a row, according to the number of tickets,
        # if all seats were empty
        places_to_add = self.tickets - 1
        on_the_left = int(math.ceil(places_to_add / 2.0))
        on_the_right = places_to_add - on_the_left
        start_seat = best_seat - on_the_left
        end_seat = best_seat + on_the_right
        return list(range(start_seat, end_seat + 1))

    @staticmethod
    def best_seats_available_in_free_seats(best_seats_list, free_seats_list):
        # Checks if the possible best_seats_list is in a free_seats_list
        if len(free_seats_list) < len(best_seats_list):
            raise ValueError("The second given list should be the bigger one")
        else:
            for i in range((len(free_seats_list) - len(best_seats_list) + 1)):
                if best_seats_list == free_seats_list[i:len(best_seats_list) + i]:
                    return True
            return False

    def get_best_seats(self):
        # Returns the best seats in the theater: (best line, best_seats)
        max_line = self.measures[0]
        max_seat = self.measures[1]
        best_line = int(math.ceil(float(2 / 3) * max_line))
        best_seat = int(math.ceil(max_seat / 2))
        best_tickets_seats = self.generate_optional_best_seats(best_seat)
        # Currently assuming that all seats are empty, starting to work on the real shit from here soon
        if self.best_seats_available_in_free_seats(best_tickets_seats, self.free_seats[best_line]):
            return best_line, best_tickets_seats


# Testing:

driver = webdriver.Chrome()
driver.get("https://www.rav-hen.co.il/#/buy-tickets-by-cinema?in-cinema=1061&at=2019-04-14&view-mode=list")
driver.find_element_by_xpath('//a[@class="btn btn-sm btn-primary"]').click()
driver.find_element_by_xpath('//select[@class="ddlTicketQuantity"]/option[@value="2"]').click()
driver.find_element_by_xpath('//a[@id="lbSelectSeats"]').click()
driver.find_element_by_xpath('//a[@id="u1stLogoContainer"]').click()
time.sleep(3)
driver.find_element_by_xpath('//a[@class="u1st_profile_advancedScreenReader u1st_caption"]').click()
source = driver.page_source

love_in_shlakes_rav_chen_theater_2_15_40 = Theater(source, 5)
print(love_in_shlakes_rav_chen_theater_2_15_40.all_seats)
print(love_in_shlakes_rav_chen_theater_2_15_40.free_seats)
print(love_in_shlakes_rav_chen_theater_2_15_40.measures)
print(love_in_shlakes_rav_chen_theater_2_15_40.best_seats)






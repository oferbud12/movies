from selenium import webdriver
import time
from bs4 import BeautifulSoup


driver = webdriver.Chrome()
driver.get("https://www.rav-hen.co.il/#/buy-tickets-by-cinema?in-cinema=1061&at=2019-04-14&view-mode=list")
driver.find_element_by_xpath('//a[@data-url="https://www.rav-hen.co.il/booking?presentationCode=6311041419-99782&cinemaId=1061&lang=he-IL"]').click()
driver.find_element_by_xpath('//select[@class="ddlTicketQuantity"]/option[@value="2"]').click()
driver.find_element_by_xpath('//a[@id="lbSelectSeats"]').click()
driver.find_element_by_xpath('//a[@id="u1stLogoContainer"]').click()
time.sleep(3)
driver.find_element_by_xpath('//a[@class="u1st_profile_advancedScreenReader u1st_caption"]').click()

source = driver.page_source
soup1 = BeautifulSoup(source, "html.parser")

def get_free_seats(soup):
    empty_seats = soup.findAll(attrs={"data-state": "0"})
    empty_seats = str(empty_seats).split('id="s_')[1:]
    valid_char = [str(i) for i in range(24)] + ["_"]
    return ["".join([char for char in seat[:5] if char in valid_char]) for seat in empty_seats]
        #seat_place_line = "".join([char for char in seat[:5] if char in valid_char])
        #print(seat_place_line)

a = get_free_seats(soup1)
print(a)
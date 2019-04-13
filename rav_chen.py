#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import time


chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome()
url = r'https://www.rav-hen.co.il/whatson'
driver.get(url)



driver.find_element_by_xpath('//a[@class="cinema-card"]').click()
time.sleep(2)
driver.find_element_by_xpath('//a[@class="btn btn-sm btn-primary"]').click()
time.sleep(2)
driver.find_element_by_xpath('//select[@class="ddlTicketQuantity"]/option[@value="1"]').click()
driver.find_element_by_xpath('//a[@class="actionBtn"]').click()

driver.execute_script(
	"""window.localStorage.setItem("User1st.u1st-SRSnoozingDisabled",
		'%7B%22expiration%22%3A1641502042033%2C%22value%22%3A%221%22%7D')""")
driver.execute_script(
	"""window.localStorage.setItem("User1st.u1stIsActive",
		'%7B%22expiration%22%3A1641502254319%2C%22value%22%3A%221%22%7D')""")
driver.execute_script(
	"""window.localStorage.setItem("User1st.u1stSettings",
		'%7B%22expiration%22%3A1641502254356%2C%22value%22%3A%22%257B%2522profileID%2522%253A%2522advancedScreenReader%2522%257D%22%7D')""")
driver.execute_script(
	"""window.sessionStorage.setItem("User1st.u1st-SRSnoozingDisabled",
		'%7B%22expiration%22%3A1641502042033%2C%22value%22%3A%221%22%7D')""")
driver.execute_script(
	"""window.sessionStorage.setItem("User1st.u1stIsActive",
		'%7B%22expiration%22%3A1641502254319%2C%22value%22%3A%221%22%7D')""")
driver.execute_script(
	"""window.sessionStorage.setItem("User1st.u1stSettings",
		'%7B%22expiration%22%3A1641502254356%2C%22value%22%3A%22%257B%2522profileID%2522%253A%2522advancedScreenReader%2522%257D%22%7D')""")
driver.execute_script("location.reload()")

print('reloaded')


source = driver.page_source
source = driver.page_source
soup = BeautifulSoup(source, 'lxml')
soup = soup.prettify()
print(soup.encode("utf-8"))

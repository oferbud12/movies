from selenium import webdriver
import datetime
import json
import time
from bs4 import BeautifulSoup


def parse_element(element, element_type):
    if element_type == "movie_name":
        movie_name = str(element).split('name">')[1].split('</')[0]
        return movie_name
    elif element_type == "movie_data":
        element = str(element).replace("amp;", "").split('data-url="')[1].split('" href="#">')
        url = element[0]
        screen_time = element[1][:-4]
        return url, screen_time


driver = webdriver.Chrome()
url = "https://www.rav-hen.co.il/#/buy-tickets-by-cinema?in-cinema=1061&at=%s&view-mode=list" % datetime.date.today()
driver.get(url)

soup = BeautifulSoup(driver.page_source, "html.parser")
movies_names = [parse_element(movie, "movie_name") for movie in soup.find_all(attrs={"class": "qb-movie-name"})]
movies_data = [parse_element(movie, "movie_data") for movie in soup.find_all(attrs={"class": "btn btn-sm btn-primary"})]

print(movies_names)
print(movies_data)

movies_dict = dict()

for movie_name in movies_names:
    movies_dict[movie_name] = dict()
    for movie_data in movies_data:
        try:
            screen_times = [list(screen.values())[1] for screen in movies_dict[movie_name].values()]
            if movie_data[1] in screen_times:
                break
            else:
                movies_dict[movie_name][movies_data.index(movie_data) + 1] = {"url": movie_data[0], "screen_time": movie_data[1]}
        except KeyError:
            movies_dict[movie_name][movies_data.index(movie_data) + 1] = {"url": movie_data[0], "screen_time": movie_data[1]}

print(movies_dict)

with open("bank.json", "w") as outfile:
    json.dump(movies_dict, outfile)









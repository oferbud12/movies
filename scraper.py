from selenium import webdriver
import datetime
import json
from bs4 import BeautifulSoup


class RavHenHerzlyiaScraper:

    def __init__(self):
        self.driver = webdriver.Chrome()
        self.load_website_data_to_json("Rav_Hen_Herzlyia")
        self.driver.close()

    @staticmethod
    def get_current_movies_screens_url():
        url = "https://www.rav-hen.co.il/#/buy-tickets-by-cinema?in-cinema=1061&at=%s&view-mode=list" % datetime.date.today()
        return url

    @staticmethod
    def parse_element(element, element_type):
        if element_type == "movie_name":
            movie_name = str(element).split('name">')[1].split('</')[0]
            return movie_name
        elif element_type == "movie_screen":
            element = str(element).replace("amp;", "").split('data-url="')[1].split('" href="#">')
            url = element[0]
            presentation_code = url.split("presentationCode=")[1].split("-")[0]
            screen_time = element[1][:-4]
            return presentation_code, screen_time, url

    def load_website_data_to_json(self, website_name):
        self.driver.get(RavHenHerzlyiaScraper.get_current_movies_screens_url())
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        movies_names = [RavHenHerzlyiaScraper.parse_element(movie, "movie_name") for movie in soup.find_all(attrs={"class": "qb-movie-name"})]
        movies_data = [RavHenHerzlyiaScraper.parse_element(movie, "movie_screen") for movie in soup.find_all(attrs={"class": "btn btn-sm btn-primary"})]
        movies_dict = {}
        for movie_name in movies_names:
            movies_dict[movie_name] = {"code": movies_data[0][0]}
            for movie_data in movies_data:
                if movie_data[0] == movies_dict[movie_name]["code"]:
                    movies_dict[movie_name][movie_data[1]] = movie_data[2]
                else:
                    break
            movies_data = [movie_data for movie_data in movies_data if movie_data[2] not in movies_dict[movie_name].values()]

        with open("bank.json", "r") as json_file:
            data = json.load(json_file)
            data[website_name] = movies_dict
        with open("bank.json", "w") as outfile:
            json.dump(data, outfile)


now = RavHenHerzlyiaScraper()




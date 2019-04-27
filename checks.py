import json

with open("bank.json", "r") as outfile:
    data = json.load(outfile)

for movie, data in data["rav_hen_herzlyia"].items():
    print(movie)
    print(data)
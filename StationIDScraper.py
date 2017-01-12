from bs4 import BeautifulSoup
import urllib.request

station_url = 'https://tidesandcurrents.noaa.gov/stations.html?type=Historic+Water+Levels'
with urllib.request.urlopen(station_url) as url:
    station_html = url.read()
    
soup = BeautifulSoup(station_html, "html.parser")

stations = soup.find_all('div', {'class': lambda L: L and L.startswith('span4 station')})

station_info = {}
for station in stations:
    station_info[station.a.get_text().split()[0]] = {}
    station_info[station.a.get_text().split()[0]]['dates'] = station.span.get_text()

import json

with open("station_info.json", "w") as writeJSON:
    json.dump(station_info, writeJSON)


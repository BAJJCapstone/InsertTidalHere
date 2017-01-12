from bs4 import BeautifulSoup
import urllib.request
import json

station_url = 'https://tidesandcurrents.noaa.gov/stations.html?type=Historic+Water+Levels'
with urllib.request.urlopen(station_url) as url:
    station_html = url.read()
    
soup = BeautifulSoup(station_html, "html.parser")

stations = soup.find_all('div', {'class': lambda L: L and L.startswith('span4 station')})

station_info = {}

station_info['ID'] = {}
station_info['dates'] = {}

for station in stations:
    key = ''.join(station.a.get_text().split()[1:])
    station_info['dates'][key] = station.span.get_text()
    station_info['ID'][key] = station.a.get_text().split()[0]

with open("station_info.json", "w") as writeJSON:
    json.dump(station_info, writeJSON)


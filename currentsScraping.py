
from bs4 import BeautifulSoup
import urllib.request
import json
import pandas as pd

current_stations = pd.read_csv('coops-activecurrentstations.csv')
historical_stations = pd.read_csv('coops-historiccurrentstations.csv')

station_id_list = []
for ID in current_stations['Station ID']:
    station_id_list.append(ID)
for ID in historical_stations['Station ID']:
    station_id_list.append(ID)

currentStationDict = {}
sampleIntervalDict = {}
x = 0

for i, station_id in enumerate(station_id_list):
    print('{} of {}, have saved {}'.format(i, len(station_id_list), x))
    current_prefix = "https://tidesandcurrents.noaa.gov/cdata/StationInfo?id="

    with urllib.request.urlopen(current_prefix + station_id) as url:
        current_html = url.read()

    soup = BeautifulSoup(current_html, "html.parser")
    tables = soup.find_all('table')
    for i, table in enumerate(tables):
        headers = table.find_all('thead')
        for header in headers:
            header_titles = [th.get_text() for th in header.find_all('th')]
            singleDeploymentTitles = ['Attribute', 'Value']
            multipleDeploymentTitles = ['Deployed', 'Recovered', 'Latitude', 'Longitude']
            if all(title in singleDeploymentTitles for title in header_titles):
                rows = table.tbody.find_all('tr')
                dataList = [[td.get_text() for td in tr.findAll("td")] for tr in rows]
                dataDict = {data[0]: data[1] for data in dataList}
                currentStationDict[station_id] = dataDict['Deployment/Recovery Dates (UTC)'].split(' / ')
                currentStationDict[station_id].append(dataDict['Latitude'])
                currentStationDict[station_id].append(dataDict['Longitude'])
                sampleIntervalDict[station_id] = dataDict['Sample Interval']
                x += 1

            elif all(title in multipleDeploymentTitles for title in header_titles):
                rows = table.tbody.find_all('tr')
                currentStationDict[station_id] = [[td.get_text() for td in tr.findAll("td")] for tr in rows]
                print(currentStationDict[station_id])

with open("current_station_info.json", "w") as writeJSON:
    json.dump(currentStationDict, writeJSON)

with open("current_station_intervals.json", "w") as writeJSON:
    json.dump(sampleIntervalDict, writeJSON)

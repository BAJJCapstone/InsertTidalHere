from bs4 import BeautifulSoup
import urllib.request
import json
import pandas as pd

prefix = 'https://tidesandcurrents.noaa.gov/'

station_url = 'https://tidesandcurrents.noaa.gov/stations.html?type=Historic+Water+Levels'
with urllib.request.urlopen(station_url) as url:
    station_html = url.read()

soup = BeautifulSoup(station_html, "html.parser")

stations = soup.find_all('div', {'class': lambda L: L and L.startswith('span4 station')})

with open('availableTypes.txt', 'r') as possible_data:
    column_list = []
    for line in possible_data:
        column_list.append(line.strip())

date_dataframe = pd.DataFrame(columns = column_list)


for station in stations:
    date_dataframe.loc[station.a.get_text().split()[0]] = 'NULL'
    with urllib.request.urlopen(prefix + station.a["href"]) as url: #open individual station
        individual_html = url.read()
    individual_soup = BeautifulSoup(individual_html, "html.parser") # parse the page
    table = individual_soup.find_all('tr') #find the table of available data
    for table_row in table[1:]: # skip the header
        data_type = table_row.find_all('td')[0].get_text().replace(u'\xa0',u'')
        dates_string = '{} - {}'.format(table_row.find_all('td')[1].get_text(), table_row.find_all('td')[2].get_text())
        date_dataframe[data_type][station.a.get_text().split()[0]] = dates_string


date_dataframe.to_pickle('dates.pkl')

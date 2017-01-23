
# coding: utf-8

# In[2]:

from bs4 import BeautifulSoup
import urllib.request
import json
import pandas as pd


# In[6]:

current_stations = pd.read_csv('coops-activecurrentstations.csv')
historical_stations = pd.read_csv('coops-historiccurrentstations.csv')

station_id_list = []
for ID in current_stations['Station ID']:
    station_id_list.append(ID)
for ID in historical_stations['Station ID']:
    station_id_list.append(ID)


# In[42]:

current_url = "https://tidesandcurrents.noaa.gov/cdata/StationInfo?id=cb0102"

with urllib.request.urlopen(current_url) as url:
    current_html = url.read()

soup = BeautifulSoup(current_html, "html.parser")
# print(soup.prettify())
tables = soup.find_all('table')
for i, table in enumerate(tables):
    headers = table.find_all('thead')
    for header in headers:
        header_titles = [th.get_text() for th in header.find_all('th')]
        desired_titles = ['Deployed', 'Recovered', 'Latitude', 'Longitude']
        for header_title, desired_title in zip(header_titles, desired_titles):
            if header_title != desired_title:
                break
        else:
            for entry in table.tbody.find_all('tr')[0]:
                current_info = [data.get_text for data in entry.find_all('td')]
            
    


# In[ ]:




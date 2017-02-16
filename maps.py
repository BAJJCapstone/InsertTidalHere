
# coding: utf-8

# In[2]:

import json
with open('current_station_info.json', 'r') as station_info_file:
    currents_station_info = json.load(station_info_file)


# In[3]:

import re

latitude = []
longitude = []
stations = []
for key, date_list in currents_station_info.items():
    if any(isinstance(el, list) for el in date_list):
        stations.append(key)
        latitude.append(date_list[0][2])
        longitude.append(date_list[0][3])
    else:
        stations.append(key)
        latitude.append(date_list[2])
        longitude.append(date_list[3])       

def convert(tude):
    multiplier = 1 if tude[-1] in ['N', 'E'] else -1
    return multiplier * sum(float(x) / 60 ** n for n, x in enumerate(tude[:-3].split('° ')))
        
dec_latitude = [convert(string) for string in latitude]
dec_longitude = [convert(string) for string in longitude]


# In[53]:

import json
from bs4 import BeautifulSoup
import urllib.request

with open('station_info.json', 'r') as station_info_file:
    tidal_station_info = json.load(station_info_file)

    
def retrieveLocationData(station_id):

    station_url = 'https://tidesandcurrents.noaa.gov/stationhome.html?id={}'.format(station_id)
    with urllib.request.urlopen(station_url) as url:
        station_html = url.read()

    soup = BeautifulSoup(station_html, "html.parser")
    table = soup.find_all('tr') #find the table of available data
    got_latitude = False
    got_longitude = False
    try:
        for table_row in table: # skip the header
            data_type = table_row.find_all('td')[0].get_text()
            if 'Latitude' in data_type: 
                latitude = table_row.find_all('td')[1].get_text()
                got_latitude = True
            if 'Longitude' in data_type: 
                longitude = table_row.find_all('td')[1].get_text()
                got_longitude = True
            if got_longitude and got_latitude:
                return latitude, longitude
    except:
        return None
    
location_dictionary = {}
for key, station_id in tidal_station_info['ID'].items():
    location_tuple = retrieveLocationData(station_id)
    if location_tuple:
        location_dictionary[key] = location_tuple
    else:
        print('Unable to find {}:{}'.format(key, station_id))
        
with open("tidal_location_dictionary.json", "w") as writeJSON:
    json.dump(location_dictionary, writeJSON)


# In[4]:

import json

with open("tidal_location_dictionary.json", "r") as readJSON:
    location_dictionary = json.load(readJSON)

tidal_longitude = []
tidal_latitude = []

for key, loc_tuple in location_dictionary.items():
    tidal_latitude.append(convert(loc_tuple[0]))
    tidal_longitude.append(convert(loc_tuple[1]))


# In[15]:

import plotly.plotly as py
import pandas as pd

scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]

data = [dict(
        type = 'scattergeo',
        name = 'Tidal Measurement Stations',
        locationmode = 'USA-states',
        lon = tidal_longitude,
        lat = tidal_latitude,
        text = stations,
        mode = 'markers',
        marker = dict(symbol = 'square-open',
                     color = 'black')),
        ]

layout = dict(
        title = 'Tidal',
        titlefont = dict(
            size = 26,
            color = 'black'),
        paper_bgcolor='transparent',
        plot_bgcolor='transparent',
        legend = dict(
        orientation = 'h',
        xanchor = 'center',
        x=0.5,
        font = dict(
        size = '20',
        color = 'black')),
        geo = dict(
            scope='usa',
            showland = True,
            landcolor = "transparent",
            subunitcolor = "black",
            countrycolor = "black",
            bgcolor = 'transparent',
            countrywidth = 1,
            subunitwidth = 0.5        
        ),
    )

fig = dict( data=data, layout=layout )
py.iplot( fig, validate=False, filename='coops-tidal-stations' )


# In[14]:

data = [dict(
        type = 'scattergeo',
        name = 'Current Measurement Stations',
        locationmode = 'USA-states',
        lon = dec_longitude,
        lat = dec_latitude,
        text = stations,
        mode = 'markers',
        marker = dict(symbol = 'triangle-up-open'
                     ,color = 'black'))]

layout = dict(
        title = 'Currents',
        titlefont = dict(
            size = 26,
            color = 'black'),
        paper_bgcolor='transparent',
        plot_bgcolor='transparent',
        legend = dict(
        orientation = 'h',
        xanchor = 'center',
        x=0.5,
        font = dict(
        size = '20',
        color = 'black')),
        geo = dict(
            scope='usa',
            showland = True,
            landcolor = "transparent",
            subunitcolor = "black",
            countrycolor = "black",
            bgcolor = 'transparent',
            countrywidth = 1,
            subunitwidth = 0.5        
        ),
    )
fig = dict( data=data, layout=layout )
py.iplot( fig, validate=False, filename='coops-currents-stations' )



# In[ ]:




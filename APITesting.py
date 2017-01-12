
# coding: utf-8

# In[1]:

import requests
import json
from pandas.io.json import json_normalize
import pandas as pd

with open('token.json') as token_file:
    header = json.load(token_file)


# In[36]:

pd_stations = pd.read_json('station_info.json')
pd_stations


# In[34]:

import re
from time import strptime
import datetime

def datesToInt(date):
    
    if date = 'present':
        date_string = time.strftime("%x")
        now = datetime.datetime.now()
        return now.year, now.month, now.day
    date_list = re.findall(r"[\w']+", date)
    day = int(date_list[1])
    year = int(date_list[2])
    month = int(strptime(date_list[0],'%b').tm_mon)
    
    return year, month, day


# In[37]:

import datetime
now = datetime.datetime.now()
type(now.year)


# In[40]:


def retrieveLifetimeData(pandas_thing):
    date_range_string = pandas_thing['date']
    station_id = pandas_thing['ID']

    dates = date_range_string.split('-')
    assert dates[0] != ''
    year, month, day = datesToInt(dates[0])

    end_year, end_month, end_day = datesToInt(dates[1])

    pd_metadata = json_normalize(resp.json()['metadata'])
    pd_metadata.columns = ['Station ID', 'Latitude', 'Longitude', 'Location']
    pd_data = json_normalize(resp.json()['data'])
    first_loop = True
    while 1:
        end_loop = False
        if year < end_year and month+1 < end_month and day < end_day:
            url = 'https://tidesandcurrents.noaa.gov/api/datagetter?'
            params = {
                'begin_date': '{0}/{1}/{2}'.format(month, day, year),
                'end_date':'{0}/{1}/{2}'.format(month+1, day, year),
                'station':station_id,
                'product':'water_level',
                'datum':'mllw',
                'units':'metric',
                'time_zone':'gmt',
                'application':'web_services',
                'format':'json'    
            }
        else:
            url = 'https://tidesandcurrents.noaa.gov/api/datagetter?'
            params = {
                'begin_date': '{0}/{1}/{2}'.format(month, day, year),
                'end_date':'{0}/{1}/{2}'.format(end_month, end_day, end_year),
                'station':station_id,
                'product':'water_level',
                'datum':'mllw',
                'units':'metric',
                'time_zone':'gmt',
                'application':'web_services',
                'format':'json'    
            }            
            end_loop = True
        resp = requests.get(url=url, params=params)
        if first_loop:
            pd_metadata.append(resp.json()['metadata'])
            first_loop = False
        pd_data.append(resp.json()['data'])
        
        month += 1
        if end_loop:
            return pd_metadata, pd_data


# In[46]:

pd_item = pd_stations[0,:]
retrieveLifetimeData(pd_item)


# In[30]:

try:
    pd_metadata = json_normalize(resp.json()['metadata'])
    pd_metadata.columns = ['Station ID', 'Latitude', 'Longitude', 'Location']
    pd_data = json_normalize(resp.json()['data'])
    
except KeyError:
    print(resp.json()['error'])


# In[31]:

# API for Climate Data

url = 'http://www.ncdc.noaa.gov/cdo-web/api/v2/datatypes?datacategoryid=HYDROMETEOR'

resp = requests.get(url=url, headers=header)

try:
    pd_metadata = json_normalize(resp.json()['metadata'])
#     pd_metadata.columns = ['Station ID', 'Latitude', 'Longitude', 'Location']
    pd_results = json_normalize(resp.json()['results'])
    
except KeyError:
    print(resp.json()['error'])
    print('Error in the api input')


# In[32]:

url = 'http://www.ncdc.noaa.gov/cdo-web/api/v2/datacategories?limit=41'
resp = requests.get(url=url, headers=header)

try:
    pd_metadata = json_normalize(resp.json()['metadata'])
    # pd_metadata.columns = ['Station ID', 'Latitude', 'Longitude', 'Location']
    pd_results = json_normalize(resp.json()['results'])
    
except KeyError:
    print(resp.json()['error'])
    print('Error in the api input')


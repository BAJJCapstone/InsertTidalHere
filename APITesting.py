
# coding: utf-8

# In[2]:

import requests
import json
from pandas.io.json import json_normalize
import pandas as pd


# In[3]:

pd_stations = pd.read_json('station_info.json')

prefix = 'https://tidesandcurrents.noaa.gov/inventory.html?id='


# In[4]:

current_stations = pd.readcsv('coops-activecurrentstations.csv')
historical_stations = pd.read_csv('coops-historiccurrentstations.csv')


# In[9]:

historical_stations


# In[6]:

with open('current_station_info.json', 'r') as myFile:
    current_dict = json.load(myFile)

print(len(current_dict.keys()))


# In[5]:

import re
from time import strptime
import datetime

def datesToInt(date):
    if date == 'present':
        date_string = time.strftime("%x")
        now = datetime.datetime.now()
        return now.year, now.month, now.day
    date_list = re.findall(r"[\w']+", date)
    day = int(date_list[1])
    year = int(date_list[2])
    month = int(strptime(date_list[0],'%b').tm_mon)
    
    return year, month, day


# In[6]:

def retrieveLifetimeData(pandas_thing):
    date_range_string = pandas_thing['dates']
    station_id = pandas_thing['ID']

    dates = date_range_string.split('-')
    assert dates[0] != ''
    year, month, day = datesToInt(dates[0])

    end_year, end_month, end_day = datesToInt(dates[1])
    this_is_silly = end_year*10000+end_month*100+end_day

    first_loop = True
    while 1:
        end_loop = False
        
        if month == 12:
            next_year += 1
            next_month = 1
            next_day = day
        else:
            next_year = year
            next_month = month
            next_day = day
        if next_year*10000+next_month*100+end_day < this_is_silly:
            next_year = end_year
            next_day = end_day
            next_month = end_month
            
            
        print('{:02d}/{:02d}/{}'.format(month, day, year))
        print('{:02d}/{:02d}/{}'.format(next_month, day, next_year))
        url = 'https://tidesandcurrents.noaa.gov/api/datagetter?'
        params = {
            'begin_date': '{:02d}/{:02d}/{}'.format(month, day, year),
            'end_date':'{:02d}/{:02d}/{}'.format(next_month, day, year),
            'station':station_id,
            'product':'water_level',
            'datum':'mllw',
            'units':'metric',
            'time_zone':'gmt',
            'application':'web_services',
            'format':'json'    
        }

            
        resp = requests.get(url=url, params=params)
        if first_loop:
            try:
                
                metadata_dict = resp.json()['metadata']
                pd_data = pd.DataFrame(resp.json()['data'])
            except KeyError:
                print(resp.json()['error'])
                return None, None
            
        pd_data.append(resp.json()['data'])
        
        month += 1
        if end_loop:
            return metadata_dict, pd_data


# In[7]:

def retrieveRecentData(pandas_thing):
    station_id = pandas_thing['Station ID']

    url = 'https://tidesandcurrents.noaa.gov/api/datagetter?'
    params = {
        'date':'recent',
        'station':station_id,
        'product':'currents',
        'bin':'1',
        'units':'metric',
        'time_zone':'gmt',
        'application':'web_services',
        'format':'json'    
    }
    resp = requests.get(url=url, params=params)
    try:

        metadata_dict = resp.json()['metadata']
        pd_data = pd.DataFrame(resp.json()['data'])
        return metadata_dict, pd_data    
    
    except KeyError:
        print(resp.json()['error'])
        return None, None



# In[ ]:

url = 'https://tidesandcurrents.noaa.gov/api/datagetter?'
params = {
    'date':'recent',
    'station':station_id,
    'product':'currents',
    'bin':'1',
    'units':'metric',
    'time_zone':'gmt',
    'application':'web_services',
    'format':'json'    
}
resp = requests.get(url=url, params=params)
try:

    metadata_dict = resp.json()['metadata']
    pd_data = pd.DataFrame(resp.json()['data'])
    return metadata_dict, pd_data    

except KeyError:
    print(resp.json()['error'])
    return None, None



# In[8]:

for index, row in current_stations.iterrows():
    metadata_dict, pd_data = retrieveRecentData(row)
    if metadata_dict is not None:
        break
    


# In[10]:

metadata_dict


# In[11]:

pd_data


# In[ ]:

with open('token.json') as token_file:
    header = json.load(token_file)


# In[ ]:

try:
    pd_metadata = json_normalize(resp.json()['metadata'])
    pd_metadata.columns = ['Station ID', 'Latitude', 'Longitude', 'Location']
    pd_data = json_normalize(resp.json()['data'])
    
except KeyError:
    print(resp.json()['error'])


# In[ ]:

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


# In[ ]:

url = 'http://www.ncdc.noaa.gov/cdo-web/api/v2/datacategories?limit=41'
resp = requests.get(url=url, headers=header)

try:
    pd_metadata = json_normalize(resp.json()['metadata'])
    # pd_metadata.columns = ['Station ID', 'Latitude', 'Longitude', 'Location']
    pd_results = json_normalize(resp.json()['results'])
    
except KeyError:
    print(resp.json()['error'])
    print('Error in the api input')


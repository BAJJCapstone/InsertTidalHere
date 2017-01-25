
# coding: utf-8

# In[1]:

import requests
import json
from pandas.io.json import json_normalize
import pandas as pd

import re
import time
from time import strptime
import datetime


# ### Investigating currents 

# In[2]:

with open('current_station_info.json', 'r') as station_info_file:
    currents_station_info = json.load(station_info_file)
    
with open('current_station_intervals.json', 'r') as station_dates_file:
    currents_station_intervals = json.load(station_dates_file)


# In[3]:

def datesToInt(date):
    if date == '':
        date_string = time.strftime("%x")
        now = datetime.datetime.now()
        return '{}{:02d}{:02d} 00:00:00'.format(now.year, now.month, now.day) 
    split_date = re.findall(r"[\w']+", date)
    print(split_date)
    day = int(split_date[1])
    year = int(split_date[2])
    month = int(time.strptime(split_date[0],'%b').tm_mon)
    time = ':'.join(split_date[-3:])
    return '{}{:02d}{:02d} {}'.format(year, month, day, time)


# In[4]:

for key, date_list in currents_station_info.items():
    print('***********Starting with**************: \n {} \n'.format(date_list))
    if any(isinstance(el, list) for el in date_list):
        for i, date in enumerate(date_list):
            print('1.{}'.format(date))
            currents_station_info[key][i] = [element.replace('-','') for element in date]
            print('2.{}'.format(currents_station_info[key][i]))
            if date[1] == '':
                date_string = time.strftime("%x")
                now = datetime.datetime.now()
                currents_station_info[key][0][1] = '{}{:02d}{:02d} 00:00:00'.format(now.year, now.month, now.day)      
                
    else:
        tmp_list = []
        for date in date_list[:1]:
            tmp_list.append(datesToInt(date))
        tmp_list = tmp_list + date_list[2:]
        currents_station_info[key] = tmp_list
    
    print('New Dictionary Entry:{}'.format(currents_station_info[key]))
    print('\n\n\n ***NEXT*** \n\n\n')


# In[ ]:

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


# In[ ]:

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



# In[ ]:

for index, row in current_stations.iterrows():
    metadata_dict, pd_data = retrieveRecentData(row)
    if metadata_dict is not None:
        break
    


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


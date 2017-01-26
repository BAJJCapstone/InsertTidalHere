
# coding: utf-8

# In[10]:

import requests
import json
from pandas.io.json import json_normalize
import pandas as pd

import re
import time
from time import strptime
import datetime


# ### Investigating currents 

# In[11]:

with open('current_station_info.json', 'r') as station_info_file:
    currents_station_info = json.load(station_info_file)
    
with open('current_station_intervals.json', 'r') as station_dates_file:
    currents_station_intervals = json.load(station_dates_file)
    
    


# In[12]:

for key, date_list in currents_station_info.items():
    if any(isinstance(el, list) for el in date_list):
        for i, dates in enumerate(date_list):
            for j, date in enumerate(dates[:1]):
                if date[1] == '':
                    currents_station_info[key][0][1] = datetime.datetime.now()
                    continue
                split_date = re.findall(r"[\w']+", date)
                currents_station_info[key][i][j] = datetime.datetime(year = int(split_date[0]), 
                                month = int(split_date[1]),
                                day = int(split_date[2]), 
                                hour = int(split_date[3]), 
                                minute = int(split_date[4]),
                                second = int(split_date[5]))   
    else:
        for_consistency = []
        tmp_list = []
        for date in date_list[:1]:
            split_date = re.findall(r"[\w']+", date)
            tmp_list.append(datetime.datetime(year = int(split_date[2]), 
                            month = int(strptime(split_date[0],'%b').tm_mon),
                            day = int(split_date[1]), 
                            hour = int(split_date[3]),
                            minute = int(split_date[4]),
                            second = int(split_date[5])))
        
        tmp_list = tmp_list + date_list[2:]
        currents_station_info[key] = for_consistency.append(tmp_list) #put the list inside of another list


# In[ ]:

def retrieveLifetimeData(station_id, date_lists):
    for date_list in date_lists:
        begin_date = date_list[0]
        end_date = date_list[1]
        date = begin_date
        month = datetime.timedelta(month=1)
        first_loop = True
        while 1:
            end_loop = False
            next_date = date + month
            url = 'https://tidesandcurrents.noaa.gov/api/datagetter?'
            params = {
                'begin_date': '{:02d}/{:02d}/{} {:02d}:{:02d}:{:02d}'.format(date.month, date.day, date.year, date.hour, date.minute, date.second),
                'end_date':'{:02d}/{:02d}/{} {:02d}:{:02d}:{:02d}'.format(next_date.month, next_date.day, next_date.year, next_date.hour, next_date.minute, next_date.second),
                'station':station_id,
                'product':'currents',
                'units':'metric',
                'time_zone':'gmt',
                'application':'web_services',
                'format':'json'    
            }
            for i in range(1,10):
                print(i)
                params['bin'] = i
                resp = requests.get(url=url, params=params)
                if first_loop:
                    try:
                        metadata_dict = resp.json()['metadata']
                        pd_data = pd.DataFrame(resp.json()['data'])
                    except KeyError:
                        print(resp.json()['error'])
                        return None, None

            pd_data.merge(resp.json()['data'])
        
        month += 1
        if end_loop:
            return metadata_dict, pd_data


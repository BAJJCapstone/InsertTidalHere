
# coding: utf-8

# In[28]:

## Simple API call to NOAA

import requests
import json
from pandas.io.json import json_normalize


url = 'https://tidesandcurrents.noaa.gov/api/datagetter?'

params = {
    'begin_date':'20130101 10:00',
    'end_date':'20130201 10:24',
    'station':'8454000',
    'product':'currents',
     #'datum':'mllw',
    'units':'metric',
    'time_zone':'gmt',
    'application':'web_services',
    'format':'json'    
}

resp = requests.get(url=url, params=params)
print(resp.json())


# In[24]:

try:
    pd_metadata = json_normalize(resp.json()['metadata'])
    pd_metadata.columns = ['Station ID', 'Latitude', 'Longitude', 'Location']
    pd_data = json_normalize(resp.json()['data'])
    
except KeyError:
    print(resp.json()['error'])
    print('Error in the api input')


# In[20]:

pd_metadata


# In[21]:

pd_data


# In[ ]:




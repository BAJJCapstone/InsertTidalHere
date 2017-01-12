
# coding: utf-8

# In[3]:

## Simple API call to NOAA

import requests
import json
from pandas.io.json import json_normalize


url = 'https://tidesandcurrents.noaa.gov/api/datagetter?'

params = {
    'begin_date':'20160101 10:00',
    'end_date':'20160201 10:00',
    'station':'nb0301',
    'product':'currents',
     #'datum':'mllw',
    'units':'metric',
    'time_zone':'gmt',
    'application':'web_services',
    'format':'json'    
}

resp = requests.get(url=url, params=params)
print(resp.json())


# In[4]:

try:
    pd_metadata = json_normalize(resp.json()['metadata'])
    pd_metadata.columns = ['Station ID', 'Latitude', 'Longitude', 'Location']
    pd_data = json_normalize(resp.json()['data'])
    
except KeyError:
    print(resp.json()['error'])
    print('Error in the api input')


# In[8]:

resp.url


# In[5]:

pd_metadata


# In[7]:

pd_data['b'!=6]


# In[ ]:




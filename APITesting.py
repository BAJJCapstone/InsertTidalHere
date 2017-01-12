
# coding: utf-8

# In[ ]:

import requests
import json
from pandas.io.json import json_normalize

with open('token.json') as token_file:
    header = json.load(token_file)
    print(header)


# In[19]:

url = 'http://www.ncdc.noaa.gov/cdo-web/api/v2/datacategories?limit=41'
resp = requests.get(url=url, headers=header)
print(resp.json())

try:
    pd_metadata = json_normalize(resp.json()['metadata'])
#     pd_metadata.columns = ['Station ID', 'Latitude', 'Longitude', 'Location']
    pd_results = json_normalize(resp.json()['results'])
    
except KeyError:
    print(resp.json()['error'])
    print('Error in the api input')


# In[20]:

pd_results


# In[26]:

url = 'http://www.ncdc.noaa.gov/cdo-web/api/v2/datatypes?datacategoryid=HYDROMETEOR'

resp = requests.get(url=url, headers=header)
print(resp.json())

try:
    pd_metadata = json_normalize(resp.json()['metadata'])
#     pd_metadata.columns = ['Station ID', 'Latitude', 'Longitude', 'Location']
    pd_results = json_normalize(resp.json()['results'])
    
except KeyError:
    print(resp.json()['error'])
    print('Error in the api input')


# In[27]:

pd_results


# In[28]:

# Old version of NOAA API

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


# In[29]:

try:
    pd_metadata = json_normalize(resp.json()['metadata'])
    pd_metadata.columns = ['Station ID', 'Latitude', 'Longitude', 'Location']
    pd_data = json_normalize(resp.json()['data'])
    
except KeyError:
    print(resp.json()['error'])
    print('Error in the api input')


# In[36]:

pd_metadata['Station ID'].value_counts()


# In[30]:

pd_data


# In[34]:




# In[ ]:




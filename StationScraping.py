
# coding: utf-8

# In[2]:

from bs4 import BeautifulSoup
import urllib.request
import json

prefix = 'https://tidesandcurrents.noaa.gov/'

station_url = 'https://tidesandcurrents.noaa.gov/stations.html?type=Historic+Water+Levels'
with urllib.request.urlopen(station_url) as url:
    station_html = url.read()
    
soup = BeautifulSoup(station_html, "html.parser")

stations = soup.find_all('div', {'class': lambda L: L and L.startswith('span4 station')})

types = set()

for station in stations:
    with urllib.request.urlopen(prefix + station.a["href"]) as url:
        individual_html = url.read()
    individual_soup = BeautifulSoup(individual_html, "html.parser")
    available = individual_soup.find_all('tr')
    for data in available[1:]:
        types.add(data.find_all('td')[0].get_text().replace(u'\xa0',u''))
        
print(types)


# In[30]:

print(prefix + stations[0].a["href"])

with urllib.request.urlopen(prefix + stations[0].a["href"]) as url:
    individual_html = url.read()
    
individual_soup = BeautifulSoup(individual_html, "html.parser")    
    
# print(individual_soup.prettify()[3000:4000])

tests = individual_soup.find_all('tr')#, {'class': 'legenditem'})


# In[35]:


for test in tests[1:]:
    print(test.find_all('td')[0].get_text())
    print(test.find_all('td')[1].get_text())
    print(test.find_all('td')[2].get_text())


# In[ ]:

station_info = {}

station_info['ID'] = {}
station_info['dates'] = {}

for station in stations:
    link_suffix = station.a['href']
    key = ''.join(station.a.get_text().split()[1:])
    station_info['dates'][key] = station.span.get_text()
    station_info['ID'][key] = station.a.get_text().split()[0]
    

with open("station_info.json", "w") as writeJSON:
    json.dump(station_info, writeJSON)


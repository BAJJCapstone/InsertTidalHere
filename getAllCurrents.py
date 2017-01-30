
import requests
import json
from pandas.io.json import json_normalize
import pandas as pd

import re
import time
from time import strptime
import datetime

from retry_decorator import retry

import sys
sys.stdout = open('currents_output.log', 'w')

import os.path
current_directory = os.path.dirname(__file__)
saving_directory = os.path.join(current_directory, 'currentData')
if not os.path.exists(saving_directory):
    os.makedirs(saving_directory)

with open('current_station_info.json', 'r') as station_info_file:
    currents_station_info = json.load(station_info_file)

with open('current_station_intervals.json', 'r') as station_dates_file:
    currents_station_intervals = json.load(station_dates_file)

for key, date_list in currents_station_info.items():
    if any(isinstance(el, list) for el in date_list):
        for i, dates in enumerate(date_list):
            for j, date in enumerate(dates[:2]):
                if date == '':
                    currents_station_info[key][0][1] = datetime.datetime.now()
                    continue
                split_date = re.findall(r"[\w']+", date)
                currents_station_info[key][i][j] = datetime.datetime(year = int(split_date[0]),
                                month = int(split_date[1]),
                                day = int(split_date[2]),
                                hour = int(split_date[3]),
                                minute = int(split_date[4]))
    else:
        currents_station_info[key] = []
        tmp_list = []
        for date in date_list[:2]:
            split_date = re.findall(r"[\w']+", date)
            tmp_list.append(datetime.datetime(year = int(split_date[2]),
                            month = int(strptime(split_date[0],'%b').tm_mon),
                            day = int(split_date[1]),
                            hour = int(split_date[3]),
                            minute = int(split_date[4])))
        tmp_list = tmp_list + date_list[2:]
        currents_station_info[key].append(tmp_list) #put the list inside of another list



@retry(Exception)
def retrieveLifetimeData(station_id, date_lists):
    lifetime_data = []
    for date_list in date_lists:
        begin_date = date_list[0]
        begin_date += datetime.timedelta(minutes=begin_date.minute % 6)

        end_date = date_list[1]
        end_date -= datetime.timedelta(minutes=end_date.minute % 6)

        date = begin_date
        month = datetime.timedelta(days=31)
        first_loop = True
        while 1:
            end_loop = False
            next_date = date + month

            if next_date > end_date:
                next_date = end_date
                end_loop = True

            url = 'https://tidesandcurrents.noaa.gov/api/datagetter?'
            params = {
                'begin_date': '{:02d}/{:02d}/{} {:02d}:{:02d}'.format(date.month, date.day, date.year, date.hour, date.minute),
                'end_date':'{:02d}/{:02d}/{} {:02d}:{:02d}'.format(next_date.month, next_date.day, next_date.year, next_date.hour, next_date.minute),
                'station':station_id,
                'product':'currents',
                'units':'metric',
                'time_zone':'gmt',
                'application':'web_services',
                'format':'json'
            }

            bin_list = []

            i=1
            while 1:
                params['bin'] = i
                resp = requests.get(url=url, params=params)
                try:
                    bin_list.append(pd.DataFrame(resp.json()['data']))
                except:
                    break
                bin_list[i-1].drop('b', axis=1, inplace=True)
                bin_list[i-1].set_index('t', inplace=True)
                bin_list[i-1].rename(columns = lambda x : '{}.{}.'.format(station_id, i) + x, inplace = True)
                i += 1
            try:
                monthly_data = pd.concat(bin_list, axis=1)
                lifetime_data.append(monthly_data)
            except ValueError:
                print('No available data for {}  -  {}'.format(date, next_date))
                pass

            date = next_date
            if end_loop:
                break
    print('Done with {}'.format(station_id))
    try:
        lifetime_dataframe = pd.concat(lifetime_data)
        lifetime_dataframe.to_pickle(os.path.join(saving_directory, '{}.pkl'.format(station_id)))
        return lifetime_dataframe, True
    except ValueError:
        print('Error: No available data from - {}'.format(station_id))
        return None, False

all_of_the_data = []
total = len(currents_station_info.keys())
counter = 0
for station_id, available_dates in currents_station_info.items():
    counter += 1

    print('{} of {}'.format(counter, total))
    print('{}:{}'.format(station_id, available_dates))
    if os.path.isfile(os.path.join(saving_directory, '{}.pkl'.format(station_id))):
        print('Already completed {}'.format(station_id))
        all_of_the_data.append(pd.read_pickle(os.path.join(saving_directory, '{}.pkl'.format(station_id))))
        continue

    dataframe, successful = retrieveLifetimeData(station_id, available_dates)
    if successful:
        all_of_the_data.append(dataframe)

imachampion = pd.concat(all_of_the_data, axis=1)
imachampion.to_pickle('currents.pkl')

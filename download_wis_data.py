# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 12:09:39 2024

@author: croland

download_wis_data.py
Summary: Queries the WIS api and downloads CSV to local (https://wisportal.erdc.dren.mil/wis-api/apidocs/#)
Author: Collin Roland
Last modified: 2024/04/05
TO DO: Investigate minimal sleep time that is possible

"""
# %% Import packages

import json
import os
from datetime import datetime, timedelta
import pathlib
import requests
from requests.adapters import HTTPAdapter, Retry
import random
from time import sleep

# %% Self-defined functions


def download_results(url, filename, overwrite=False):
    s = requests.Session()
    retries = Retry(total=5,
                    backoff_factor=0.1,
                    status_forcelist=[ 500, 502, 503, 504 ])
    s.mount('https://', HTTPAdapter(max_retries=retries))
    response = s.get(url)
    path = pathlib.Path(os.path.join(os.getcwd(), filename))
    if overwrite or not path.exists():
        print('downloading {} to {}'.format(filename, path))
        open(filename, 'wb').write(response.content)
    else:
        print('{} already exists, skipping {}'.format(path, filename))
    return response
            
# %% Generate time bounds for request

start_time = datetime(2007, 1, 1, 0, 0, 0)
end_time = datetime(2021, 12, 1, 0, 0, 0)
delta = timedelta(days = 30)
dates = []
while start_time <= end_time:
    dates.append(start_time.date())
    start_time += delta

# %% Build request URL

os.chdir(r'E:\wis_wave\scratch')
url_1 = 'https://wisportal.erdc.dren.mil/wis-api/api/station/data?url=https%3A%2F%2Fchlthredds.erdc.dren.mil%2Fthredds%2FdodsC%2Fwis%2F'
region = 'GreatLakes'
station = 'ST95259'
format_str = 'csv'
variables = 'waveHs,waveTp,waveMeanDirection,waveSpread,windDirection,windSpeed,waveTpPeak'
variables = variables.replace(",", "%2C")
count = 0
while count < len(dates):
    url_all = url_1 + region + '%2F' + station + '%2F' + station + '.nc4&time=' + str(dates[count]) + 'T00%3A00%3A00%2F' + str(dates[count + 1]) + 'T23%3A59%3A59&format=' + format_str + "&variables=" + variables + "&allYears=False"
    filename = station + '_' + dates[count].isoformat().replace("-", "") + '.csv'
    response = download_results(url_all, filename)
    sleep(random.uniform(1, 3))
    count += 1

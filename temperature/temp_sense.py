#!/usr/bin/env python

from datetime import datetime
import json
import time
import requests
import uuid
from bmp180 import Bmp180

house_server_ip = 'http://192.168.0.2:8888'
sensor = Bmp180()
temp_log_file = '/home/gary/office_temp_log.log'

def log_to_file(line):
    with open(temp_log_file, 'a') as f:
        f.write(line + '\n')


def take_temp_reading():
    url = '{0}/office'.format(house_server_ip)
    (temp, pres) = sensor.read_data()
    payload = {
        'id': str(uuid.uuid1()),
        'room': 'office',
        'sensor': 'temperature',
        'temperature': temp,
        'pressure': pres,
        'time': str(datetime.now())
    }
    try:
        # log_to_file(json.dumps(payload))
        # print json.dumps(payload)
        r = requests.post(url, data=json.dumps(payload))
    except requests.exceptions.RequestException as e:    # This is the correct syntax
        print e

def main():

    while True:
        take_temp_reading()
        time.sleep(5.0)

if __name__ == '__main__':
    main()

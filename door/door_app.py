
import time
import requests
import RPi.GPIO as GPIO
from datetime import datetime
import json


GPIO.setmode(GPIO.BCM)

house_server_ip = 'http://192.168.0.2:8888'
door_switch = 23

GPIO.setup(door_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def door_open():
    url = '{0}/door'.format(house_server_ip)
    print url
    payload = {
            'id': 'door_front',
            'status': 'open',
            'time': str(datetime.now())
        }
    try:
        r = requests.post(url, data=json.dumps(payload))
    except requests.exceptions.RequestException as e:    # This is the correct syntax
        print e
    # r = requests.get(url)
    # print r.status_code
    print 'door open'

def main():
    switch_position = 'unknown'

    while True:

        door_state = GPIO.input(door_switch)
        new_switch_position = 'unknown'

        if door_state == False:
            new_switch_position = 'closed'
        else:
            new_switch_position = 'open'

        if new_switch_position != switch_position:
            switch_position = new_switch_position
            if new_switch_position == 'open':
                door_open()
        time.sleep(0.5)

if __name__ == '__main__':
    main()

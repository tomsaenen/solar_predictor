#! python3

import time
from datetime import datetime

from color import BLUE, RED, GREEN, YELLOW, YELLOW_BRIGHT
from solaredge import SolarEdgeConnector
from plc import PLCConnector


def print_time_prefix():
    now = datetime.now()
    print('[' + now.strftime('%H:%M:%S') + ']', end=' ')


def get_battery_level(sec):
    print('Getting battery level... ', end='')
    _, _, _, battery_level = sec.get_site_power_flow(0)
    print('%i%%' % battery_level)
    return battery_level


def write_battery_level(plc, battery_level):
    print('Writing to PLC... ', end='')
    plc.write_db(db=99, offset=404, value=battery_level)
    print(GREEN + 'Done')


# Create connectors
sec = SolarEdgeConnector(verbose=False)
sec.get_sites_list()
print_time_prefix()
plc = PLCConnector(verbose=False)


while True:
    # Get battery level
    print_time_prefix()
    battery_level = get_battery_level(sec)

    # Write to PLC
    print_time_prefix()
    write_battery_level(plc, battery_level)

    # Wait for next iteration
    print('Waiting...', end='')
    time.sleep(30)
    print('\r', end='')

#! python3

import sys
import time
from datetime import datetime

from color import BLUE, RED, GREEN, YELLOW, YELLOW_BRIGHT
from solaredge import SolarEdgeConnector
from plc import PLCConnector


def print_time_prefix():
    now = datetime.now()
    print('[' + now.strftime('%H:%M:%S') + ']', end=' ')


# Create connectors
sec = SolarEdgeConnector(verbose=False)
try:
    sec.get_sites_list()
except Exception as ex:
    print(ex)
    sys.exit()
print_time_prefix()
plc = PLCConnector(verbose=False)

# Infinite loop, stopped by KeyBoardInterrupt
try:
    while True:
        try:
            # Get power flow data
            print_time_prefix()
            print('Getting power flow data... ', end='')
            component_power, component_status, connections, battery_level = sec.get_site_power_flow(0)
            print(GREEN + 'Done')
        except Exception as ex:
            print(ex)
        else:
            try:
                # Write data to PLC
                print_time_prefix()
                print('Writing data to PLC... ', end='')
                plc.write_int_to_db(db=99, offset=404, value=battery_level)
                plc.write_real_to_db(db=99, offset=420, value=component_power['grid'])
                plc.write_real_to_db(db=99, offset=424, value=component_power['house'])
                plc.write_real_to_db(db=99, offset=428, value=component_power['solar'])
                plc.write_real_to_db(db=99, offset=432, value=component_power['battery'])
                print(GREEN + 'Done')
            except Exception as ex:
                print(ex)

        # Wait for next iteration
        print('Waiting...', end='')
        time.sleep(30)
        print('\r', end='')
except KeyboardInterrupt:
    print('\n' + 'Stopped')

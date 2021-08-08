#! python3

import json
import datetime
from collections import defaultdict

import requests
import urllib3
urllib3.disable_warnings() # Ignore InsecureRequestWarning
import pytz

from color import BLUE, RED, GREEN, YELLOW, YELLOW_BRIGHT


class SolarEdgeConnector:
    '''
    Connect and make requests to Solar Edge API
    '''
    def __init__(self, verbose=True, info=False, debug=False):
        # API self.root
        self.root = 'https://monitoringapi.solaredge.com'

        # Verbosity
        self.verbose = verbose
        self.info = info
        self.debug = debug

        # API Date Formats
        # ! Data's are always in the time zone of the site
        self.datetime_format = 'YYYY-MM-DD hh:mm:ss'
        self.date_format = 'YYYY-MM-DD'

        # Rename components
        self.rename_component = {}
        self.rename_component['GRID'] = 'grid'
        self.rename_component['LOAD'] = 'house'
        self.rename_component['PV'] = 'solar'
        self.rename_component['STORAGE'] = 'battery'

        # Import API key
        with open('solaredge_api.json', 'r') as file:
            self.credentials = json.load(file)


    def _get_request(self, root, method, parameter=None, debug=False):
        '''
        GET request to Solar Edge REST API

        Arguments
        ---------
        root      (string)
        method    (string)
        parameter (list)

        debug

        Returns
        -------
        json_data
        '''
        # Build request url
        if parameter == None:
            url = root + method
        else:
            url = root + method + '?' + '&'.join(parameter)

        if debug == True:
            print(YELLOW + '[REQUEST] ' + url)

        # Do request
        response = requests.get(url, verify=False)

        # Check HTTP Status Code
        if response.status_code == 200:
            json_data = response.json()

            if debug == True:
                    print(GREEN + '200 - OK')
                    print(YELLOW + json.dumps(json_data, sort_keys=True, indent=4))

            return json_data

        elif response.status_code == 400:
            raise Exception(RED + '401 - Bad Request')

        elif response.status_code == 401:
            raise Exception(RED + '401 - Authentication Required')

        elif response.status_code == 404:
            raise Exception(RED + '404 - Not Found')

        else:
            raise Exception(RED + 'Unprocessed HTTP Response: %d' % response.status_code)

    ################################ Sites API #################################

    def get_sites_list(self):
        '''
        Sites List
        '''
        # Progress print
        if self.verbose:
            print('Getting sites list... ', end='')

        # Build request
        method = '/sites/list'
        parameter = []
        parameter.append('api_key=' + self.credentials['api_key'])

        # Do request
        json_data = self._get_request(self.root, method, parameter)

        # Extract data
        self.nr_of_sites = json_data['sites']['count']
        self.sites = json_data['sites']['site']

        # Print info
        if self.info:
            print('\n' + BLUE + 'Site List')
            print('Number of sites: ' + str(self.nr_of_sites))
            for i, site in enumerate(self.sites):
                print('\n' + 'Site %d' % (i+1))
                print('  ' + 'Name: ' + str(site['name']))
                print('  ' + 'ID: ' + str(site['id']))
                print('  ' + 'Peak Power: %.2f kWp' % site['peakPower'])
                print('  ' + 'Status: %s' % site['status'])
                #print('\t' + 'Last updated: %s' % site['lastUpdateTime']) # ! Via 'Site Overview' you get Time info as well (this is just Date)

        # Progress print
        if self.verbose:
            print(GREEN + 'Done')


    def get_site_details(self, site_id):
        '''
        Site Details

        ! Provides no extra info compared to site list (checked via debug=True)

        Argument
        --------
        site_id (int)
        '''
        # Progress print
        if self.verbose:
            print('Getting site details... ', end='')

        # Build request
        method = '/site/%s/details' % self.sites[site_id]['id'] # /site/SITE_ID/details
        parameter = []
        parameter.append('api_key=' + self.credentials['api_key'])

        # Do request
        json_data = self._get_request(self.root, method, parameter, debug=False)

        # Progress print
        if self.verbose:
            print(GREEN + 'Done')


    def get_site_energy(self, site_id, start_date, end_date):
        '''
        Site Energy

        Site energy measurements (Wh)
        > can be used to get production for multiple days at a time
        > can also be used to get current production for today, but this makes more sense through 'Site Overview'

        Argument
        --------
        site_id (int)
        start_date  (string)    :   YYYY-MM-DD
        end_date    (string)    :   YYYY-MM-DD

        Returns
        -------
        energy   (dict)  :   {'time'  : list of time (datetime),
                              'value' : list of energy (float) [kWh]}
        '''
        # Progress print
        if self.verbose:
            print('Getting site energy... ', end='')

        # Build request
        method = '/site/%s/energy' % self.sites[site_id]['id'] # /site/SITE_ID/energy
        parameter = []
        parameter.append('startDate=%s' % start_date) # mandatory
        parameter.append('endDate=%s' % end_date) # mandatory
        #parameter.append('timeUnit=HOUR') # QUARTER_OF_AN_HOUR, HOUR, DAY (default), WEEK, MONTH, YEAR
        parameter.append('api_key=' + self.credentials['api_key'])

        # Do request
        json_data = self._get_request(self.root, method, parameter, debug=False)

        # Extract data
        energy = {}
        energy['time'] = []
        energy['value'] = []
        for entry in json_data['energy']['values']:
            unaware_dt = datetime.datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S')
            dt = pytz.timezone('Europe/Brussels').localize(unaware_dt) # timezone aware datetime
            energy['time'].append(dt)
            energy['value'].append(entry['value'] / 1000) # Wh to kWh

        # Print info
        if self.info:
            print('\n' + BLUE + 'Site Energy')
            for i, _ in enumerate(energy['time']):
                print(str(energy['time'][i]) + ': ' + str(energy['value'][i]))

        # Progress print
        if self.verbose:
            print(GREEN + 'Done')

        # Return data
        return energy


    def get_site_power(self, site_id, start_time, end_time):
        '''
        Site Power

        Site power measurements
        - in 15 minutes resolution (QUARTER_OF_AN_HOUR fixed)
        - limited to one-month period

        ! = inverter measurements (solar + battery to house)

        Arguments
        ---------
        site_id     (int)
        start_time  (string)    :   YYYY-MM-DD hh:mm:ss
        end_time    (string)    :   YYYY-MM-DD hh:mm:ss

        Returns
        -------
        power   (dict)  :   {'time'  : list of time (datetime),
                             'value' : list of power (float) [kW]}
        '''
        # Progress print
        if self.verbose:
            print('Getting site power measurements... ', end='')

        # Build request
        method = '/site/%s/power' % self.sites[site_id]['id'] # /site/SITE_ID/power
        parameter = []
        parameter.append('startTime=%s' % start_time.replace(' ','%20')) # mandatory
        parameter.append('endTime=%s' % end_time.replace(' ','%20')) # mandatory
        parameter.append('api_key=' + self.credentials['api_key'])

        # Do request
        json_data = self._get_request(self.root, method, parameter, debug=False)

        # Extract data
        power = {}
        power['time'] = []
        power['value'] = []
        for entry in json_data['power']['values']:
            unaware_dt = datetime.datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S')
            dt = pytz.timezone('Europe/Brussels').localize(unaware_dt) # timezone aware datetime
            if entry['value'] != None:
                power['time'].append(dt)
                power['value'].append(entry['value'] / 1000) # W to kW

        # Print info
        if self.info:
            print('\n' + BLUE + 'Site Power Measurements')
            for i, _ in enumerate(power['time']):
                print(str(power['time'][i]) + ': ' + str(power['value'][i]))

        # Progress print
        if self.verbose:
            print(GREEN + 'Done')

        # Return data
        return power


    def get_site_overview(self, site_id):
        '''
        Site Overview

        Argument
        --------
        site_id     (int)

        Returns
        -------
        last_update         (datetime)  :
        current_power       (float)     : [W]
        current_production  (float)     : [Wh]
        '''
        # Progress print
        if self.verbose:
            print('Getting site overview... ', end='')

        # Build request
        method = '/site/%s/overview' % self.sites[site_id]['id'] # /site/SITE_ID/overview
        parameter = []
        parameter.append('api_key=' + self.credentials['api_key'])

        # Do request
        json_data = self._get_request(self.root, method, parameter, debug=False)

        # Extract data
        current_power = json_data['overview']['currentPower']['power'] # W
        current_production = json_data['overview']['lastDayData']['energy'] # Wh
        last_update_string = json_data['overview']['lastUpdateTime']

        format = '%Y-%m-%d %H:%M:%S'
        unaware_last_update = datetime.datetime.strptime(last_update_string, format)
        last_update = pytz.timezone('Europe/Brussels').localize(unaware_last_update) # timezone aware datetime

        # Print info
        if self.info:
            print('\n' + BLUE + 'Current values')
            print('Current power: %.2f kW' % (current_power/1000))
            print('Current production: %.2f kWh' % (current_production/1000))
            print('Last update: %s' % last_update_string)

        # Progress print
        if self.verbose:
            print(GREEN + 'Done')

        # Return result
        return last_update, current_power, current_production


    def get_site_power_flow(self, site_id):
        '''
        Site Power Flow

        Current power flow (PV array, battery, consumption, grid)

        Argument
        --------
        site_id (int)
        '''
        # Progress print
        if self.verbose:
            print('Getting site power flow... ', end='')

        # Build request
        method = '/site/%s/currentPowerFlow' % self.sites[site_id]['id'] # /site/SITE_ID/overview
        parameter = []
        parameter.append('api_key=' + self.credentials['api_key'])

        # Do request
        json_data = self._get_request(self.root, method, parameter, debug=False)

        # Extract data
        component_power = {}
        for key in self.rename_component.keys():
            component_power[self.rename_component[key]] = json_data['siteCurrentPowerFlow'][key]['currentPower']

        component_status = {}
        for key in self.rename_component.keys():
            component_status[self.rename_component[key]] = json_data['siteCurrentPowerFlow'][key]['status']

        connections = json_data['siteCurrentPowerFlow']['connections']
        for connection in connections:
            for key in connection:
                connection[key] = self.rename_component[connection[key].upper()]

        battery_level = json_data['siteCurrentPowerFlow']['STORAGE']['chargeLevel'] # %

        # Print info
        if self.info:
            print('\n' + BLUE + 'Power Flow')

            for name, power in component_power.items():
                print('%s %s %.2f kW' % (name.title().ljust(9), component_status[name].ljust(13), power))

            print('\n' + 'Connections:')
            for connection in connections:
                print('\t' + '%s --> %s' % (connection['from'].title(), connection['to'].title()))

            print('\n' + 'Battery level: %d%%' % battery_level)

        # Progress print
        if self.verbose:
            print(GREEN + 'Done')


    def get_storage_information(self, site_id, start_time, end_time):
        '''
        Storage Information

        Detailed information from batteries (state of energy, power, lifetime energy)
        - limited to one-week period
        - in 5 minutes resolution
        > used to get battery history

        Argument
        --------
        site_id     (int)
        start_time  (string)    :   YYYY-MM-DD hh:mm:ss
        end_time    (string)    :   YYYY-MM-DD hh:mm:ss

        Returns
        -------
        battery_data (list of dicts)    :  one dict per battery, for which each key returns a list:
            {
             'time'             : timestamps (datetime)
             'batteryState'     : 0=Invalid, 1=Standby, 2=ThermalMgmt, 3=Enabled, 4=Fault
             'stateOfCharge'    : % charged (of available capacity)

             'power'            : positive power = charging, negative = discharging
             'ACGridCharging'   : charging energy from grid (Wh)

             'internalTemp'     : Battery internal temperature (Celsius)

             'lifeTimeEnergyCharged'    : Energy charged during lifetime (Wh)
             'lifeTimeEnergyDischarged' : Energy discharged during lifetime (Wh)
             'fullPackEnergyAvailable'  : Maximum energy that can be stored (Wh)
            }
        '''
        # Progress print
        if self.verbose:
            print('Getting storage information... ', end='')

        # Build request
        method = '/site/%s/storageData' % self.sites[site_id]['id'] # /site/SITE_ID/storageData
        parameter = []
        parameter.append('startTime=%s' % start_time.replace(' ','%20')) # mandatory
        parameter.append('endTime=%s' % end_time.replace(' ','%20')) # mandatory
        parameter.append('api_key=' + self.credentials['api_key'])

        # Do request
        json_data = self._get_request(self.root, method, parameter, debug=False)

        # Extract data
        nr_of_batteries = json_data['storageData']['batteryCount']
        batteries = json_data['storageData']['batteries']

        battery_data = []
        for battery in batteries:
            battery_data.append(defaultdict(list))
            for entry in battery['telemetries']:
                for key in entry:
                    if key == 'timeStamp':
                        unaware_dt = datetime.datetime.strptime(entry[key], '%Y-%m-%d %H:%M:%S')
                        dt = pytz.timezone('Europe/Brussels').localize(unaware_dt) # timezone aware datetime
                        battery_data[-1]['time'].append(dt)
                    else:
                        battery_data[-1][key].append(entry[key])

        # DEBUG
        if self.debug:
            for battery in battery_data:
                for key in battery:
                    print(YELLOW + key)
                    for entry in battery[key]:
                        print(YELLOW_BRIGHT + str(entry))

        # Print info
        if self.info:
            print('\n' + BLUE + 'Battery Information')
            print('Number of batteries: %d' % nr_of_batteries)
            for i, battery in enumerate(batteries):
                print('\n' + 'Battery %d' % (i+1))
                print('  ' + 'Model: %s' % battery['modelNumber'])
                print('  ' + 'Serial Number: %s' % battery['serialNumber'])
                print('  ' + 'Capacity: %s Wh' % battery['nameplate'])

        # Progress print
        if self.verbose:
            print(GREEN + 'Done')

        # Return data
        return battery_data

    ############################ Site Equipment API ############################

    def get_inventory(self, site_id):
        '''
        Inventory

        Inventory of SolarEdge equipment in the site:
        - inverters (SMI's)
        - batteries
        - meters
        - gateways
        - sensors

        Argument
        --------
        site_id (int)
        '''
        # Progress print
        if self.verbose:
            print('Getting site inventory... ', end='')

        # Build request
        method = '/site/%s/inventory' % self.sites[site_id]['id'] # /site/SITE_ID/inventory
        parameter = []
        parameter.append('api_key=' + self.credentials['api_key'])

        # Do request
        json_data = self._get_request(self.root, method, parameter, debug=False)

        # Extract data
        inventory = json_data['Inventory']

        # Print info
        if self.info:
            print('\n' + BLUE + 'Site Inventory')

            print('Inverters: %d' % len(inventory['inverters']))
            if len(inventory['inverters']) > 0:
                for item in inventory['inverters']:
                    print('  ' + '%s' % item['SN'], end=' ')
                    print('(Connected optimizers: %d)' % item['connectedOptimizers'])

            print('Batteries: %d' % len(inventory['batteries']))
            if len(inventory['batteries']) > 0:
                for item in inventory['batteries']:
                    print('  ' + '%s' % item['model'])

            print('Meters: %d' % len(inventory['meters']))
            if len(inventory['meters']) > 0:
                for item in inventory['meters']:
                    print('  ' + '%s (%s)' % (item['name'], item['form']))

            print('Sensors: %d' % len(inventory['sensors']))
            print('Gateways: %d' % len(inventory['gateways']))

        # Progress print
        if self.verbose:
            print(GREEN + 'Done')


if __name__ == '__main__':
    sec = SolarEdgeConnector(verbose=False, info=True)
    # Sites API
    sec.get_sites_list()
    sec.get_site_energy(0, '2021-08-07', '2021-08-07')
    sec.get_site_power(0, '2021-08-04 00:00:00', '2021-08-04 23:59:59')
    sec.get_site_overview(0)
    sec.get_site_power_flow(0)
    sec.get_storage_information(0, '2021-08-04 00:00:00', '2021-08-04 03:59:59')
    # Site Equipment API
    sec.get_inventory(0)

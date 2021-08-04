#! python3

################################ SolarEdge API #################################
#               Copyright (c) 2021 Tom Saenen <tomsaenen@me.com>               #
################################################################################

import json
import datetime

import requests
import urllib3
urllib3.disable_warnings() # Ignore InsecureRequestWarning

from color import RED, GREEN, YELLOW, BLUE

verbose = True
debug = True

################################################################################

root = 'https://monitoringapi.solaredge.com'

# API Date Formats
# ! Data's are always in the time zone of the site
datetime_format = 'YYYY-MM-DD hh:mm:ss'
date_format = 'YYYY-MM-DD'

# Rename components
rename_component = {}
rename_component['GRID'] = 'grid'
rename_component['LOAD'] = 'house'
rename_component['PV'] = 'solar'
rename_component['STORAGE'] = 'battery'

################################################################################

# Import API key
with open('solaredge_api.json', 'r') as file:
    credentials = json.load(file)

################################################################################

def get_rest(root, method, parameter=None, debug=False):
    '''
    GET request to Solar Edge

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

################################## Sites API ###################################

#--------------------------------- Site List ----------------------------------#

print(BLUE + 'Site List')

# Build request
method = '/sites/list'
parameter = []
parameter.append('api_key=' + credentials['api_key'])

json_data = get_rest(root, method, parameter)

# Print sites info
nr_of_sites = json_data['sites']['count']
print('Number of sites: ' + str(nr_of_sites))

sites = json_data['sites']['site']
for i, site in enumerate(sites):
    print('\n' + 'Site %d' % (i+1))
    print('  ' + 'Name: ' + str(site['name']))
    print('  ' + 'ID: ' + str(site['id']))
    print('  ' + 'Peak Power: %.2f kWp' % site['peakPower'])
    print('  ' + 'Status: %s' % site['status'])
    #print('\t' + 'Last updated: %s' % site['lastUpdateTime']) # ! Via 'Site Overview' you get Time info as well (this is just Date)

#-------------------------------- Site Details --------------------------------#

# ! Provides no extra info compared to site list (checked via debug=True)

# method = '/site/%s/details' % sites[0]['id'] # /site/SITE_ID/details
# parameter = []
# parameter.append('api_key=' + credentials['api_key'])
#
# json_data = get_rest(root, method, parameter, debug=False)

#-------------------------------- Site Energy ---------------------------------#

# Site energy measurements (Wh)
# > can be used to get production for multiple days at a time
# > can also be used to get current production for today, but this makes more sense through 'Site Overview'

# method = '/site/%s/energy' % sites[0]['id'] # /site/SITE_ID/energy
# parameter = []
# parameter.append('startDate=2021-08-04') # mandatory
# parameter.append('endDate=2021-08-04') # mandatory
# #parameter.append('timeUnit=HOUR') # QUARTER_OF_AN_HOUR, HOUR, DAY (default), WEEK, MONTH, YEAR
# parameter.append('api_key=' + credentials['api_key'])
#
# json_data = get_rest(root, method, parameter, debug=False)
#
# # Extract data
# current_production = json_data['energy']['values'][0]['value'] # Wh
#
# # Print info
# print('Current power: %.2f kWh' % (current_production/1000))

#--------------------------------- Site Power ---------------------------------#

# Site power measurements
# - in 15 minutes resolution (QUARTER_OF_AN_HOUR fixed)
# - limited to one-month period
print('\n' + BLUE + 'Site Power Today')

# Build request
method = '/site/%s/power' % sites[0]['id'] # /site/SITE_ID/power
parameter = []
parameter.append('startTime=2021-08-04%2000:00:00') # mandatory
parameter.append('endTime=2021-08-04%2023:59:59') # mandatory
parameter.append('api_key=' + credentials['api_key'])

json_data = get_rest(root, method, parameter, debug=False)

# Extract data
power = {}
for entry in json_data['power']['values']:
    dt = datetime.datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S')
    power[dt] = entry['value'] # W

if debug == True:
    for key in power:
        print(str(key) + ': ' + str(power[key]))

#------------------------------- Site Overview --------------------------------#

# Site overview data
print('\n' + BLUE + 'Current values')

# Build request
method = '/site/%s/overview' % sites[0]['id'] # /site/SITE_ID/overview
parameter = []
parameter.append('api_key=' + credentials['api_key'])

# Do request
json_data = get_rest(root, method, parameter, debug=False)

# Extract data
current_power = json_data['overview']['currentPower']['power'] # W
current_production = json_data['overview']['lastDayData']['energy'] # Wh
last_update = json_data['overview']['lastUpdateTime']

# Print info
print('Current power: %.2f kW' % (current_power/1000))
print('Current production: %.2f kWh' % (current_production/1000))
print('Last update: %s' % last_update)

#------------------------------ Site Power Flow -------------------------------#

# Current power flow (PV array, battery, consumption, grid)
print('\n' + BLUE + 'Power Flow')

# Build request
method = '/site/%s/currentPowerFlow' % sites[0]['id'] # /site/SITE_ID/overview
parameter = []
parameter.append('api_key=' + credentials['api_key'])

# Do request
json_data = get_rest(root, method, parameter, debug=False)

# Extract data
component_power = {}
for key in rename_component.keys():
    component_power[rename_component[key]] = json_data['siteCurrentPowerFlow'][key]['currentPower']

component_status = {}
for key in rename_component.keys():
    component_status[rename_component[key]] = json_data['siteCurrentPowerFlow'][key]['status']

connections = json_data['siteCurrentPowerFlow']['connections']
for connection in connections:
    for key in connection:
        connection[key] = rename_component[connection[key].upper()]

battery_level = json_data['siteCurrentPowerFlow']['STORAGE']['chargeLevel'] # %

# Print info
for name, power in component_power.items():
    print('%s %s %.2f kW' % (name.title().ljust(9), component_status[name].ljust(8), power))

print('\n' + 'Connections:')
for connection in connections:
    print('\t' + '%s --> %s' % (connection['from'].title(), connection['to'].title()))

print('\n' + 'Battery level: %d%%' % battery_level)

#---------------------------- Storage Information -----------------------------#

# Detailed information from batteries (state of energy, power, lifetime energy)
# - limited to one-week period
# - in 5 minutes resolution
# > used to get battery history
print('\n' + BLUE + 'Battery Information')

# Build request
method = '/site/%s/storageData' % sites[0]['id'] # /site/SITE_ID/storageData
parameter = []
parameter.append('startTime=2021-08-04%2000:00:00') # mandatory
parameter.append('endTime=2021-08-04%2003:59:59') # mandatory
parameter.append('api_key=' + credentials['api_key'])

# Do request
json_data = get_rest(root, method, parameter, debug=False)

# Extract data
nr_of_batteries = json_data['storageData']['batteryCount']
batteries = json_data['storageData']['batteries']

# Print info
print('Number of batteries: %d' % nr_of_batteries)

for i, battery in enumerate(batteries):
    print('\n' + 'Battery %d' % (i+1))
    print('  ' + 'Model: %s' % battery['modelNumber'])
    print('  ' + 'Serial Number: %s' % battery['serialNumber'])
    print('  ' + 'Capacity: %s Wh' % battery['nameplate'])

#! python3

import sys
import warnings
import datetime

import pytz
import pandas as pd
from scipy import integrate
import scipy.interpolate

from color import BLUE, RED, GREEN
from elia import EliaConnector
from solaredge import SolarEdgeConnector
from solar import SolarTimes
from plot import SolarPlot

local_timezone = 'Europe/Brussels' # pytz format

verbose = True
info = False

############################## Process Arguments ###############################

# Today unless other date specified via first argument 'YYYY-MM-DD'
if len(sys.argv) == 1:
    date = datetime.date.today()
elif len(sys.argv) == 2:
    try:
        date = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    except ValueError:
            print(RED + 'Incorrect date format. Syntax: YYYY-MM-DD')
            sys.exit()
else: # len(sys.argv) > 2
    print(RED + 'Too many arguments')
    sys.exit()

################################## Time Range ##################################

# Chosen range
today = datetime.date.today()

if date == today:  time_view = 'today'
elif date > today: time_view = 'future'
elif date < today: time_view = 'past'

# Target timezone
local_tz = pytz.timezone(local_timezone)

########################### Get SolarEdge Peak Power ###########################

sec = SolarEdgeConnector()
sec.get_sites_list()
local_capacity = sec.sites[0]['peakPower'] # [kWp]

############################ Get Elia Forecast Data ############################

# Convert to strings
date_from = date.strftime('%Y-%m-%d')
date_to = (date + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

# Get Elia Data
ec = EliaConnector()
data = ec.get_chart_data(date_from, date_to, region=5, tz=local_timezone)

#----------------------- Recalculate to Local Capacity ------------------------#

# Progress print
if verbose:
    print('Scaling prediction data... ', end='')

# Calculations
for i in range(len(data['MostRecentForecast'])):
    data['PredictedLoadFactor'].append(data['MostRecentForecast'][i] / data['MonitoredCapacity'][i] * 100) # [%]
    data['LocalForecast'].append(data['PredictedLoadFactor'][i]/100 * local_capacity) # [kW]

# Print info
if info:
    df = pd.DataFrame(data)
    df.set_index('time', inplace=True)
    print('\n' + BLUE + 'Prediction Data')
    print(df[['PredictedLoadFactor','LocalForecast']].to_string())

# Progress print
if verbose:
    print(GREEN + 'Done')

#--------------------------------- Integrate ----------------------------------#

# Progress print
if verbose:
    print('Calculating predictions... ', end='')

# Time elapsed since start, in seconds
time_elapsed_s = []
for i in data['time']:
    time_elapsed_s.append((i - data['time'][0]).total_seconds())

# Integrate kW to kJ
total_kj = integrate.simpson(data['LocalForecast'], time_elapsed_s)

# To kWh
predicted_total_kwh = total_kj/3600

#----------------------------- Current production -----------------------------#

if time_view == 'today':
    # Interpolation function
    f = scipy.interpolate.interp1d(time_elapsed_s, data['LocalForecast'], kind='linear')

    # Now (current power)
    datetime_now = datetime.datetime.now(tz=local_tz)
    time_now_s = (datetime_now - data['time'][0]).total_seconds() # seconds since start of day

    predicted_current_power = f(time_now_s)

    # Integrate (current production)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        current_kj, _ = integrate.quad(f, time_elapsed_s[0], time_now_s)
    predicted_current_kwh = current_kj/3600

# Print info
if info:
    print('\n' + BLUE + 'Predictions')
    print('Total daily production: %.2f kWh' % predicted_total_kwh)
    print('Current power: %.2f kW' % predicted_current_power)
    print('Current production: %.2f kWh' % predicted_current_kwh)

# Progress print
if verbose:
    print(GREEN + 'Done')

############################ Get SolarEdge Actuals #############################

if time_view in ('past', 'today'):
    # Date arguments for SolarEdge API
    start_time = date.strftime('%Y-%m-%d 00:00:00')
    end_time = date.strftime('%Y-%m-%d 23:59:59')

    # Get power history
    actual = sec.get_site_power(0, start_time, end_time)

if time_view == 'today':
    # Get current values
    last_update, current_power, current_production = sec.get_site_overview(0)

if time_view == 'past':
    # Date arguments for SolarEdge API
    day = date.strftime('%Y-%m-%d')

    # Get total production
    energy = sec.get_site_energy(0, day, day)

################################### Sun Info ###################################

st = SolarTimes()
sun_times = st.get_times(tz=local_timezone, lat=51.197567558420694, lon=4.716483482278131, date=date)

##################################### Plot #####################################

plot = SolarPlot()

#-------------------------------- Solar Power ---------------------------------#

forecast = {}
forecast['time'] = data['time']
forecast['value'] = data['LocalForecast']

if time_view == 'today':
    plot.solar_power(time_view, local_tz, sun_times, local_capacity,
                     forecast, predicted_total_kwh,
                     predicted_current_power, predicted_current_kwh,
                     actual, current_power/1000, current_production/1000, last_update)
elif time_view == 'future':
    plot.solar_power(time_view, local_tz, sun_times, local_capacity,
                     forecast, predicted_total_kwh)
elif time_view == 'past':
    plot.solar_power(time_view, local_tz, sun_times, local_capacity,
                     forecast, predicted_total_kwh,
                     actual=actual, actual_total_kwh=energy['value'][0])

#--------------------------------- Power Flow ---------------------------------#

# if time_view == 'today':
#     # Get data
#     component_power, component_status, connections = sec.get_site_power_flow(0)
#
#     # Plot
#     plot.power_flow(component_power, component_status, connections)

#------------------------------------------------------------------------------#

plot.show_all()

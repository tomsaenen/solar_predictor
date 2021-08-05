#! python3

import sys
import warnings
import datetime

import pytz
import pandas as pd
from scipy import integrate
import scipy.interpolate
import astral

from color import BLUE
from elia import EliaConnector
from solaredge import SolarEdgeConnector
from plot import SolarPlot

################################################################################

local_timezone = 'Europe/Brussels' # pytz format

latitude = 51.197567558420694
longitude = 4.716483482278131

################################################################################

# Today unless other date specified via first argument 'YYYY-MM-DD'
if len(sys.argv) == 1:
    today = True
    datetime_from = datetime.date.today()
else:
    today = False
    datetime_from = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')

########################### Get SolarEdge Peak Power ###########################

sec = SolarEdgeConnector()
sec.get_sites_list()
local_capacity = sec.sites[0]['peakPower'] # [kWp]

############################ Get Elia Forecast Data ############################

datetime_to = datetime_from + datetime.timedelta(days=1)

# Convert to strings
date_from = datetime_from.strftime('%Y-%m-%d')
date_to = datetime_to.strftime('%Y-%m-%d')

# Get Elia Data
ec = EliaConnector()
time, data = ec.get_chart_data(date_from, date_to, region=5, tz=local_timezone)

#----------------------- Recalculate to Local Capacity ------------------------#

# Calculations
for i in range(len(data['MostRecentForecast'])):
    data['PredictedLoadFactor'].append(data['MostRecentForecast'][i] / data['MonitoredCapacity'][i] * 100) # [%]
    data['LocalForecast'].append(data['PredictedLoadFactor'][i]/100 * local_capacity) # [kW]

# Print info
df = pd.DataFrame(data, index=time)
print('\n' + BLUE + 'Prediction Data')
print(df[['PredictedLoadFactor','LocalForecast']].to_string())

#--------------------------------- Integrate ----------------------------------#

# Time elapsed since start, in seconds
time_elapsed_s = []
for i in time:
    time_elapsed_s.append((i - time[0]).total_seconds())

# Integrate kW to kJ
total_kj = integrate.simpson(data['LocalForecast'], time_elapsed_s)

# To kWh
total_kwh = total_kj/3600

print('\n' + BLUE + 'Predictions')
print('Total daily production: %.2f kWh' % total_kwh)

#----------------------------- Current production -----------------------------#

if today == True:
    # Interpolation function
    f = scipy.interpolate.interp1d(time_elapsed_s, data['LocalForecast'], kind='linear')

    # Now (current power)
    local_tz = pytz.timezone(local_timezone) # target timezone
    datetime_now = datetime.datetime.now(tz=local_tz)
    time_now_s = (datetime_now - time[0]).total_seconds() # seconds since start of day

    current_predicted_power = f(time_now_s)
    print('Current power: %.2f kW' % current_predicted_power)

    # Integrate (current production)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        current_kj, _ = integrate.quad(f, time_elapsed_s[0], time_now_s)
    current_kwh = current_kj/3600
    print('Current production: %.2f kWh' % current_kwh)

############################ Get SolarEdge Actuals #############################

start_time = datetime_from.strftime('%Y-%m-%d 00:00:00')
end_time = datetime_from.strftime('%Y-%m-%d 23:59:59')

actual_power = sec.get_site_power(0, start_time, end_time)

last_update, current_power, current_production = sec.get_site_overview(0)


################################### Sun Info ###################################

if today == True:
    loc = astral.LocationInfo('Brussels', 'Belgium', local_timezone, latitude, longitude)

    from astral.sun import sun
    sun_times = sun(loc.observer, date=datetime_from, tzinfo=local_tz)

    print('\n' + BLUE + 'Solar Info')
    print('Dawn:    %s' % sun_times['dawn'].strftime("%Hu%M"))
    print('Sunrise: %s' % sun_times['sunrise'].strftime("%Hu%M"))
    print('Noon:    %s' % sun_times['noon'].strftime("%Hu%M"))
    print('Sunset:  %s' % sun_times['sunset'].strftime("%Hu%M"))
    print('Dusk:    %s' % sun_times['dusk'].strftime("%Hu%M"))

##################################### Plot #####################################

plot = SolarPlot()
plot.plot(time, data['LocalForecast'], list(actual_power.keys()), list(actual_power.values()), local_tz,
          current_predicted_power, sun_times, local_capacity, total_kwh, current_kwh,
          current_power/1000, current_production/1000, last_update)

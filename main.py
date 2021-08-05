#! python3

import sys
import datetime
import warnings

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy import integrate
import scipy.interpolate
import astral
import pytz

from color import BLUE

################################################################################

local_capacity = 12.09 # [kWp]

local_timezone = 'Europe/Brussels' # pytz format

latitude = 51.197567558420694
longitude = 4.716483482278131

################################################################################

#------------------------------------ Date ------------------------------------#

# Today unless other date specified via first argument 'YYYY-MM-DD'
if len(sys.argv) == 1:
    today = True
    datetime_from = datetime.date.today()
else:
    today = False
    datetime_from = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')

#--------------------------- Get Elia Forecast Data ---------------------------#

datetime_to = datetime_from + datetime.timedelta(days=1)

# Convert to strings
date_from = datetime_from.strftime('%Y-%m-%d')
date_to = datetime_to.strftime('%Y-%m-%d')

# Get Elia Data
from elia import EliaConnector
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

#---------------------------------- Sun Info ----------------------------------#

if today == True:
    loc = astral.LocationInfo('Brussels', 'Belgium', local_timezone, latitude, longitude)

    from astral.sun import sun
    local_tz = pytz.timezone(local_timezone) # target timezone
    sun_times = sun(loc.observer, date=datetime_from, tzinfo=local_tz)

    print('\n' + BLUE + 'Solar Info')
    print('Dawn:    %s' % sun_times['dawn'].strftime("%Hu%M"))
    print('Sunrise: %s' % sun_times['sunrise'].strftime("%Hu%M"))
    print('Noon:    %s' % sun_times['noon'].strftime("%Hu%M"))
    print('Sunset:  %s' % sun_times['sunset'].strftime("%Hu%M"))
    print('Dusk:    %s' % sun_times['dusk'].strftime("%Hu%M"))

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
    datetime_now = datetime.datetime.now(tz=local_tz)
    time_now_s = (datetime_now - time[0]).total_seconds() # seconds since start of day

    current_power = f(time_now_s)
    print('Current power: %.2f kW' % current_power)

    # Integrate (current production)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        current_kj, _ = integrate.quad(f, time_elapsed_s[0], time_now_s)
    current_kwh = current_kj/3600
    print('Current production: %.2f kWh' % current_kwh)

##################################### Plot #####################################

#plt.style.use('dark_background')

cm = 1/2.54 # inch
plt.figure(figsize=(35*cm,18*cm))

lines = plt.plot(time, data['LocalForecast'], linewidth = 1, label='Predicted')
forecast_color = lines[0].get_color()
lines = plt.plot(time[0],0, label='Actual')
actual_color = lines[0].get_color()

plt.legend(loc='lower left', bbox_to_anchor=(-0.2, 0.0))

plt.subplots_adjust(left=0.28, right=0.92, top=0.9, bottom=0.1)

plt.suptitle('Solar Power Forecast', fontweight='bold', fontsize= 15)
plt.ylabel('[kW]')

plt.xlim(time[0], time[-1])

plt.grid(which='major', alpha=0.5)
plt.grid(which='minor', alpha=0.5)

plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz=local_tz))
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y', tz=local_tz))

plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=2, tz=local_tz))
plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%Hu', tz=local_tz))

# Current time
plt.axvline(x=datetime_now, color='r', linestyle='dashed', linewidth=1, alpha=0.7)

label = datetime_now.strftime('%Hu%M')
trans = plt.gca().get_xaxis_transform()
plt.text(datetime_now, 1.01, label, transform=trans,
         horizontalalignment = 'center',
         verticalalignment = 'bottom',
         color='r')

# Current predicted power
plt.axhline(y=current_power, color=forecast_color, linestyle='dashed', linewidth=1, alpha=0.7)

plt.plot(datetime_now, current_power, 'o', color=forecast_color)

trans = plt.gca().get_yaxis_transform()
plt.text(1.01, current_power, '%.2f kW' % current_power, transform=trans,
         horizontalalignment = 'left',
         verticalalignment = 'center',
         color=forecast_color)

#--------------------------------- Sun times ----------------------------------#

# - More top margin for labels
data_range = max(data['LocalForecast']) - min(data['LocalForecast'])
ymin = min(data['LocalForecast']) - 0.05*data_range # default bottom margin
ymax = max(data['LocalForecast']) + 0.10*data_range # more top margin
plt.ylim(ymin,ymax)

plt.twiny()
plt.xlim(time[0], time[-1])

del sun_times['dawn']
del sun_times['dusk']
plot_sun_times = sun_times.copy()
for old_key in sun_times:
    new_key = old_key + '\n' + sun_times[old_key].strftime("%Hu%M")
    plot_sun_times[new_key] = sun_times[old_key]

plt.xticks(ticks=list(plot_sun_times.values()), labels=plot_sun_times.keys())

plt.gca().tick_params(axis='x', direction='in',pad=-28)

#----------------------------------- Table ------------------------------------#

rows = []
rows.append(['Local Capacity', '%.2f' % local_capacity, 'kWp'])
rows.append(['','',''])
rows.append([r'$\bf{Elia\ Predictions}$','',''])
rows.append(['Total daily production', '%.2f' % total_kwh, 'kWh'])
rows.append(['Current power', '%.2f' % current_power, 'kW'])
rows.append(['Current production', '%.2f' % current_kwh, 'kWh'])
rows.append(['','',''])
rows.append([r'$\bf{SolarEdge\ Actuals}$','',''])
rows.append(['Current power','','kW'])
rows.append(['Current production','','kWh'])

nr_of_rows = len(rows)

# Position (axes coordinates)
x0 = -0.39
y0 = 0.65
width = 0.57
height = 0.35

t = plt.table(rows, edges='open', cellLoc='left', bbox=[x0, y0, width, height])
t.auto_set_font_size(False)
#t.set_fontsize(8)
t.auto_set_column_width((0,1,3))

# Color cells
t[2, 0].set_text_props(color=forecast_color)
t[7, 0].set_text_props(color=actual_color)

# Right align numbers
for i in range(nr_of_rows):
    t[i,1].set_text_props(horizontalalignment = 'right')

#------------------------------------------------------------------------------#

plt.savefig('plot.png')
plt.show()

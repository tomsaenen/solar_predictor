#! python3

import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from color import GREEN


class SolarPlot:
    '''
    Plot solar predictions and actual
    '''
    def __init__(self, verbose=True):
        # Verbosity
        self.verbose = verbose


    def plot(self, time_forecast, forecast, time_actual, actual, tz,
             current_predicted_power, sun_times, local_capacity, total_predicted_kwh, current_predicted_kwh,
             current_actual_power, current_actual_kwh, actual_last_updated):
        '''
        Arguments
        ---------
        time        (list)  : time as list of timedata (timezone aware)
        forecast    (list)  :
        actual      (list)  :
        tz

        current_predicted_power
        sun_times
        local_capacity
        total_predicted_kwh
        current_predicted_kwh

        current_actual_power
        current_actual_kwh
        actual_last_updated
        '''
        # Progress print
        if self.verbose:
            print('Plotting... ', end='')

        # Add last values (TODO)
        time_actual.append(actual_last_updated)
        actual.append(current_actual_power)

        for i, j in zip(time_actual,actual):
            print(i, end='\t')
            print(j)

        #plt.style.use('dark_background')

        cm = 1/2.54 # inch
        plt.figure(figsize=(35*cm,18*cm))

        lines = plt.plot(time_forecast, forecast, linewidth = 1, label='Predicted')
        forecast_color = lines[0].get_color()
        lines = plt.plot(time_actual, actual, linewidth = 1, label='Actual')
        actual_color = lines[0].get_color()

        plt.legend(loc='lower left', bbox_to_anchor=(-0.2, 0.0))

        plt.subplots_adjust(left=0.28, right=0.92, top=0.9, bottom=0.1)

        plt.suptitle('Solar Power Forecast', fontweight='bold', fontsize= 15)
        plt.ylabel('[kW]')

        plt.xlim(time_forecast[0], time_forecast[-1])

        plt.grid(which='major', alpha=0.5)
        plt.grid(which='minor', alpha=0.5)

        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz=tz))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y', tz=tz))

        plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=2, tz=tz))
        plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%Hu', tz=tz))

        # Current time
        datetime_now = datetime.datetime.now(tz=tz)
        plt.axvline(x=datetime_now, color='r', linestyle='dashed', linewidth=1, alpha=0.7)

        label = datetime_now.strftime('%Hu%M')
        trans = plt.gca().get_xaxis_transform()
        plt.text(datetime_now, 1.01, label, transform=trans,
                 horizontalalignment = 'center',
                 verticalalignment = 'bottom',
                 color='r')

        # Current predicted power
        plt.axhline(y=current_predicted_power, color=forecast_color, linestyle='dashed', linewidth=1, alpha=0.7)
        plt.plot(datetime_now, current_predicted_power, 'o', color=forecast_color)

        trans = plt.gca().get_yaxis_transform()
        plt.text(1.01, current_predicted_power, '%.2f kW' % current_predicted_power, transform=trans,
                 horizontalalignment = 'left',
                 verticalalignment = 'center',
                 color=forecast_color)

        # Current actual power
        plt.axhline(y=current_actual_power, color=actual_color, linestyle='dashed', linewidth=1, alpha=0.7)
        plt.plot(actual_last_updated, current_actual_power, 'o', color=actual_color)

        plt.text(1.01, current_actual_power, '%.2f kW' % current_actual_power, transform=trans,
                 horizontalalignment = 'left',
                 verticalalignment = 'center',
                 color=actual_color)

        #--------------------------------- Sun times ----------------------------------#

        # - More top margin for labels
        forecast_data_range = max(forecast) - min(forecast)
        forecast_ymin = min(forecast) - 0.05*forecast_data_range # default bottom margin
        forecast_ymax = max(forecast) + 0.10*forecast_data_range # more top margin

        actual = [x for x in actual if x is not None]

        actual_data_range = max(actual) - min(actual)
        actual_ymin = min(actual) - 0.05*actual_data_range # default bottom margin
        actual_ymax = max(actual) + 0.10*actual_data_range # more top margin

        ymin = min(forecast_ymin, actual_ymin)
        ymax = max(forecast_ymax, actual_ymax)

        plt.ylim(ymin,ymax)

        plt.twiny()
        plt.xlim(time_forecast[0], time_forecast[-1])

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
        rows.append(['Total daily production', '%.2f' % total_predicted_kwh, 'kWh'])
        rows.append(['Current power', '%.2f' % current_predicted_power, 'kW'])
        rows.append(['Current production', '%.2f' % current_predicted_kwh, 'kWh'])
        rows.append(['','',''])
        rows.append([r'$\bf{SolarEdge\ Actuals}$','',''])
        rows.append(['Current power', '%.2f' % current_actual_power, 'kW'])
        rows.append(['Current production', '%.2f' % current_actual_kwh, 'kWh'])
        rows.append(['Last updated', actual_last_updated.strftime("%Hu%M"), ''])

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
        t[10, 0].set_text_props(color='grey')
        t[10, 1].set_text_props(color='grey')

        # Right align numbers
        for i in range(nr_of_rows):
            t[i,1].set_text_props(horizontalalignment = 'right')

        #------------------------------------------------------------------------------#

        plt.savefig('plot.png')
        plt.show()

        # Progress print
        if self.verbose:
            print(GREEN + 'Done')

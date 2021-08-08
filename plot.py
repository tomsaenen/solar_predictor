#! python3

import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from color import GREEN, YELLOW, YELLOW_BRIGHT


class SolarPlot:
    '''
    Plot solar predictions and actual
    '''
    def __init__(self, verbose=True, debug=False):
        # Verbosity
        self.verbose = verbose
        self.debug = debug


    def plot(self, time_view, tz, sun_times, local_capacity,
             forecast, predicted_total_kwh,
             predicted_current_power=None, predicted_current_kwh=None,
             actual=None, actual_current_power=None, actual_current_kwh=None, actual_last_updated=None, actual_total_kwh=None):
        '''
        Arguments
        ---------
        time_view       (string)    : 'past'/'today'/'future'
        tz
        sun_times
        local_capacity  (float)     : [kWp]

        forecast    (dict)  : {timedata (timezone aware) : value [kW]}
        actual      (dict)  : {timedata (timezone aware) : value [kW]}

        predicted_total_kwh
        predicted_current_power (float)     : (optional) [kW]
        predicted_current_kwh   (float)     : (optional) [kWh]

        actual_current_power    (float)     : (optional) [kW]
        actual_current_kwh      (float)     : (optional) [kWh]
        actual_last_updated     (datetime)  : (optional)

        actual_total_kwh
        '''
        # Progress print
        if self.verbose:
            print('Plotting... ', end='')
            if self.debug: print()

        # Add last value (only if it is later)
        if time_view == 'today':
            if actual_last_updated > actual['time'][-1]:
                actual['time'].append(actual_last_updated)
                actual['value'].append(actual_current_power)

        #plt.style.use('dark_background')

        cm = 1/2.54 # inch
        plt.figure(figsize=(35*cm,18*cm))

        # DEBUG input
        if self.debug:
            print(YELLOW + 'Prediction')
            for i, _ in enumerate(forecast['time']):
                print(YELLOW_BRIGHT + str(forecast['time'][i]) + ': %f' % (forecast['value'][i]))

            if time_view in ('past', 'today'):
                print(YELLOW + 'Actual')
                for i, _ in enumerate(actual['time']):
                    print(YELLOW_BRIGHT + str(actual['time'][i]) + ': %f' % (actual['value'][i]))

        # Plot predictions
        lines = plt.plot(forecast['time'], forecast['value'], linewidth = 1, label='Predicted')
        forecast_color = lines[0].get_color()

        # Plot actuals
        if time_view in ['past', 'today']:
            lines = plt.plot(actual['time'], actual['value'], linewidth = 1, label='Actual')
            actual_color = lines[0].get_color()

        # Plot settings
        plt.legend(loc='lower left', bbox_to_anchor=(-0.2, 0.0))

        plt.subplots_adjust(left=0.28, right=0.92, top=0.9, bottom=0.1)

        plt.suptitle('Solar Power Forecast', fontweight='bold', fontsize= 15)
        plt.ylabel('[kW]')

        plt.xlim(forecast['time'][0], forecast['time'][-1])

        plt.grid(which='major', alpha=0.5)
        plt.grid(which='minor', alpha=0.5)

        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=1, tz=tz))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y', tz=tz))

        plt.gca().xaxis.set_minor_locator(mdates.HourLocator(interval=2, tz=tz))
        plt.gca().xaxis.set_minor_formatter(mdates.DateFormatter('%Hu', tz=tz))

        #--------------------------- Current values ---------------------------#

        if time_view == 'today':
            # Current time
            if predicted_current_power != None:
                datetime_now = datetime.datetime.now(tz=tz)
                plt.axvline(x=datetime_now, color='r', linestyle='dashed', linewidth=1, alpha=0.7)

                label = datetime_now.strftime('%Hu%M')
                trans = plt.gca().get_xaxis_transform()
                plt.text(datetime_now, 1.01, label, transform=trans,
                         horizontalalignment = 'center',
                         verticalalignment = 'bottom',
                         color='r')

            # Current predicted power
            if predicted_current_power != None:
                plt.axhline(y=predicted_current_power, color=forecast_color, linestyle='dashed', linewidth=1, alpha=0.7)
                plt.plot(datetime_now, predicted_current_power, 'o', color=forecast_color)

                trans = plt.gca().get_yaxis_transform()
                plt.text(1.01, predicted_current_power, '%.2f kW' % predicted_current_power, transform=trans,
                         horizontalalignment = 'left',
                         verticalalignment = 'center',
                         color=forecast_color)

            # Current actual power
            if actual_current_power != None:
                plt.axhline(y=actual_current_power, color=actual_color, linestyle='dashed', linewidth=1, alpha=0.7)
                plt.plot(actual_last_updated, actual_current_power, 'o', color=actual_color)

                plt.text(1.01, actual_current_power, '%.2f kW' % actual_current_power, transform=trans,
                         horizontalalignment = 'left',
                         verticalalignment = 'center',
                         color=actual_color)

        #----------------------------- Sun times ------------------------------#

        # - More top margin for labels
        forecast_data_range = max(forecast['value']) - min(forecast['value'])
        forecast_ymin = min(forecast['value']) - 0.05*forecast_data_range # default bottom margin
        forecast_ymax = max(forecast['value']) + 0.10*forecast_data_range # more top margin

        if time_view in ('past', 'today'):
            actual_data_range = max(actual['value']) - min(actual['value'])
            actual_ymin = min(actual['value']) - 0.05*actual_data_range # default bottom margin
            actual_ymax = max(actual['value']) + 0.10*actual_data_range # more top margin

            ymin = min(forecast_ymin, actual_ymin)
            ymax = max(forecast_ymax, actual_ymax)

        elif time_view == 'future':
            ymin = forecast_ymin
            ymax = forecast_ymax

        plt.ylim(ymin,ymax)

        plt.twiny()
        plt.xlim(forecast['time'][0], forecast['time'][-1])

        del sun_times['dawn']
        del sun_times['dusk']
        plot_sun_times = sun_times.copy()
        for old_key in sun_times:
            new_key = old_key + '\n' + sun_times[old_key].strftime("%Hu%M")
            plot_sun_times[new_key] = sun_times[old_key]

        plt.xticks(ticks=list(plot_sun_times.values()), labels=plot_sun_times.keys())

        plt.gca().tick_params(axis='x', direction='in',pad=-28)

        #------------------------------- Table --------------------------------#

        rows = []
        rows.append(['Local Capacity', '%.2f' % local_capacity, 'kWp'])
        rows.append(['','',''])

        # Predictions
        rows.append([r'$\bf{Elia\ Predictions}$','',''])
        elia_row = len(rows)-1
        rows.append(['Total production', '%.2f' % predicted_total_kwh, 'kWh'])
        if predicted_current_power != None:
            rows.append(['Current power', '%.2f' % predicted_current_power, 'kW'])
        if predicted_current_kwh != None:
            rows.append(['Current production', '%.2f' % predicted_current_kwh, 'kWh'])
        rows.append(['','',''])

        # Actuals
        if time_view in ('past', 'today'):
            rows.append([r'$\bf{SolarEdge\ Actuals}$','',''])
            solaredge_row = len(rows)-1

        if time_view == 'today':
            if actual_current_power != None:
                rows.append(['Current power', '%.2f' % actual_current_power, 'kW'])
            if actual_current_kwh != None:
                rows.append(['Current production', '%.2f' % actual_current_kwh, 'kWh'])
            if actual_last_updated != None:
                rows.append(['Last updated', actual_last_updated.strftime("%Hu%M"), ''])
                last_update_row = len(rows)-1

        if time_view == 'past':
            rows.append(['Total production', '%.2f' % actual_total_kwh, 'kWh'])

        nr_of_rows = len(rows)

        # Position (axes coordinates)
        x0 = -0.39
        y0 = 0.65
        width = 0.57
        height = 0.35

        t = plt.table(rows, edges='open', cellLoc='left', bbox=[x0, y0, width, height])
        t.auto_set_font_size(False)
        t.auto_set_column_width((0,1,3))

        # Format cells
        t[elia_row, 0].set_text_props(color=forecast_color)
        if time_view in ('past', 'today'):
            t[solaredge_row, 0].set_text_props(color=actual_color)
            if actual_last_updated != None:
                t[last_update_row, 0].set_text_props(color='grey')
                t[last_update_row, 1].set_text_props(color='grey')
                t[last_update_row, 0].set_fontsize(9)
                t[last_update_row, 1].set_fontsize(9)

        # Right align numbers
        for i in range(nr_of_rows):
            t[i,1].set_text_props(horizontalalignment = 'right')

        #----------------------------------------------------------------------#

        # Progress print
        if self.verbose:
            print(GREEN + 'Done')

        #plt.savefig('plot.png')
        plt.show()

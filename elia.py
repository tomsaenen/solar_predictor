#! python3

from collections import defaultdict
import datetime

import requests
import urllib3
urllib3.disable_warnings()
import xmltodict
import pytz
import pandas as pd

from color import GREEN, BLUE


class EliaConnector:
    '''
    Connect and make requests to Elia API
    '''
    def __init__(self, verbose=True, info=False, debug=False):
        # API self.root
        self.root = 'https://publications.elia.be/Publications/publications/solarforecasting.v4.svc/'

        # Verbosity
        self.verbose = verbose
        self.info = info
        self.debug = debug


    def get_chart_data(self, date_from, date_to, region, tz):
        '''
        Arguments
        ---------
        date_from   (string)    : YYYY-MM-DD
        date_to     (string)    : YYYY-MM-DD
        region      (int)       : region number as specified by Elia
        tz          (string)    : timezone data will be converted to (pytz format)

        Returns
        -------
        data    (defaultdict)   : {datetime (timezone aware) : value}
        '''
        # Progress print
        if self.verbose:
            print('Getting prediction data... ', end='')

        # Build request
        method = 'GetChartDataForZoneXml'
        parameters = 'dateFrom=' + date_from + '&dateTo=' + date_to + '&sourceId=' + str(region)
        url = self.root + method + '?' + parameters

        # Do request
        response = requests.get(url, verify=False)

        # XML to JSON
        json_data = xmltodict.parse(response.text)

        # Save data to lists (in one dict, key = column name)
        time = []
        data = defaultdict(list)

        for entry in json_data['SolarForecastingChartDataForZone']['SolarForecastingChartDataForZoneItems']['SolarForecastingChartDataForZoneItem']:
            # Get time as datetime
            time_data = entry['StartsOn']['a:DateTime']
            format = '%Y-%m-%dT%H:%M:%SZ'
            time_datetime = datetime.datetime.strptime(time_data, format)

            # Convert timezone
            time_datetime_utc = pytz.utc.localize(time_datetime) # make datetime timezone aware
            local_tz = pytz.timezone(tz) # target timezone
            time_datetime_bru = time_datetime_utc.astimezone(local_tz) # convert to timezone

            data['time'].append(time_datetime_bru)
            data['MostRecentForecast'].append(float(entry['MostRecentForecast']))
            #data['RealTime'].append(float(entry['RealTime']))
            data['MonitoredCapacity'].append(float(entry['MonitoredCapacity']))

        # Print info
        if self.info:
            df = pd.DataFrame(data)
            df.set_index('time', inplace=True)
            print('\n' + BLUE + 'Elia Data')
            print(df.to_string())

        # Progress print
        if self.verbose:
            print(GREEN + 'Done')

        # Return results
        return data


if __name__ == '__main__':
    ec = EliaConnector(verbose=False, info=True)
    ec.get_chart_data('2021-08-03', '2021-08-04', region=5, tz='Europe/Brussels')

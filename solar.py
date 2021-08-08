#! python3

import datetime

import astral
import pytz

from color import GREEN, BLUE


class SolarTimes:
    '''
    Get solar times
    '''
    def __init__(self, verbose=True, info=False, debug=False):
        # Verbosity
        self.verbose = verbose
        self.info = info
        self.debug = debug


    def get_times(self, tz, lat, lon, date):
        '''
        Get solar times

        Arguments
        ---------
        tz      (string)    : timezone (in tz format)
        lat     (float)     : latitude
        lon     (float)     : longitude
        date    (date)

        Returns
        -------
        sun_times (dict)
        '''
        # Progress print
        if self.verbose:
            print('Getting solar times... ', end='')

        loc = astral.LocationInfo('Brussels', 'Belgium', tz, lat, lon)

        from astral.sun import sun
        local_tz = pytz.timezone(tz)
        sun_times = sun(loc.observer, date=date, tzinfo=local_tz)

        # Print info
        if self.info:
            print('\n' + BLUE + 'Solar Info')
            print('Dawn:    %s' % sun_times['dawn'].strftime("%Hu%M"))
            print('Sunrise: %s' % sun_times['sunrise'].strftime("%Hu%M"))
            print('Noon:    %s' % sun_times['noon'].strftime("%Hu%M"))
            print('Sunset:  %s' % sun_times['sunset'].strftime("%Hu%M"))
            print('Dusk:    %s' % sun_times['dusk'].strftime("%Hu%M"))

        # Progress print
        if self.verbose:
            print(GREEN + 'Done')

        # Return results
        return sun_times


if __name__ == '__main__':
    st = SolarTimes(verbose=False, info=True)
    today = datetime.date.today()
    st.get_times(tz='Europe/Brussels', lat=51.197567558420694, lon=4.716483482278131, date=today)

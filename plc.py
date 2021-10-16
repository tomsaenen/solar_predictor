#! python3

import json

from snap7.client import Client
import snap7.util

from color import BLUE, RED, GREEN, YELLOW, YELLOW_BRIGHT


class PLCConnector:
    '''
    Connect and communicate with PLC
    '''
    def __init__(self, verbose=True, info=False, debug=False):
        # Verbosity
        self.verbose = verbose
        self.info = info
        self.debug = debug

        # Import credentials
        with open('credentials.json', 'r') as file:
            self.credentials = json.load(file)

        # PLC IP address from credentials
        ip = self.credentials['plc']['ip']['local']

        # Create client
        print('Connecting to PLC... ', end='')
        self.client = Client()
        self.client.connect(ip, 0, 2, 102)
        if self.client.get_connected():
            print(GREEN + 'Connected')


    def list_blocks(self):
        # List blocks
        print('List blocks... ')
        blockslist = self.client.list_blocks() # returns snap7.types.BlocksList
        print(blockslist)
        print(GREEN + 'Done')


    def read_db(self):
        print('Read from DB99... ')
        data = self.client.db_read(99, 5, 1)
        float = snap7.util.get_byte(data,0)
        print(float)
        print(GREEN + 'Done')


    def write_int_to_db(self, db, offset, value):
        '''
        Arguments
        ---------
        db      (int)   :  db number
        offset  (int)   :  byte offset (within db)
        value   (int)   :  value to write
        '''
        # Progress print
        if self.verbose:
            print('Write to DB%i... ' % db)

        # Prepare data
        data = bytearray(2)
        snap7.util.set_int(data, 0, value)

        # Write data to PLC
        try:
            self.client.db_write(db, offset, data)
        except snap7.exceptions.Snap7Exception as ex:
            #print(ex)
            raise Exception(RED + 'Write to PLC Failed')

        # Progress print
        if self.verbose:
            print(GREEN + 'Done')


    def write_db_layout(self):
        # DB layout test
        from plc_db_layouts import db99_layout
        db_number = 99
        db_data = self.client.db_get(db_number)
        db99 = snap7.util.DB(
            db_number,              # the db we use
            db_data,                # bytearray from the plc
            db99_layout,            # layout specification
            446,                    # size of the specification (last index + size of last var)
            1,                      # number of row's / specifications (how often the specification is repeated)
            layout_offset=0,        # sometimes specification does not start a 0
            db_offset=0             # At which point in db_data should we start parsing for data
        )
        print(db99)

            # id_field='RC_IF_NAME',  # field we can use to make row
        print(db99[0]['Optimizers'])
        db99[0]['Optimizers'] = 7

        print(db99.specification) # string
        print(db99[0]._specification) # resulting dict

        # Bytearray: db99._bytearray

        db99[0].write(self.client) # ! NEEDS TO BE DB-ROW, so must index object


    def write_data_db(db_number, db_data, start=0):
        area = snap7.types.S7AreaDB
        #self.client.write_area(area, db_number, 0, size, db_data)
        self.client.write_area(snap7.types.Areas.DB, db_number, start, db_data)


if __name__ == '__main__':
    plc = PLCConnector()
    plc.list_blocks()
    #plc.read_db()
    #plc.write_db()
    #plc.write_db_layout()
    #plc.write_data_db(db_number, db99._bytearray)
    #plc.write_data_db()

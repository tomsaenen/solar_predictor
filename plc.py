#! python3

from snap7.client import Client
import snap7.util

from color import BLUE, RED, GREEN, YELLOW, YELLOW_BRIGHT

# Create client
print('Connecting to PLC... ', end='')
client = Client()
#client.connect('192.168.0.31', 0, 2, 102) # intern
client.connect('94.226.54.149', 0, 2, 102) # extern (forwarded via router)
if client.get_connected():
    print(GREEN + 'Connected')

# List blocks
# print('List blocks... ')
# blockslist = client.list_blocks() # returns snap7.types.BlocksList
# print(blockslist)
# print(GREEN + 'Done')

# DB99
# print('Read from DB99... ')
# data = client.db_read(99, 5, 1)
# float = snap7.util.get_byte(data,0)
# print(float)
# print(GREEN + 'Done')

# Write test
# print('Write to DB99... ')
# data = bytearray(1)
# snap7.util.set_byte(data, 0, 255)
# client.db_write(99, 4, data)
# print(GREEN + 'Done')

# DB layout test
from plc_db_layouts import db99_layout
db_number = 99
db_data = client.db_get(db_number)
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

db99[0].write(client) # ! NEEDS TO BE DB-ROW

# def write_data_db(db_number, db_data, start=0):
#     area = snap7.types.S7AreaDB
#     #client.write_area(area, db_number, 0, size, db_data)
#     client.write_area(snap7.types.Areas.DB, db_number, start, db_data)
#
# write_data_db(db_number, db99._bytearray)

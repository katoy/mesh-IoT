# See
#  https://developer.meshprj.com/hc/ja/articles/9164308204313-Python

import asyncio
from bleak import BleakClient, discover
from bleak import BleakScanner
from struct import pack
import requests
import json
from urllib.request import urlopen

# UUID
CORE_INDICATE_UUID = ('72c90005-57a9-4d40-b746-534e22ec9f9e')
CORE_NOTIFY_UUID = ('72c90003-57a9-4d40-b746-534e22ec9f9e')
CORE_WRITE_UUID = ('72c90004-57a9-4d40-b746-534e22ec9f9e')

# Constant values
MESSAGE_TYPE_INDEX = 0
EVENT_TYPE_INDEX = 1
STATE_INDEX = 2
MESSAGE_TYPE_ID = 1
EVENT_TYPE_ID = 0

def call_node_red(event):
    action = str(event)
    if event == 1:
        action = 'Single Pressed.'
    elif event == 2:
        action = 'Long Pressed.'
    elif event == 3:
        action = 'Double Pressed.'
    print(action)

    url = 'http://localhost:1880/mesh/button?event=' + str(event)
    with urlopen(url) as res:
        print(json.load(res))

# Callback
def on_receive_notify(sender, data: bytearray):
    action = ''
    if data[MESSAGE_TYPE_INDEX] != MESSAGE_TYPE_ID and data[EVENT_TYPE_INDEX] != EVENT_TYPE_ID:
        return
    call_node_red(data[2] )

def on_receive_indicate(sender, data: bytearray):
    data = bytes(data)
    print('[indicate] ', end='')
    for x in data:
        # print(x, end='')
        print("{0:02x}".format(x), end='')
    print()

async def scan(prefix='MESH-100'):
    while True:
        call_node_red('scan...')
        try:
            return next(d for d in await BleakScanner.discover() if d.name and d.name.startswith(prefix))
        except StopIteration:
            continue

async def main():
    # Scan device
    device = await scan('MESH-100BU')
    print('found ', device.name, device.address)

    # Connect device
    async with BleakClient(device, timeout=None) as client:
        # Initialize
        await client.start_notify(CORE_NOTIFY_UUID, on_receive_notify)
        await client.start_notify(CORE_INDICATE_UUID, on_receive_indicate)
        await client.write_gatt_char(CORE_WRITE_UUID, pack('<BBBB', 0, 2, 1, 3), response=True)
        call_node_red('connected')

        await asyncio.sleep(30)

        # Finish
        call_node_red('finish')

# Initialize event loop
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

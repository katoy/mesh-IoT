import asyncio
from bleak import BleakClient, discover  # pip3 install bleak
from struct import pack
import requests
import urllib
from urllib.request import urlopen
import json
import os
import platform

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

# Callback
def on_receive_notify(sender, data: bytearray):
    if data[MESSAGE_TYPE_INDEX] != MESSAGE_TYPE_ID and data[EVENT_TYPE_INDEX] != EVENT_TYPE_ID:
        return
    if data[2] == 1:
        print('Single Pressed.')
        my_task_one()
    elif data[2] == 2:
        print('Long Pressed.')
    elif data[2] == 3:
        print('Double Pressed.')

def on_receive_indicate(sender, data: bytearray):
    data = bytes(data)
    print('[indicate] ',data)

async def scan(prefix='MESH-100'):
    while True:
        print('scan...')
        try:
            return next(d for d in await discover() if d.name and d.name.startswith(prefix))
        except StopIteration:
            continue

def to_location(name):
    url = 'https://api.sssapi.app/ouZltg7fT2t9kbyodTQZ3/'

    headers = {
        "User-Agent": "camouflage useragent",
    }

    request = urllib.request.Request(url=url, headers=headers)
    with urllib.request.urlopen(request) as response:
        text = response.read().decode('utf-8')
        data = json.loads(text)

    for x in data:
        if x["pref_name"] == name:
            return  [x["pref_name"], x["lat"], x["lon"]]
    return ["*東京", 35.689185, 139.691648] # 東京の緯度経度

def weather(lat, lon):
    apikey = "" # EDIT

    if len(apikey) == 0:
        print("#----- OpenWeather の APIKEy が未設定です")
        return {"name": "xxx", "description": "yyy" }

    response = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={
            "appid": apikey,
            "units": "metric",
            "lang": "ja",
            # 緯度経度
            "lat": lat,
            "lon": lon,
        },
    )
    ret = json.loads(response.text)
    return {"name": ret["name"], "description": ret["weather"][0]["description"]}

def ifttt_webhook(name, desc):
    payload = {"value1": name, "value2": "", "value3": desc }
    url = "" # EDIT
    if len(url) == 0:
        print("#----- IFTTT の webhook が未設定です")
    else:
        response = requests.post(url, data=payload)

def notify(name, desc):
    if platform.system() == 'Darwin':
        os.system("osascript -e 'display notification \"{}\" with title \"{}\"'".format(desc, name))
    ifttt_webhook(name, desc)

def sub_task(name):
  locations = to_location(name)
  # print(locations)
  ret = weather(locations[1], locations[2])
  # print(ret["name"], ret["description"])
  notify(ret["name"], ret["description"])

# ---------------------------
def my_task_one():
    sub_task("東京都")
    sub_task("北海道")

async def main():
    # Scan device
    device = await scan('MESH-100BU')
    print('found', device.name, device.address)

    # Connect device
    async with BleakClient(device, timeout=None) as client:
        # Initialize
        await client.start_notify(CORE_NOTIFY_UUID, on_receive_notify)
        await client.start_notify(CORE_INDICATE_UUID, on_receive_indicate)
        await client.write_gatt_char(CORE_WRITE_UUID, pack('<BBBB', 0, 2, 1, 3), response=True)
        print('connected')

        await asyncio.sleep(30)

        # Finish

# Initialize event loop
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # my_task_one("東京都")
    # my_task_one("北海道")
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
        my_task_two()
    elif data[2] == 3:
        print('Double Pressed.')
        my_task_three()

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


# 都道府県名から移動軽度をえる
def to_location(name):
    # Sheet: https://docs.google.com/spreadsheets/d/1Q4hJxEfK5HsH-JNW9zqgOwTiQk1uR-2XK9O-rbJFI8I/edit#gid=0
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

# 国名から移動軽度を得る
def to_location_world(name):
    # Shhet: https://docs.google.com/spreadsheets/d/1M5m1UKmcdIThzmZqf4uRTC4ug08YQhAHKjAlfruO_Eo/edit#gid=0
    url = 'https://script.google.com/macros/s/AKfycbyzU8apFTI42dSReu2M0vifV1_oID-ojQSTnVE5NgLpM1Xdc13T1jwCVCEXg6c1RTP2/exec'

    response = requests.get(url + "?name=" + name)
    ret = json.loads(response.text)
    # print(ret)
    return  [ret["items"]["name"], ret["items"]["lat"], ret["items"]["lon"]]

# 郵便番号から移動軽度を得る
def to_location_zip(zipcode):
    # Shhet: https://docs.google.com/spreadsheets/d/1pJSVx8RtbqmTSkl2D8fCcBJKJCwwvY5wZg2wt-w53i4/edit#gid=1219701044

    url = 'https://script.google.com/macros/s/AKfycbxUXULvG2ExdCo5OhO7sh1vCEOo7F_3z3HHz53zoNFQWJVxXHZZFtcgoJ-j5vODIVGL/exec'

    response = requests.get(url + "?zipcode=" + zipcode)
    ret = json.loads(response.text)
    # print(ret)
    return  [ret["items"]["full_name"], ret["items"]["緯度"], ret["items"]["経度"]]

# 緯度経度から天気を得る
def weather(lat, lon):
    apikey = "" # EDIT

    if len(apikey) == 0:
        print("#----- OpenWeather の APIKEY が未設定です")
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
    print(ret)
    return {"name": ret["name"], "description": ret["weather"][0]["description"]}

# IFTTT を呼び出す
def ifttt_webhook(name, desc):
    payload = {"value1": name, "value2": "", "value3": desc }
    url = "" # EDIT
    if len(url) == 0:
        print("#----- IFTTT の webhook が未設定です")
    else:
        response = requests.post(url, data=payload)

# コンソールに通知を出す(for Mac)
def notify(name, desc):
    if platform.system() == 'Darwin':
        os.system("osascript -e 'display notification \"{}\" with title \"{}\"'".format(desc, name))
    ifttt_webhook(name, desc)

# 都道府県名から天気を得る
def sub_task(name):
    locations = to_location(name)
    # print(locations)
    ret = weather(locations[1], locations[2])
    # print(ret["name"], ret["description"])
    notify(ret["name"], ret["description"])

# 　国名から天気を得る
def sub_task_world(name):
    locations = to_location_world(name)
    # print(locations)
    ret = weather(locations[1], locations[2])
    # print(ret["name"], ret["description"])
    notify(ret["name"], ret["description"])

# 郵便番号から天気を得る
def sub_task_zip(zipcode):
    locations = to_location_zip(zipcode)
    # print(locations)
    ret = weather(locations[1], locations[2])
    # print(ret["name"], ret["description"])
    notify(ret["name"], ret["description"])

# ---------------------------
def my_task_one():
    sub_task("東京都")
    sub_task("北海道")

def my_task_two():
    sub_task_world('日本')
    sub_task_world('イギリス')

def my_task_three():
    sub_task_zip('100-0001')
    sub_task_zip('9070024')

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

    #
    # print(to_location("東京都"))
    # print(to_location("北海道"))
    # sub_task('北海道')
    # my_task()

    # print(to_location_world('アメリカ合衆国'))
    # sub_task_world('アメリカ合衆国')
    # my_task_two()

    # print(to_location_zip('100-0001'))
    # print(to_location_zip('640941'))
    # sub_task_zip('100-0001')
    # sub_task_zip('640941')
    # sub_task_zip('9070024')
    # my_task_three()

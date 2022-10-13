# MESH GPIO の status LED を光らせる。
# red, green, blue の on / off を指定する。

import asyncio
from bleak import BleakClient, discover
from struct import pack

CORE_INDICATE_UUID = ('72c90005-57a9-4d40-b746-534e22ec9f9e')
CORE_NOTIFY_UUID = ('72c90003-57a9-4d40-b746-534e22ec9f9e')
CORE_WRITE_UUID = ('72c90004-57a9-4d40-b746-534e22ec9f9e')

EV_KIND_GP = {
    0: '?',
    1: 'アナログ入力のイベント通知',
    2: 'デジタル入力の状態通知　　',
    3: 'アナログ入力の状態通知　　',
    4: '電源出力の状態通知　　　　',
    5: 'デジタル出力の状態通知　　',
    6: 'PWM 出力の状態通知　　　　'
}

# Callback
def on_receive_notify(sender, data: bytearray):
    b_ary = bytes(data)
    print('[notify] ', EV_KIND_GP.get(b_ary[1]), end='')
    for x in b_ary:
        print("{0:02x}".format(x), end=' ')
    print()

def on_receive_indicate(sender, data: bytearray):
    print('[indicate] ', end='')
    for x in bytes(data):
        print("{0:02x}".format(x), end=' ')
    print()

def print_command(data: bytearray):
    print('[command] ', end='')
    for x in bytes(data):
        print("{0:02x}".format(x), end=' ')
    print()

def calc_checksum(data: bytearray):
    checksum = 0
    for x in data:
        checksum += x
    return checksum & 0xFF

# MESH ブロックのステータス LED を操作するコマンド
# See https://developer.meshprj.com/hc/ja/articles/8286379681945#h_01GBQTH1222DGNRKQ1QCTHST11
def make_command():
    message_type = 0 # ブロック共通機能
    event_type = 0 # ステータスバーの点灯
    red = 1
    green = 1
    blue = 1
    on = 1

    command = pack('<BBBBBB', message_type, 0, red, green, blue, on)
    command = command + pack('B', calc_checksum(command)) # Add check sum to byte array
    return command

async def scan(prefix = 'MESH-100'):
    while True:
        print('scan...')
        try:
            return next(d for d in await discover() if d.name and d.name.startswith(prefix))
        except StopIteration:
            continue

async def main():
    # Scan device
    device = await scan('MESH-100GP')
    print('found', device.name, device.address)

    # Connect device
    async with BleakClient(device, timeout=None) as client:
        # Initialize
        await client.start_notify(CORE_NOTIFY_UUID, on_receive_notify)
        await client.start_notify(CORE_INDICATE_UUID, on_receive_indicate)
        await client.write_gatt_char(CORE_WRITE_UUID, pack('<BBBB', 0, 2, 1, 3), response=True)
        print('connected')

        # Generate command
        command = make_command()
        print_command(command)

        try:
            # Write command
            await client.write_gatt_char(CORE_WRITE_UUID, command, response=True)
        except Exception as e:
            print('error', e)
            return

        await asyncio.sleep(10)

        # Finish

# Initialize event loop
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

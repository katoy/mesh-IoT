import asyncio
from bleak import BleakScanner
from struct import pack

CORE_INDICATE_UUID = ('72c90005-57a9-4d40-b746-534e22ec9f9e')
CORE_NOTIFY_UUID = ('72c90003-57a9-4d40-b746-534e22ec9f9e')
CORE_WRITE_UUID = ('72c90004-57a9-4d40-b746-534e22ec9f9e')

EV_KIND_LE = {
    0: '? ',
    1: '? ',
    2: '? ',
    3: '? ',
    4: '? ',
    5: '? ',
    6: '? '
}
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
def on_receive_notify(sender, data: bytearray, ev_kinds = {}):
    b_ary = bytes(data)
    print('[notify] ', ev_kinds.get(b_ary[1]), end='')
    for x in b_ary:
        print("{0:02x}".format(x), end=' ')
    print()

def on_receive_notify_le(sender, data: bytearray):
    on_receive_notify(sender, data, EV_KIND_LE)

def on_receive_notify_gp(sender, data: bytearray):
    on_receive_notify(sender, data, EV_KIND_GP)

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

async def scan(prefix = 'MESH-100'):
    while True:
        print('scan...')
        try:
            return next(d for d in await BleakScanner.discover() if d.name and d.name.startswith(prefix))
        except StopIteration:
            continue

if __name__ == '__main__':
    print("これは自作モジュールです")

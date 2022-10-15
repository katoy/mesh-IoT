# 信号機のように赤, 黄、緑の順番に点滅させる。

import asyncio
from struct import pack
from bleak import BleakClient
import my_mesh

def make_command(red, green, blue, time_on, time_off):
        message_type = 1
        event_type = 0
        duration = 4 * 1000 # [ms]
        pattern = 1 # 1:blink, 2:firefly
        command = pack(
                    '<BBBBBBBHHHB',
                    message_type, event_type, red, 0, green, 0, blue, duration, time_on, time_off, pattern
                )
        command = command + pack('B', my_mesh.calc_checksum(command)) # Add check sum to byte array
        return command

def commands_for_task():
    return [
        make_command(0, 10, 0, 4000, 0), # green
        make_command(0, 10, 0, 800, 200), # green 点滅
        make_command(10, 10, 0, 4000, 0), # yellow
        make_command(10, 0, 0, 4000, 0) # red
    ]

async def main():
    # Scan device
    device = await my_mesh.scan('MESH-100LE')
    print('found', device.name, device.address)

    # Connect device
    async with BleakClient(device, timeout=None) as client:
        # Initialize
        await client.start_notify(my_mesh.CORE_NOTIFY_UUID, my_mesh.on_receive_notify_le)
        await client.start_notify(my_mesh.CORE_INDICATE_UUID, my_mesh.on_receive_indicate)
        await client.write_gatt_char(my_mesh.CORE_WRITE_UUID, pack('<BBBB', 0, 2, 1, 3), response=True)
        print('connected')
        try:
            commands = commands_for_task()
            for i in range(2):
                for k in range(len(commands)):
                    # コマンドをMESH ブロックへ送る
                    my_mesh.print_command(commands[k])
                    await client.write_gatt_char(my_mesh.CORE_WRITE_UUID, commands[k], response=True)
                    await asyncio.sleep(4)
        except Exception as e:
            print('error', e)
        # Finish
        print('finish')

# Initialize event loop
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    finally:
        asyncio.set_event_loop(None)
        loop.close()

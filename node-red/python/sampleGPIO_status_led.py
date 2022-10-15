# MESH GPIO の status LED を光らせる。
# red, green, blue の on / off を指定する。

import asyncio
from bleak import BleakClient
from struct import pack
import my_mesh

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
    command = command + pack('B', my_mesh.calc_checksum(command)) # Add check sum to byte array
    return command

async def main():
    # Scan device
    device = await my_mesh.scan('MESH-100GP')
    print('found', device.name, device.address)

    # Connect device
    async with BleakClient(device, timeout=None) as client:
        # Initialize
        await client.start_notify(my_mesh.CORE_NOTIFY_UUID, my_mesh.on_receive_notify_gp)
        await client.start_notify(my_mesh.CORE_INDICATE_UUID, my_mesh.on_receive_indicate)
        await client.write_gatt_char(my_mesh.CORE_WRITE_UUID, pack('<BBBB', 0, 2, 1, 3), response=True)
        print('connected')

        # Generate command
        command = make_command()
        my_mesh.print_command(command)

        try:
            # Write command
            await client.write_gatt_char(my_mesh.CORE_WRITE_UUID, command, response=True)
        except Exception as e:
            print('error', e)
            return

        await asyncio.sleep(10)

        # Finish

# Initialize event loop
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    finally:
        asyncio.set_event_loop(None)
        loop.close()

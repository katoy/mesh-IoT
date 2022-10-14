import asyncio
from struct import pack
from bleak import BleakClient
import my_mesh

def make_command(red, green, blue):
        message_type = 1
        event_type = 0
        duration = 5 * 1000 # 5,000[ms]
        on = 1 * 1000 # 1,000[ms]
        off = 500 # 500[ms]
        pattern = 1 # 1:blink, 2:firefly
        command = pack('<BBBBBBBHHHB', message_type, event_type, red, 0, green, 0, blue, duration, on, off, pattern)
        command = command + pack('B', my_mesh.calc_checksum(command)) # Add check sum to byte array
        return command

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

        # Generate command
        # command = make_command(2, 0, 0)
        command = make_command(0, 2, 0)
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
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

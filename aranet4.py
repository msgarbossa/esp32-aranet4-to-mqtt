
import sys
import uasyncio as asyncio
import aioble
import bluetooth
from config import config
import gc

sys.path.append("")


def le16(data, start=0):
    """
    Read value from byte array as a long integer

    :param bytearray data:  Array of bytes to read from
    :param int start:  Offset to start reading at
    :return int:  An integer, read from the first two bytes at the offset.
    """
    raw = bytearray(data)
    return raw[start] + (raw[start + 1] << 8)

def write_le16(data, pos, value):
    """
    Write a value as a long integer to a byte array

    :param bytearray data:  Array of bytes to write to
    :param int pos:  Position to store value at as a two-byte long integer
    :param int value:  Value to store
    :return bytearray:  Updated bytearray
    """
    data[pos] = (value) & 0x00FF
    data[pos + 1] = (value >> 8) & 0x00FF

    return data

type_gen = type((lambda: (yield))())  # Generator type


# If a callback is passed, run it and return.
# If a coro is passed initiate it and return.
# coros are passed by name i.e. not using function call syntax.
def launch(func: function, tup_args: tuple):
    res = func(*tup_args)
    if isinstance(res, type_gen):
        loop = asyncio.get_event_loop()
        loop.create_task(res)

class Aranet4:

    # AR4_SERVICE = "0000fce0-0000-1000-8000-00805f9b34fb" # v1.2.0 and later
    AR4_SERVICE = bluetooth.UUID(0xfce0) # v1.2.0 and later (this is the advertised service)
    AR4_READ_CURRENT_READINGS = bluetooth.UUID("f0cd1503-95da-4f4b-9ac8-aa55d312af0c")  # this is the main characteristic
    UNKNOWN1 = bluetooth.UUID("f0cd1401-95da-4f4b-9ac8-aa55d312af0c")
    GENERIC_SERVICE = bluetooth.UUID(0x1800)
    COMMON_SERVICE = bluetooth.UUID(0x180a)
    # AR4_READ_CURRENT_READINGS = bluetooth.UUID(0x1503)
    GENERIC_READ_DEVICE_NAME = bluetooth.UUID("00002a00-0000-1000-8000-00805f9b34fb")
    AR4_READ_HISTORY_READINGS_V2 = bluetooth.UUID("f0cd2005-95da-4f4b-9ac8-aa55d312af0c")
    AR4_READ_HISTORY_READINGS_V1 = bluetooth.UUID("f0cd2003-95da-4f4b-9ac8-aa55d312af0c")

    UUID_SERIAL_NUMBER = bluetooth.UUID("00002a25-0000-1000-8000-00805f9b34fb")
    UUID_BATTERY_LEVEL = bluetooth.UUID("00002a19-0000-1000-8000-00805f9b34fb")
    UUID_MANUFACTURER_NAME = bluetooth.UUID("00002a29-0000-1000-8000-00805f9b34fb")
    UUID_MODEL_NAME = bluetooth.UUID("00002a24-0000-1000-8000-00805f9b34fb")
    UUID_DEVICE_NAME = bluetooth.UUID("00002a00-0000-1000-8000-00805f9b34fb")
    UUID_SERIAL_NUMBER = bluetooth.UUID("00002a25-0000-1000-8000-00805f9b34fb")
    UUID_HARDWARE_REVISION = bluetooth.UUID("00002a27-0000-1000-8000-00805f9b34fb")
    UUID_SOFTWARE_REVISION = bluetooth.UUID("00002a28-0000-1000-8000-00805f9b34fb")
    UUID_UPDATE_INTERVAL = bluetooth.UUID("f0cd2002-95da-4f4b-9ac8-aa55d312af0c")
    UUID_SINCE_LAST_UPDATE = bluetooth.UUID("f0cd2004-95da-4f4b-9ac8-aa55d312af0c")
    UUID_STORED_READINGS = bluetooth.UUID("f0cd2001-95da-4f4b-9ac8-aa55d312af0c")
    UUID_CURRENT_READING_SIMPLE = bluetooth.UUID("f0cd1503-95da-4f4b-9ac8-aa55d312af0c")
    UUID_CURRENT_READING_FULL = bluetooth.UUID("f0cd3001-95da-4f4b-9ac8-aa55d312af0c")
    UUID_HISTORY_RANGE = bluetooth.UUID("f0cd1402-95da-4f4b-9ac8-aa55d312af0c")
    UUID_HISTORY_NOTIFIER = bluetooth.UUID("f0cd2003-95da-4f4b-9ac8-aa55d312af0c")

    # Available sensor identifiers
    SENSOR_CO2 = 0
    SENSOR_TEMPERATURE = 2
    SENSOR_PRESSURE = 4
    SENSOR_HUMIDITY = 6

    def __init__(self, ble_names_to_find: list, metrics_callback: function,
                 temp_format: str = "C", default_reconnect_sec = 300, *args, **kwargs):

        self.ble_names_to_find = ble_names_to_find
        self._metrics_callback = metrics_callback  # metrics function
        self._temp_format = temp_format
        self._default_reconnect_sec = default_reconnect_sec

        self.metrics = {
            "temp": -1,
            "humidity": -1,
            "pressure": -1,
            "co2": -1,
            "battery": -1
        }

        # loop = asyncio.get_event_loop()
        # loop.create_task(self.get_sensors())  # Thread runs forever

    async def get_sensors(self):
        # ble_config = ble.config()
        # print(ble_config.mac)
        self.found_devices = await find_nearby(self.ble_names_to_find)
        device = self.found_devices[0]
        # device = await bleScanner.ble_scan()
        if not device:
            print("BLE sensor not found")
            return
        print("device:", type(device))


        while True:
            try:
                print("Connecting to", device)
                connection = await device.connect(timeout_ms=2000)
            except asyncio.TimeoutError:
                print("Timeout during connection")
                return

            print("connection:", type(connection))

            if connection.is_connected():
                print("device is connected")

            # await connection.exchange_mtu()

            data = None  # initialize to test if data was received

            async with connection:
                try:
                    print("looking for service")
                    conn_svc = await connection.service(Aranet4.AR4_SERVICE)
                    if not conn_svc:
                        print("get service failed")
                        raise("Unable to get service")
                    print("get service complete")
                    print("conn_svc:", type(conn_svc))

                    uuids = [
                        # AltAranet4.UUID_SERIAL_NUMBER,
                        # AltAranet4.UUID_BATTERY_LEVEL,
                        # AltAranet4.UUID_MANUFACTURER_NAME,
                        # AltAranet4.UUID_MODEL_NAME,
                        # AltAranet4.UUID_DEVICE_NAME,
                        # AltAranet4.UUID_SERIAL_NUMBER,
                        # AltAranet4.UUID_HARDWARE_REVISION,
                        # AltAranet4.UUID_SOFTWARE_REVISION,

                        # AltAranet4.UUID_UPDATE_INTERVAL,
                        # AltAranet4.UUID_SINCE_LAST_UPDATE,
                        # AltAranet4.UUID_STORED_READINGS,
                        # AltAranet4.UUID_CURRENT_READING_SIMPLE,
                        Aranet4.UUID_CURRENT_READING_FULL,
                        # AltAranet4.UUID_HISTORY_RANGE,
                        # AltAranet4.UUID_HISTORY_NOTIFIER,
                    ]

                    for char in uuids:
                        print("trying characteristic:", char)
                        svc_char = await conn_svc.characteristic(char)
                        # await conn_svc.subscribe(notify=True)
                        if svc_char:
                            print("found characteristic")
                            try:
                                data = await svc_char.read(timeout_ms=10000)
                                # print(data)
                            except Exception as e:
                                # print("Exception:", e)
                                raise(e)

                    print("finished characteristic")

                    data = await svc_char.read(timeout_ms=10000)
                    print(data)

                except asyncio.TimeoutError:
                    print("Timeout discovering services/characteristics")

                except Exception as e:
                    print("Error collecting sensor data:", e)

                if not data:
                    print("no data received, waiting default reconnect seconds ({0}) to retry.".format(self._default_reconnect_sec))
                    await asyncio.sleep_ms(self._default_reconnect_sec * 1000)
                    continue

                temp_raw = le16(data, Aranet4.SENSOR_TEMPERATURE)
                if self._temp_format == "C":
                    temp = temp_raw / 20
                else:
                    temp = (temp_raw / 20) * (9/5) + 32
                humidity = data[Aranet4.SENSOR_HUMIDITY]
                pressure = le16(data, Aranet4.SENSOR_PRESSURE) / 10
                co2 = le16(data, Aranet4.SENSOR_CO2)
                battery = data[7]
                update_interval = le16(data, 9)
                since_last_update = le16(data, 11)
                
                self.metrics = {
                    "temp": temp,
                    "humidity": humidity,
                    "pressure": pressure,
                    "co2": co2,
                    "battery": battery
                }

                try:
                    print("Disconnecting from", device)
                    connection = await connection.disconnect()
                except Exception as e:
                    print("Error disconnecting: ", e)
                    continue
                next_update_ms = (update_interval - since_last_update + 2) * 1000
                cb_args = (temp, humidity, pressure, co2, battery)
                launch(self._metrics_callback, cb_args)
                print("next update in {0} seconds".format(next_update_ms/1000))
                await asyncio.sleep_ms(next_update_ms)

                # byte_len = len(data)
                # print("byte_len:", byte_len)

                # idx = 0
                # while idx < byte_len - 1:
                #     print(idx, " raw:", data[idx])
                #     print(idx, " shift:", le16(data, idx))
                #     idx += 1


async def find_nearby(ble_device_find_names: list):
    # Scan for 5 seconds, in active mode, with very low interval/window (to
    # maximise detection rate).
    print("Native byteorder: ", sys.byteorder)
    aioble.core.log_level = 2
    ble_device_names_find_len = len(ble_device_find_names)
    print("Looking for {0} device(s)".format(ble_device_names_find_len))
    ble_devices_found = []
    async with aioble.scan(20000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() in ble_device_find_names:
                if Aranet4.AR4_SERVICE not in result.services():
                    print("Found device, but not the service (still scanning)")
                    continue
                print("Found:", result.device)
                ble_devices_found.append(result.device)

                found_count = len(ble_devices_found)
                if (found_count == ble_device_names_find_len):
                    print("found all devices")
                    gc.collect()
                    return ble_devices_found
                else:
                    print("found {0} devices out of {1}, still scanning BLE".format(found_count, ble_device_names_find_len))

    print("BLE scan timeout reached. Found {0} devices out of {1}".format(found_count, ble_device_names_find_len))
    gc.collect()
    return ble_devices_found


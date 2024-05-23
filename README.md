# esp32-aranet4-to-mqtt

BLE gateway for Aranet4 CO2 sensor to collect current statistics and push to MQTT.

## Examples

### MQTT message format

```json
{
  "pressure": 968.3,
  "fs": 1.8125,
  "battery": 54,
  "co2": 1139,
  "humidity": 33,
  "temp": 79.43,
  "memory": "51.66",
  "signal": -55
}
```

### Grafana dashboard

![example-grafana-dashboard](/grafana-dashboard-for-aranet4.png)

## Configuration

Modify ./config/config.py:
- SSID
- NETWORK_KEY
- BROKER_ADDRESS
- BROKER_USER
- BROKER_PASSWORD
- ARANET4_BLE_NAMES

## Installation

An ESP32 microcontroller with BLE support is required to connect to the Aranet4.  Not all models support BLE such as DEVKIT or ESP32-S2.  ESP32-C3 or ESP32-S3 support BLE.  The example script below sets up an ESP32-C3 using the /dev/ttyUSB0 serial device.

```bash
tty="/dev/ttyUSB0"
esptool.py --chip esp32c3 --port $tty erase_flash && sleep 10 && \
esptool.py --chip esp32c3 --port $tty --baud 460800 write_flash -z 0x0 ~/Downloads/ESP32_GENERIC_C3-20240222-v1.22.2.bin && sleep 10 && \
mpremote connect $ttymip install umqtt.simple && \
mpremote connect $tty mip install aioble && \
mpremote connect $tty mip install types && \
ampy --port $tty --baud 115200 put util && \
ampy --port $tty --baud 115200 put config && \
ampy --port $tty--baud 115200 put main.py  && \
ampy --port $tty --baud 115200 put boot.py  && \
ampy --port $tty --baud 115200 put MQTT && \
ampy --port $tty--baud 115200 put aranet4.py && \
echo "done"
```

## License

MIT

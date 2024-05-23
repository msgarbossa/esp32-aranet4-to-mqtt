

from micropython import const
import sys
import uasyncio as asyncio
from config import config
from MQTT import mqttClient
from util import wifiManager, timeFormat
from machine import reset
import aranet4

from util import timeFormat
from config import config
import gc
import os

sys.path.append("")

# available RAM
def free(full=False):
  F = gc.mem_free()
  A = gc.mem_alloc()
  T = F+A
  P = '{0:.2f}'.format(F/T*100)
  if not full: return P
  else : return ('Total:{0} Free:{1} ({2})'.format(T,F,P))

def df():
  s = os.statvfs('//')
  mb = (s[0]*s[3])/1048576
  return mb
  # return ('{0} MB'.format(mb))

def restart_and_reconnect():
    print('Resetting.')
    reset()

def send_mqtt():
    if not config.MQTT_ENABLED:
        print("skipping send_mqtt because MQTT is not enabled in configuration.")
        return


def send_mqtt_aranet4(*args):
    print("sensor metrics: {0} at {1}".format(args, timeFormat.currentTime()))

    mqtt_data = {
        "temp": args[0],
        "humidity": args[1],
        "pressure": args[2],
        "co2": args[3],
        "battery": args[4]
    }

    # add in filesystem usage %
    mqtt_data["fs"] = df()

    # add in available memory
    mqtt_data["memory"] = free()

    if(config.MQTT_ENABLED):
        wifiManager.connect()
        mqtt_data["signal"] = wifiManager.get_signal()
        try:
            mqttClient.MQTTConnect()
            mqttClient.sendData(mqtt_data)
            mqttClient.MQTTDisconnect()
            wifiManager.disconnect()

        except OSError as err:
            print("OS error:", err)
            restart_and_reconnect()
        except ValueError as err:
            print("ValueError:", err)
            restart_and_reconnect()
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            restart_and_reconnect()
        except:
            print("Unhandled exception - exiting")
            restart_and_reconnect()

    gc.collect()

async def main():

    aranet4_obj = aranet4.Aranet4(config.ARANET4_BLE_NAMES, send_mqtt_aranet4, temp_format="F")

    t1 = asyncio.create_task(aranet4_obj.get_sensors())
    await asyncio.gather(t1)

    # Aranet class uses callback to send data to MQTT.  If multiple sensors need aggregated data,
    # use something like this or a separate coroutine.
    # while(True):
    #     await asyncio.sleep(config.BROKER_PUBLISH_SEC)
        # send_mqtt_status()


asyncio.run(main())

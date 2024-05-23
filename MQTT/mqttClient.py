from umqtt.simple import MQTTClient
from config import config
from util import wifiManager, timeFormat
import time
import ujson
import gc

clientName = config.CLIENT_NAME
brokerAddr = config.BROKER_ADDRESS
brokerUser = config.BROKER_USER
brokerPassword = config.BROKER_PASSWORD

mqttc = MQTTClient(clientName, brokerAddr, user=brokerUser, password=brokerPassword, port=1883, keepalive=60)

# Topic to test Connection
testTopic = b'home/%s/test' % (clientName)
# Topic to publish data
pubTopic = b'home/%s/metrics' % (clientName)

encode = True
buffer = None


def MQTTConnect():
    try:
        print("{0} MQTT > Connecting to broker...".format(timeFormat.currentTime()))
        # print("MQTT > Client: ", clientName)
        # print("MQTT > Broker Address:", brokerAddr)
        mqttc.connect()
        print('{0} MQTT > Connected to {1} MQTT broker'.format(timeFormat.currentTime(), brokerAddr))
        gc.collect()
    except OSError as e:
        print("MQTT connect failed. Retrying...")
        time.sleep(1)
        MQTTConnect()

def MQTTDisconnect():
    try:
        print("{0} MQTT > Disconnecting from the broker...".format(timeFormat.currentTime()))
        # print("MQTT > Client: ", clientName)
        # print("MQTT > Broker Address:", brokerAddr)
        mqttc.disconnect()
        print('{0} MQTT > Disconnected from {1} MQTT broker'.format(timeFormat.currentTime(), brokerAddr))
        gc.collect()
    except OSError as e:
        print("MQTT disconnect failed.")
        time.sleep(1)
        # MQTTDisconnect()

def sendData(data):
    global encode
    global buffer

    if encode:
        buffer = ujson.dumps(data)
        
    if(wifiManager.isConnected()): 
        print("{0} MQTT > Sending Data...".format(timeFormat.currentTime()))
        try:
            print("MQTT > {0}".format(buffer))
            mqttc.publish(pubTopic, buffer.encode())
            print("{0} MQTT > publish complete".format(timeFormat.currentTime()))
            encode = True
            gc.collect()
        except OSError as e:
            print("{0} MQTT > Publishing failed. Retrying...".format(timeFormat.currentTime()))
            time.sleep(3)
            MQTTConnect()
            encode = False
            sendData(buffer)
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
        except:
            print("Unhandled exception - exiting")

    else:
        print("MQTT > Lost Network Connection ...")
        wifiManager.connect()
        encode = False
        sendData(buffer)

    
# Sending Test Messages over the Test Topic   
def sendTestMsg():
    testMessage = "Hello from Client! Timestamp: " + str(time.time())
    print("MQTT > {0}".format(testMessage))
    mqttc.publish(testTopic, testMessage.encode())

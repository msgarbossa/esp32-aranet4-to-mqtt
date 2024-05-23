
#----APPLICATION FLAGS----#
# True = Connect to MQTT Broker on Startup (Should always be true)
MQTT_ENABLED=True

#----WIFI CONNECTION CONFIG----#
SSID = "<WIFI_SSID>"
NETWORK_KEY  = "<WIFI_PW>"

#----MQTT CLIENT CONFIG----#
BROKER_ADDRESS = "<BROKER_IP>"
BROKER_USER = "<MQTT_USER>"
BROKER_PASSWORD = "<MQTT_PW>"
CLIENT_NAME = "aranet4"

#----NTP CONFIG----#
NTP_SERVER="192.168.1.1"
NTP_HOUR_ADJUST=0 # GMT offset (accepts negative values)

#----SCANNER CONFIG----#

# Aranet BLE name should be in the form of "Aranet4 012EF" 
ARANET4_BLE_NAMES = [ "Aranet4 012EF" ]

BROKER_PUBLISH_SEC=300

# Temperature format = C or F
TEMP_FORMAT="F"


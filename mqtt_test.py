#!/usr/bin/env python
import time

import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

client = mqtt.Client()
client.on_connect = on_connect

client.connect("192.168.178.101", 1883, 60)

client.loop_start()

while True:
    time.sleep(2)
    client.publish("zigbee2mqtt/Lampe_Schreibtisch/set", "{   \"state\": \"ON\", \"transition\": \"2\" }")
    time.sleep(2)
    client.publish("zigbee2mqtt/Lampe_Schreibtisch/set", "{   \"state\": \"OFF\", \"transition\": \"2\" }")

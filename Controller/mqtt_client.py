import paho.mqtt.client as mqtt
import logging
import time
from config import *


class MQTTClient:
    def __init__(self, serial_handler):
        self.client = mqtt.Client(MQTT_CLIENT_ID)
        self.serial_handler = serial_handler
        self.connected = False
        self.setup_callbacks()

    def setup_callbacks(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe

        if MQTT_USERNAME and MQTT_PASSWORD:
            self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logging.info("Connected to MQTT Broker successfully")
        else:
            self.connected = False
            logging.error(f"Failed to connect to MQTT Broker, return code: {rc}")

    def on_subscribe(self, client, userdata, mid, granted_qos):
        logging.info(f"Subscribed to topics with QoS: {granted_qos}")

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode().strip().upper()
            topic = msg.topic

            logging.info(f"Received MQTT message: {payload} on topic: {topic}")

            # Handle HELLO command - turn on Y16
            if topic == "plc/commands/hello" and payload == "HELLO":
                logging.info("HELLO command received - turning on Y16")
                self.serial_handler.turn_on_y16()

            # Direct Y16 control
            elif topic == "plc/commands/y16":
                if payload == "ON":
                    self.serial_handler.turn_on_y16()
                elif payload == "OFF":
                    self.serial_handler.turn_off_y16()

            # Forward all other commands directly to PLC
            else:
                logging.info(f"Forwarding message to PLC: {payload}")
                self.serial_handler.send_to_plc(payload)

        except Exception as e:
            logging.error(f"Error processing MQTT message: {e}")

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        if rc != 0:
            logging.warning(f"Unexpected MQTT disconnection, code: {rc}")
        else:
            logging.info("Disconnected from MQTT Broker")

    def publish_status(self, message):
        try:
            if self.connected:
                result = self.client.publish(MQTT_TOPIC_PUBLISH, message, qos=1)
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    logging.info(f"Published to MQTT: {message}")
                else:
                    logging.error(f"Failed to publish to MQTT: {result.rc}")
            else:
                logging.warning("Cannot publish - MQTT not connected")
        except Exception as e:
            logging.error(f"Error publishing to MQTT: {e}")

    def connect(self):
        try:
            logging.info(f"Connecting to MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()

            # Wait a bit for connection to establish
            time.sleep(2)

        except Exception as e:
            logging.error(f"Failed to connect to MQTT broker: {e}")
            self.connected = False

    def disconnect(self):
        try:
            self.connected = False
            self.client.loop_stop()
            self.client.disconnect()
            logging.info("MQTT client disconnected")
        except Exception as e:
            logging.error(f"Error disconnecting MQTT client: {e}")

    def is_connected(self):
        return self.connected
import logging
import signal
import sys
import time
from Controller.mqtt_client import MQTTClient
from Controller.serial_plc import SerialPLC

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("plc_mqtt_bridge.log"),
        logging.StreamHandler(sys.stdout)
    ]
)


class PLC_MQTT_Bridge:
    def __init__(self):
        self.serial_plc = None
        self.mqtt_client = None
        self.running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, sig, frame):
        logging.info("Shutdown signal received")
        self.stop()

    def initialize_connections(self):
        """Initialize both MQTT and Serial connections"""
        try:
            # Initialize serial connection to PLC first
            self.serial_plc = SerialPLC(None)
            if not self.serial_plc.connect():
                logging.error("Failed to connect to PLC via serial")
                return False

            # Initialize MQTT client with serial handler
            self.mqtt_client = MQTTClient(self.serial_plc)
            self.serial_plc.mqtt_client = self.mqtt_client

            # Connect to MQTT broker
            self.mqtt_client.connect()

            logging.info("Both MQTT and Serial connections initialized successfully")
            return True

        except Exception as e:
            logging.error(f"Failed to initialize connections: {e}")
            return False

    def check_connections(self):
        """Check if both connections are still active"""
        mqtt_ok = self.mqtt_client and self.mqtt_client.client.is_connected()
        serial_ok = self.serial_plc and self.serial_plc.ser and self.serial_plc.ser.is_open

        if not mqtt_ok:
            logging.warning("MQTT connection lost")
        if not serial_ok:
            logging.warning("Serial connection lost")

        return mqtt_ok and serial_ok

    def reconnect(self):
        """Attempt to reconnect lost connections"""
        self.reconnect_attempts += 1

        if self.reconnect_attempts > self.max_reconnect_attempts:
            logging.error("Max reconnection attempts reached. Stopping...")
            return False

        logging.info(f"Attempting reconnect ({self.reconnect_attempts}/{self.max_reconnect_attempts})...")

        # Clean up existing connections
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        if self.serial_plc:
            self.serial_plc.disconnect()

        time.sleep(5)  # Wait before reconnecting

        return self.initialize_connections()

    def start(self):
        logging.info("Starting PLC-MQTT Bridge for Panasonic FP0...")
        logging.info("Entering standby mode - waiting for MQTT messages...")

        try:
            if not self.initialize_connections():
                logging.error("Initial connection failed")
                return False

            self.running = True
            self.reconnect_attempts = 0

            # Main standby loop
            while self.running:
                try:
                    # Check connections periodically
                    if not self.check_connections():
                        logging.warning("Connection lost, attempting to reconnect...")
                        if not self.reconnect():
                            break

                    # Just wait in standby mode
                    time.sleep(5)  # Check every 5 seconds

                    # Log standby status periodically
                    if int(time.time()) % 30 == 0:  # Every 30 seconds
                        logging.info("Standby mode active - Waiting for MQTT messages...")

                except Exception as e:
                    logging.error(f"Error in main loop: {e}")
                    time.sleep(10)  # Wait before continuing

            return True

        except Exception as e:
            logging.error(f"Failed to start bridge: {e}")
            return False

    def stop(self):
        logging.info("Stopping PLC-MQTT Bridge...")
        self.running = False

        if self.mqtt_client:
            self.mqtt_client.disconnect()

        if self.serial_plc:
            self.serial_plc.disconnect()

        logging.info("PLC-MQTT Bridge stopped completely")


if __name__ == "__main__":
    bridge = PLC_MQTT_Bridge()

    # Keep trying to start if initial startup fails
    while True:
        try:
            if bridge.start():
                break  # Exit if started successfully
            else:
                logging.warning("Startup failed, retrying in 10 seconds...")
                time.sleep(10)
        except KeyboardInterrupt:
            logging.info("Keyboard interrupt received during startup")
            break
        except Exception as e:
            logging.error(f"Unexpected error during startup: {e}")
            time.sleep(10)

    bridge.stop()
    sys.exit(0)
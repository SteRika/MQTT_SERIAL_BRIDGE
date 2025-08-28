import serial
import threading
import time
import logging
from config import *


class SerialPLC:
    def __init__(self, mqtt_client):
        self.ser = None
        self.mqtt_client = mqtt_client
        self.running = False
        self.read_thread = None
        self.connected = False

    def connect(self):
        try:
            logging.info(f"Attempting to connect to serial port: {SERIAL_PORT}")
            self.ser = serial.Serial(
                port=SERIAL_PORT,
                baudrate=SERIAL_BAUDRATE,
                parity=SERIAL_PARITY,
                stopbits=SERIAL_STOPBITS,
                bytesize=SERIAL_BYTESIZE,
                timeout=SERIAL_TIMEOUT
            )

            if self.ser.is_open:
                self.connected = True
                logging.info(f"Connected to serial port: {SERIAL_PORT}")
                self.running = True
                self.start_reading()

                # Send initial login command (if required)
                try:
                    self.login_to_plc()
                except Exception as e:
                    logging.warning(f"Login command failed: {e}")

                return True
            else:
                logging.error("Failed to open serial port")
                return False

        except serial.SerialException as e:
            logging.error(f"Serial connection error: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected serial connection error: {e}")
            return False

    def is_connected(self):
        return self.connected and self.ser and self.ser.is_open

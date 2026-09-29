# MQTT Serial Bridge

An industrial edge-integration service that connects a **Panasonic FP0 PLC** over serial communication to an **MQTT broker**.

The bridge enables MQTT commands to control PLC operations while PLC-side communication can be surfaced back through MQTT. The application includes connection monitoring, structured logging, graceful shutdown, and automatic reconnection to support long-running industrial environments.

## Architecture

```text
MQTT Broker
    │
    │ MQTT commands / status
    ▼
Python MQTT Client
    │
    │ command routing
    ▼
Serial PLC Controller
    │
    │ Panasonic MEWTOCOL / serial
    ▼
Panasonic FP0 PLC
```

## Key Features

- MQTT subscribe/publish using `paho-mqtt`
- Serial communication using `pyserial`
- Panasonic FP0 serial configuration
- MEWTOCOL command support
- MQTT-to-PLC command forwarding
- Direct PLC output control examples
- Periodic connection-health checks
- Automatic MQTT and serial reconnection
- Maximum reconnect-attempt protection
- File and console logging
- Graceful SIGINT / SIGTERM shutdown
- Configuration isolated in `config.py`

## Project Structure

```text
MQTT_SERIAL_BRIDGE/
├── Controller/
│   ├── mqtt_client.py     # MQTT connection, subscriptions and routing
│   └── serial_plc.py      # PLC serial connection and communication
├── config.py              # MQTT, serial and PLC configuration
├── main.py                # Bridge lifecycle and reconnect logic
├── requirements.txt
└── run.bat
```

## MQTT Topics

Default configuration:

```text
Subscribe: plc/commands/#
Publish:   plc/status
```

Examples implemented in the current project include:

```text
plc/commands/hello
plc/commands/y16
```

Other command payloads can be forwarded to the PLC through the serial controller.

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Update `config.py` for your environment:

- MQTT broker and port
- MQTT topics
- Serial COM port
- Baud rate, parity, stop bits and byte size
- PLC station number
- MEWTOCOL settings

Do not commit production credentials or sensitive broker configuration.

## Run

```bash
python main.py
```

The service will initialize the PLC serial connection, connect to MQTT, enter standby mode, and continuously monitor both connections.

## Engineering Focus

This project demonstrates practical experience with:

- Industrial software integration
- Edge-to-cloud messaging
- PLC communication
- Event-driven command routing
- Connection resilience
- Production logging and fault recovery

## Author

Steven Lim — Software Engineering, Industrial Automation & R&D

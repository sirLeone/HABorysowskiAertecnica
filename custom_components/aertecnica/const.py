"""Constants for the Aertecnica Central Vacuum integration."""
from typing import Final

DOMAIN: Final = "aertecnica"
DEFAULT_NAME: Final = "Aertecnica"

# Configuration
CONF_MODBUS_TYPE: Final = "modbus_type"
CONF_SERIAL_PORT: Final = "serial_port"
CONF_BAUDRATE: Final = "baudrate"
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_SLAVE_ID: Final = "slave_id"
CONF_SCAN_INTERVAL: Final = "scan_interval"

# Modbus Types
MODBUS_TYPE_RTU: Final = "rtu"
MODBUS_TYPE_TCP: Final = "tcp"

# Default Values
DEFAULT_BAUDRATE: Final = 19200
DEFAULT_PORT: Final = 502
DEFAULT_SLAVE_ID: Final = 1
DEFAULT_SCAN_INTERVAL: Final = 2
DEFAULT_TIMEOUT: Final = 3
DEFAULT_BROADCAST_ID: Final = 0

# Serial Configuration
SERIAL_DATABITS: Final = 8
SERIAL_STOPBITS: Final = 1
SERIAL_PARITY: Final = "N"

# Modbus Register Addresses (Holding Registers, base 0x0000)
REG_CARD_MODEL: Final = 0x0000
REG_INTERPRETATION_FLAGS: Final = 0x0001
REG_CARD_HOURS: Final = 0x0002
REG_MOTOR_HOURS: Final = 0x0003
REG_BAG_HOURS: Final = 0x0004
REG_FILTER_HOURS: Final = 0x0005
REG_BAG_LEVEL: Final = 0x0006
REG_FILTER_LEVEL: Final = 0x0007
REG_PRESSURE_LEVEL: Final = 0x0008
REG_PRESSURE_1: Final = 0x0009
REG_PRESSURE_2: Final = 0x000A
REG_PRESSURE_DIFF: Final = 0x000B
REG_TEMPERATURE: Final = 0x000C
REG_SYSTEM_STATUS: Final = 0x000D
REG_LOCK_STATUS: Final = 0x000E
REG_MOTOR_POWER: Final = 0x000F
REG_PRESSURE_SETPOINT: Final = 0x0010
REG_RESIDUAL_MAX_TIME: Final = 0x0011
REG_RESET_CONTROL: Final = 0x003F

# Card Models
CARD_MODELS: Final = {
    0: "Not Identified",
    1: "Perfect",
    2: "Classic",
}

# Interpretation Flags (Register 0x0001)
FLAG_CARD_HOURS_NO_DECIMAL: Final = 0x0001      # Bit 0
FLAG_MOTOR_HOURS_NO_DECIMAL: Final = 0x0002     # Bit 1
FLAG_BAG_HOURS_NO_DECIMAL: Final = 0x0004       # Bit 2
FLAG_FILTER_HOURS_NO_DECIMAL: Final = 0x0008    # Bit 3
FLAG_TEMPERATURE_NO_DECIMAL: Final = 0x0010     # Bit 4
FLAG_MAX_TIME_MINUTES: Final = 0x0020           # Bit 5 (1=minutes, 0=seconds)

# System Status Bits (Register 0x000D)
STATUS_PID_MASK: Final = 0x0003                 # Bits 0-1
STATUS_PID_DISABLED: Final = 0
STATUS_PID_MAX_VACUUM: Final = 1
STATUS_PID_MAINTAIN_PRESSURE: Final = 2
STATUS_MICRO_LINE_CLOSED: Final = 0x0004        # Bit 2
STATUS_START_STOP_ACTIVE: Final = 0x0008        # Bit 3
STATUS_MOTOR_ON: Final = 0x0010                 # Bit 4
STATUS_AUTO_RESET_DISABLED: Final = 0x0020      # Bit 5
STATUS_STANDBY_ACTIVE: Final = 0x0040           # Bit 6
STATUS_TEMP_RESET_PROHIBITED: Final = 0x0080    # Bit 7
STATUS_PREALARM_MAX_TIME: Final = 0x0100        # Bit 8
STATUS_PREALARM_MAX_PRESSURE: Final = 0x0200    # Bit 9
STATUS_PREALARM_NUM_STARTS: Final = 0x0400      # Bit 10
STATUS_PREALARM_DIRTY_FILTER: Final = 0x0800    # Bit 11
STATUS_PREALARM_FULL_BAG: Final = 0x1000        # Bit 12
STATUS_PREALARM_MAX_TEMP: Final = 0x2000        # Bit 13
STATUS_PREALARM_APPLIANCE: Final = 0x8000       # Bit 15

# Lock Status Bits (Register 0x000E)
LOCK_MAX_TIME: Final = 0x0001                   # Bit 0
LOCK_MAX_PRESSURE: Final = 0x0002               # Bit 1
LOCK_NUM_STARTS: Final = 0x0004                 # Bit 2
LOCK_DIRTY_FILTER: Final = 0x0008               # Bit 3
LOCK_FULL_BAG: Final = 0x0010                   # Bit 4
LOCK_MAX_TEMPERATURE: Final = 0x0020            # Bit 5
LOCK_APPLIANCE: Final = 0x0080                  # Bit 7

# Reset Control Bits (Register 0x003F)
RESET_LOCK: Final = 0x0001                      # Bit 0
RESET_FULL_BAG: Final = 0x0002                  # Bit 1
RESET_DIRTY_FILTER: Final = 0x0004              # Bit 2
RESET_MOTOR_HOURS: Final = 0x0008               # Bit 3
CONTROL_SERIAL_START: Final = 0x0010            # Bit 4
CONTROL_SERIAL_STOP: Final = 0x0020             # Bit 5

# Pressure Levels
PRESSURE_LEVEL_OFF: Final = 0
PRESSURE_LEVEL_LOW: Final = 1
PRESSURE_LEVEL_OK: Final = 2
PRESSURE_LEVEL_HIGH: Final = 3

PRESSURE_LEVEL_NAMES: Final = {
    PRESSURE_LEVEL_OFF: "Off",
    PRESSURE_LEVEL_LOW: "Low",
    PRESSURE_LEVEL_OK: "OK",
    PRESSURE_LEVEL_HIGH: "High",
}

# Entity Configuration
SENSOR_TYPES: Final = {
    "card_model": {
        "name": "Card Model",
        "register": REG_CARD_MODEL,
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:information-outline",
    },
    "card_hours": {
        "name": "Card Hours",
        "register": REG_CARD_HOURS,
        "unit": "h",
        "device_class": None,
        "state_class": "total_increasing",
        "icon": "mdi:clock-outline",
    },
    "motor_hours": {
        "name": "Motor Hours",
        "register": REG_MOTOR_HOURS,
        "unit": "h",
        "device_class": None,
        "state_class": "total_increasing",
        "icon": "mdi:engine-outline",
    },
    "bag_hours": {
        "name": "Bag Hours",
        "register": REG_BAG_HOURS,
        "unit": "h",
        "device_class": None,
        "state_class": "total_increasing",
        "icon": "mdi:air-filter",
    },
    "filter_hours": {
        "name": "Filter Hours",
        "register": REG_FILTER_HOURS,
        "unit": "h",
        "device_class": None,
        "state_class": "total_increasing",
        "icon": "mdi:air-filter",
    },
    "bag_level": {
        "name": "Bag Level",
        "register": REG_BAG_LEVEL,
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:delete",
    },
    "filter_level": {
        "name": "Filter Level",
        "register": REG_FILTER_LEVEL,
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:air-filter",
    },
    "pressure_level": {
        "name": "Pressure Level",
        "register": REG_PRESSURE_LEVEL,
        "unit": None,
        "device_class": None,
        "state_class": None,
        "icon": "mdi:gauge",
    },
    "pressure_1": {
        "name": "Pressure 1",
        "register": REG_PRESSURE_1,
        "unit": "mbar",
        "device_class": "pressure",
        "state_class": "measurement",
        "icon": "mdi:gauge",
    },
    "pressure_2": {
        "name": "Pressure 2",
        "register": REG_PRESSURE_2,
        "unit": "mbar",
        "device_class": "pressure",
        "state_class": "measurement",
        "icon": "mdi:gauge",
    },
    "pressure_diff": {
        "name": "Pressure Differential",
        "register": REG_PRESSURE_DIFF,
        "unit": "mbar",
        "device_class": "pressure",
        "state_class": "measurement",
        "icon": "mdi:gauge",
    },
    "temperature": {
        "name": "Temperature",
        "register": REG_TEMPERATURE,
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "icon": "mdi:thermometer",
    },
    "motor_power": {
        "name": "Motor Power",
        "register": REG_MOTOR_POWER,
        "unit": "%",
        "device_class": None,
        "state_class": "measurement",
        "icon": "mdi:engine",
    },
    "pressure_setpoint": {
        "name": "Pressure Setpoint",
        "register": REG_PRESSURE_SETPOINT,
        "unit": "mbar",
        "device_class": "pressure",
        "state_class": None,
        "icon": "mdi:target",
    },
    "residual_max_time": {
        "name": "Residual Max Time",
        "register": REG_RESIDUAL_MAX_TIME,
        "unit": None,  # Dynamic: minutes or seconds
        "device_class": None,
        "state_class": None,
        "icon": "mdi:timer-outline",
    },
}

# Binary Sensor Types (derived from status registers)
BINARY_SENSOR_TYPES: Final = {
    "motor_status": {
        "name": "Motor Status",
        "register": REG_SYSTEM_STATUS,
        "bit": STATUS_MOTOR_ON,
        "device_class": "running",
        "icon": "mdi:engine",
    },
    "standby_status": {
        "name": "Standby Status",
        "register": REG_SYSTEM_STATUS,
        "bit": STATUS_STANDBY_ACTIVE,
        "device_class": None,
        "icon": "mdi:power-sleep",
    },
    "micro_line_status": {
        "name": "Micro Line Closed",
        "register": REG_SYSTEM_STATUS,
        "bit": STATUS_MICRO_LINE_CLOSED,
        "device_class": None,
        "icon": "mdi:electric-switch-closed",
    },
}

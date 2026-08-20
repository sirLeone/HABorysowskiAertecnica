"""Constants for the Aertecnica Central Vacuum integration."""
from typing import Final

DOMAIN: Final = "aertecnica"
DEFAULT_NAME: Final = "Aertecnica"
MANUFACTURER: Final = "Aertecnica"

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

BAUDRATE_OPTIONS: Final = [9600, 19200, 38400, 57600, 115200]

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

# Contiguous data block read on every update (0x0000..0x0011)
DATA_BLOCK_START: Final = REG_CARD_MODEL
DATA_BLOCK_SIZE: Final = REG_RESIDUAL_MAX_TIME - REG_CARD_MODEL + 1

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

# Status flag bits mapped to data keys (Register 0x000D)
SYSTEM_STATUS_BITS: Final[dict[str, int]] = {
    "micro_line_closed": STATUS_MICRO_LINE_CLOSED,
    "start_stop_active": STATUS_START_STOP_ACTIVE,
    "motor_on": STATUS_MOTOR_ON,
    "standby_active": STATUS_STANDBY_ACTIVE,
    "temp_reset_prohibited": STATUS_TEMP_RESET_PROHIBITED,
}

# Pre-alarm bits mapped to data keys with human-readable labels (Register 0x000D)
PREALARM_BITS: Final[dict[str, tuple[int, str]]] = {
    "prealarm_max_time": (STATUS_PREALARM_MAX_TIME, "Max Time"),
    "prealarm_max_pressure": (STATUS_PREALARM_MAX_PRESSURE, "Max Pressure"),
    "prealarm_num_starts": (STATUS_PREALARM_NUM_STARTS, "Num Starts"),
    "prealarm_dirty_filter": (STATUS_PREALARM_DIRTY_FILTER, "Dirty Filter"),
    "prealarm_full_bag": (STATUS_PREALARM_FULL_BAG, "Full Bag"),
    "prealarm_max_temp": (STATUS_PREALARM_MAX_TEMP, "Max Temperature"),
    "prealarm_appliance": (STATUS_PREALARM_APPLIANCE, "Appliance"),
}

# Lock bits mapped to data keys with human-readable labels (Register 0x000E)
LOCK_BITS: Final[dict[str, tuple[int, str]]] = {
    "lock_max_time": (LOCK_MAX_TIME, "Max Time"),
    "lock_max_pressure": (LOCK_MAX_PRESSURE, "Max Pressure"),
    "lock_num_starts": (LOCK_NUM_STARTS, "Num Starts"),
    "lock_dirty_filter": (LOCK_DIRTY_FILTER, "Dirty Filter"),
    "lock_full_bag": (LOCK_FULL_BAG, "Full Bag"),
    "lock_max_temperature": (LOCK_MAX_TEMPERATURE, "Max Temperature"),
    "lock_appliance": (LOCK_APPLIANCE, "Appliance"),
}

PREALARM_ANY_MASK: Final = sum(bit for bit, _ in PREALARM_BITS.values())
LOCK_ANY_MASK: Final = sum(bit for bit, _ in LOCK_BITS.values())

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

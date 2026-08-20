# Aertecnica Central Vacuum for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License](https://img.shields.io/github/license/sirLeone/HABorysowskiAertecnica)](LICENSE)

Home Assistant integration for Aertecnica central vacuum systems (known as Borysowski in Poland). This integration uses Modbus RTU/TCP protocol to communicate with the central vacuum unit.

**[Polish version / Wersja polska](README.pl.md)**

## Features

- **Full Modbus Support**: Both RTU (serial) and TCP connections
- **Real-time Monitoring**:
  - Motor status and power percentage
  - Operating hours (card, motor, bag, filter)
  - Pressure readings (2 sensors + differential)
  - Temperature monitoring
  - Bag and filter levels
- **Motor Control**: Start/stop the vacuum motor remotely
- **Alarm System**: Pre-alarms and locks for maintenance, exposed as problem binary sensors
- **Maintenance**: Reset lock button to clear active locks
- **Easy Configuration**: Config flow with UI setup, scan interval adjustable later via options
- **HACS Compatible**: Install directly from HACS

## Supported Models

- Aertecnica Perfect
- Aertecnica Classic
- Compatible units sold as Borysowski in Poland

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/sirLeone/HABorysowskiAertecnica`
6. Select category: "Integration"
7. Click "Add"
8. Find "Aertecnica Central Vacuum" in HACS and click "Download"
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from GitHub
2. Copy the `custom_components/aertecnica` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

### Adding the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for **Aertecnica Central Vacuum**
4. Select your connection type:
   - **Modbus TCP**: For network connections (requires Modbus gateway)
   - **Modbus RTU**: For direct serial connections

#### Modbus TCP Configuration

- **Host**: IP address of your Modbus gateway or device
- **Port**: Modbus port (default: 502)
- **Slave ID**: Device ID (default: 1)
- **Scan Interval**: How often to poll the device in seconds (default: 2)

#### Modbus RTU Configuration

- **Serial Port**: Port path (e.g., `/dev/ttyUSB0`)
- **Baud Rate**: 19200 (as per Aertecnica specification)
- **Slave ID**: Device ID (default: 1)
- **Scan Interval**: How often to poll the device in seconds (default: 2)

### Changing Options

The scan interval can be changed at any time without re-adding the integration: go to **Settings** → **Devices & Services** → **Aertecnica Central Vacuum** → **Configure**. The integration reloads automatically after saving.

## Entities

### Sensors

The integration creates the following sensors:

| Sensor | Description | Unit |
|--------|-------------|------|
| Card Model | Device model (Perfect/Classic) | - |
| Card Hours | Total system operating hours | h |
| Motor Hours | Motor operating hours | h |
| Bag Hours | Bag usage hours | h |
| Filter Hours | Filter usage hours | h |
| Bag Level | Bag fill level (0-5) | - |
| Filter Level | Filter dirt level (0-5) | - |
| Pressure Level | Overall pressure status | - |
| Pressure 1 | Primary pressure sensor | mbar |
| Pressure 2 | Secondary pressure sensor | mbar |
| Pressure Differential | Pressure difference | mbar |
| Temperature | Motor temperature | °C |
| Motor Power | Current motor power | % |
| Pressure Setpoint | Target pressure setting | mbar |
| Residual Max Time | Remaining run time | min/s |

### Binary Sensors

| Binary Sensor | Description |
|---------------|-------------|
| Motor Status | Motor running state |
| Standby Status | Standby mode active |
| Micro Line Closed | Micro line contact closed |
| Pre-Alarm | Any pre-alarm active (problem) |
| Lock | Any lock active (problem) |

### Switches

| Switch | Description |
|--------|-------------|
| Motor | Start/stop the vacuum motor |

### Buttons

| Button | Description |
|--------|-------------|
| Reset Lock | Clear an active lock on the unit |

### Attributes

Many sensors include additional attributes with detailed information:

- **Motor Switch**: Shows active locks and pre-alarms
- **Temperature Sensor**: Temperature alarms and reset status
- **Bag/Filter Sensors**: Pre-alarm and lock status
- **Motor Power**: PID mode, motor status, standby status

## Example Automations

### Auto-start at specific time

```yaml
automation:
  - alias: "Start vacuum at 10 AM"
    trigger:
      - platform: time
        at: "10:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.aertecnica_motor
```

### Notification on error

```yaml
automation:
  - alias: "Vacuum error notification"
    trigger:
      - platform: state
        entity_id: binary_sensor.aertecnica_lock
        to: "on"
    action:
      - service: notify.mobile_app
        data:
          title: "Vacuum Error"
          message: "Vacuum system has errors: {{ state_attr('switch.aertecnica_motor', 'active_locks') }}"
```

### Filter replacement reminder

```yaml
automation:
  - alias: "Filter replacement reminder"
    trigger:
      - platform: numeric_state
        entity_id: sensor.aertecnica_filter_level
        above: 4
    action:
      - service: notify.mobile_app
        data:
          title: "Vacuum Maintenance"
          message: "Filter needs replacement soon!"
```

## Modbus Communication

This integration implements the Aertecnica Modbus protocol as specified in the official documentation:

- **Protocol**: Modbus RTU
- **Data Format**: 8 data bits, 1 stop bit, no parity
- **Baud Rate**: 19200 bps
- **Master ID**: 1
- **Broadcast Mode**: Master sends broadcasts (ID=0)
- **Register Base**: 0x0000 (Holding registers 4000x series)

For detailed register mapping, see the [Modbus documentation](Modbus_English.pdf).

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to device

**Solutions**:
- Verify Modbus settings (baud rate, serial port, IP address)
- Check physical connections
- Ensure no other software is using the serial port
- Verify firewall settings for TCP connections
- Check device is powered on and responding

### No Data Updates

**Problem**: Sensors show "Unknown" or outdated values

**Solutions**:
- Check scan interval (may need to increase)
- Verify Modbus connection is stable
- Check Home Assistant logs for errors
- Restart the integration

### Debug Logging

Enable debug logging to troubleshoot issues:

```yaml
logger:
  default: info
  logs:
    custom_components.aertecnica: debug
    pymodbus: debug
```

## Hardware Requirements

### For Modbus RTU (Serial)

- USB to RS485 converter
- RS485 cable connection to Aertecnica control board
- Proper wiring (A+, B-, GND)

### For Modbus TCP

- Modbus RTU to TCP gateway
- Network connection to Home Assistant

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

- **Issues**: [GitHub Issues](https://github.com/sirLeone/HABorysowskiAertecnica/issues)
- **Documentation**: [Technical Documentation](claude.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based on Aertecnica Modbus protocol specification
- Developed for the Home Assistant community
- Special thanks to all contributors

## Disclaimer

This is an unofficial integration not affiliated with Aertecnica S.p.A. Use at your own risk.

---

**Aertecnica** is a trademark of Aertecnica S.p.A.
**Borysowski** is the brand name used in Poland for Aertecnica products.

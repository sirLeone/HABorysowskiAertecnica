## Aertecnica Central Vacuum 0.9.0 Beta

First beta release of the integration.

### Bug fixes

- Scan interval configured via the options flow is now actually applied — the integration reloads automatically when options change.
- Options flow works on current Home Assistant versions (removed the deprecated `config_entry` assignment, dropped in HA 2025.12).
- Config flow now distinguishes connection failures from unexpected errors.

### New features

- **Binary sensors**: Motor Status, Standby Status, Micro Line Closed, plus Pre-Alarm and Lock problem sensors.
- **Button**: Reset Lock — clears an active lock on the unit.

### Refactoring

- Shared base entity class (device info, naming; unique IDs unchanged).
- Declarative `SensorEntityDescription`-based sensor definitions with HA unit and device-class enums.
- Table-driven Modbus register and status-bit parsing; magic numbers replaced with constants derived from the register map.
- Deduplicated RTU/TCP config-flow validation; removed dead code.

### Notes

- Requires Home Assistant 2024.1+ and pymodbus 3.5+.
- Beta: implemented against the Aertecnica Modbus specification — feedback from real hardware is welcome, please report issues.

## Aertecnica Central Vacuum 0.9.1

Bug-fix release. **Upgrading is strongly recommended**: on current Home Assistant releases version 0.9.0 could not talk to the device at all.

### Bugs fixed

- **No communication with the device on current Home Assistant (critical).** pymodbus 3.10 renamed the unit-id keyword from `slave=` to `device_id=`. Home Assistant 2025.x and newer ship pymodbus 3.10+, so every register read and write failed with `TypeError`, the integration never got past setup and all entities stayed unavailable. The client now detects which keyword the installed pymodbus accepts and works with both old (3.5–3.9) and new (3.10+) versions.
- **Failed motor start/stop was silent.** When the write to the control register failed, the switch only logged an error and the UI showed nothing. The switch now raises an error that Home Assistant displays, matching the Reset Lock button.
- **Coordinator relied on an implicit config entry.** The data coordinator was created without its config entry, which Home Assistant flags as deprecated and will stop supporting in 2026.8. The entry is now passed explicitly.

### Improvements

- Entity names are translated (English and Polish) via Home Assistant translation keys instead of hardcoded English strings. Entity IDs and unique IDs are unchanged, so existing automations and history keep working.
- Register parsing is a pure, unit-tested function; Modbus error handling is shared between reads and writes.
- Integration state is stored in `entry.runtime_data`, as recommended for current Home Assistant.

### Testing and tooling

- New automated test suite covering register parsing, the Modbus client wrapper, the config and options flows, integration setup, services and option reloads. Verified against Home Assistant 2026.2 with pymodbus 3.16 and against Home Assistant 2024.12 with pymodbus 3.8.
- GitHub Actions CI runs ruff and the test suite on every push and pull request.

### Requirements

- Minimum Home Assistant version is now **2024.11** (first release whose data coordinator accepts the config entry explicitly). pymodbus 3.5 or newer.

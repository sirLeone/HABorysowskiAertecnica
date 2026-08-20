# Aertecnica / Borysowski - Integracja Centralnego Odkurzacza

## Wprowadzenie

Integracja **Aertecnica Central Vacuum** umożliwia pełną kontrolę i monitorowanie centralnego odkurzacza firmy Aertecnica (znanego w Polsce jako **Borysowski**) w systemie Home Assistant. Wykorzystując protokół **Modbus RTU/TCP**, integracja zapewnia dostęp do wszystkich parametrów pracy urządzenia, umożliwiając automatyzację, monitorowanie i zdalne sterowanie.

## Krótki opis

Ta integracja została stworzona w oparciu o oficjalną dokumentację protokołu Modbus firmy Aertecnica i oferuje:

- 🔌 **Wsparcie dla Modbus RTU i TCP** - elastyczność w wyborze metody połączenia
- 📊 **15 sensorów + 5 sensorów binarnych** - kompleksowe monitorowanie wszystkich parametrów
- 🎛️ **Sterowanie silnikiem** - zdalne włączanie/wyłączanie odkurzacza
- ⚠️ **System alarmów** - prealarmy i blokady jako sensory binarne typu problem
- 🔓 **Reset blokad** - przycisk serwisowy kasujący aktywną blokadę
- 🌍 **Dwujęzyczność** - pełne wsparcie dla języka polskiego i angielskiego
- 🏠 **Config Flow** - prosta konfiguracja przez interfejs webowy
- 📦 **HACS** - łatwa instalacja i aktualizacje

## Dla kogo jest ta integracja?

- Właściciele centralnych odkurzaczy Aertecnica/Borysowski
- Użytkownicy Home Assistant pragnący zautomatyzować pracę odkurzacza
- Instalatorzy systemów smart home
- Osoby chcące monitorować zużycie filtrów i worków

## Funkcjonalność

### Monitoring w czasie rzeczywistym

Integracja umożliwia ciągłe monitorowanie stanu urządzenia:
- Status silnika (włączony/wyłączony/standby)
- Aktualna moc silnika (0-100%)
- Temperatura silnika z ostrzeżeniami o przegrzaniu
- Ciśnienie w systemie (3 czujniki)
- Poziom napełnienia worka (5 poziomów)
- Stan zabrudzenia filtra (5 poziomów)
- Godziny pracy (ogólne, silnika, worka, filtra)

### Automatyzacja

Dzięki integracji możesz:
- Włączać odkurzacz o określonych godzinach
- Otrzymywać powiadomienia o konieczności konserwacji
- Automatycznie wyłączać urządzenie po określonym czasie
- Reagować na alarmy i błędy
- Integrować z innymi urządzeniami w domu

### Bezpieczeństwo

System monitoruje:
- Przegrzanie silnika
- Przepełnienie worka
- Zabrudzenie filtra
- Przekroczenie maksymalnego czasu pracy
- Nadmierne ciśnienie

---

## Opis techniczny

### Architektura komunikacji

Integracja wykorzystuje protokół **Modbus RTU** zgodnie ze specyfikacją Aertecnica:

```
Protocol: Modbus RTU
Baud Rate: 19200 bps
Data Format: 8 data bits, 1 stop bit, No parity
Master ID: 1 (Aertecnica card)
Slave ID: 1 (configurable)
Broadcast: ID = 0 (Master → Displays)
```

### Rejestry do odczytu (Read-Only)

Integracja odczytuje 18 rejestrów Holding (0x0000 - 0x0011):

#### Register 0x0000 - Card Model
- **Typ**: Unsigned Word (16-bit)
- **Zakres**: 0-65535
- **Wartości**:
  - `0` = Not Identified
  - `1` = Perfect
  - `2` = Classic
- **Sensor**: `sensor.aertecnica_card_model`

#### Register 0x0001 - Interpretation Flags
- **Typ**: Unsigned Word (bit flags)
- **Opis**: Flagi określające format interpretacji wartości
- **Bity**:
  - Bit 0: Card Hours (1=bez dziesiętnych, 0=z dziesiętnymi)
  - Bit 1: Motor Hours (1=bez dziesiętnych, 0=z dziesiętnymi)
  - Bit 2: Bag Hours (1=bez dziesiętnych, 0=z dziesiętnymi)
  - Bit 3: Filter Hours (1=bez dziesiętnych, 0=z dziesiętnymi)
  - Bit 4: Temperature (1=bez dziesiętnych, 0=z dziesiętnymi)
  - Bit 5: Max Time (1=minuty, 0=sekundy)

#### Register 0x0002 - Card Hours
- **Typ**: Unsigned Word
- **Zakres**: 0-6553.5 godzin
- **Format**: Z dziesiętnymi lub bez (zależnie od flagi)
- **Sensor**: `sensor.aertecnica_card_hours`
- **Jednostka**: h

#### Register 0x0003 - Motor Hours
- **Typ**: Unsigned Word
- **Zakres**: 0-6553.5 godzin
- **Sensor**: `sensor.aertecnica_motor_hours`
- **Jednostka**: h

#### Register 0x0004 - Bag Hours
- **Typ**: Unsigned Word
- **Zakres**: 0-6553.5 godzin
- **Sensor**: `sensor.aertecnica_bag_hours`
- **Jednostka**: h

#### Register 0x0005 - Filter Hours
- **Typ**: Unsigned Word
- **Zakres**: 0-6553.5 godzin
- **Sensor**: `sensor.aertecnica_filter_hours`
- **Jednostka**: h

#### Register 0x0006 - Bag Level
- **Typ**: Unsigned Word
- **Zakres**: 0-5 poziomów
- **Sensor**: `sensor.aertecnica_bag_level`
- **Poziomy**:
  - 0 = Pusty
  - 5 = Pełny (wymaga wymiany)

#### Register 0x0007 - Filter Level
- **Typ**: Unsigned Word
- **Zakres**: 0-5 poziomów
- **Sensor**: `sensor.aertecnica_filter_level`
- **Poziomy**:
  - 0 = Czysty
  - 5 = Brudny (wymaga czyszczenia)

#### Register 0x0008 - Pressure Level
- **Typ**: Unsigned Word
- **Zakres**: 0-3
- **Sensor**: `sensor.aertecnica_pressure_level`
- **Wartości**:
  - 0 = Off
  - 1 = Low
  - 2 = OK
  - 3 = High

#### Register 0x0009 - Pressure 1
- **Typ**: Unsigned Word
- **Zakres**: 0-500 mbar
- **Sensor**: `sensor.aertecnica_pressure_1`
- **Jednostka**: mbar

#### Register 0x000A - Pressure 2
- **Typ**: Unsigned Word
- **Zakres**: 0-500 mbar
- **Sensor**: `sensor.aertecnica_pressure_2`
- **Jednostka**: mbar

#### Register 0x000B - Pressure Differential
- **Typ**: Unsigned Word
- **Zakres**: 0-500 mbar
- **Sensor**: `sensor.aertecnica_pressure_diff`
- **Jednostka**: mbar
- **Opis**: Różnica ciśnień statycznych

#### Register 0x000C - Temperature
- **Typ**: Signed Word
- **Zakres**: -20.0 do 150.0 °C
- **Sensor**: `sensor.aertecnica_temperature`
- **Jednostka**: °C
- **Format**: Z dziesiętnymi lub bez (zależnie od flagi)

#### Register 0x000D - System Status
- **Typ**: Unsigned Word (16-bit flags)
- **Opis**: Status systemu i alarmy
- **Wykorzystanie**: Sensory i switch
- **Bity**:
  - **Bit 0-1**: PID Activation Status
    - 0 = Disabled
    - 1 = PID Maximum vacuum limiter
    - 2 = PID maintenance of pressure setpoint
  - **Bit 2**: Micro Line Status (1=Closed, 0=Open)
  - **Bit 3**: Start Stop Status (1=Start button, 0=Micro line/OFF)
  - **Bit 4**: Motor Status (1=ON, 0=OFF) → `switch.aertecnica_motor`, `binary_sensor.aertecnica_motor_status`
  - **Bit 5**: Disable auto reset (1=Disabled, 0=Enabled)
  - **Bit 6**: Stand By Status (1=Active, 0=Not Active)
  - **Bit 7**: Temperature Reset Control (1=Prohibited, 0=Permitted)
  - **Bit 8**: Pre-alarm Maximum Time (1=Active, 0=Not Active)
  - **Bit 9**: Pre-alarm Maximum Pressure (1=Active, 0=Not Active)
  - **Bit 10**: Pre-alarm Number of Starts (1=Active, 0=Not Active)
  - **Bit 11**: Pre-alarm Dirty Filter (1=Active, 0=Not Active)
  - **Bit 12**: Pre-alarm Full Bag (1=Active, 0=Not Active)
  - **Bit 13**: Pre-alarm Max Temperature (1=Active, 0=Not Active)
  - **Bit 15**: Pre-alarm Appliance (1=Active, 0=Not Active)

#### Register 0x000E - Lock Status
- **Typ**: Unsigned Word (16-bit flags)
- **Opis**: Status blokad (błędów krytycznych)
- **Bity**:
  - **Bit 0**: Lock Maximum Time (1=Active)
  - **Bit 1**: Lock Maximum Pressure (1=Active)
  - **Bit 2**: Lock Number of Starts (1=Active)
  - **Bit 3**: Lock Dirty Filter (1=Active)
  - **Bit 4**: Lock Full Bag (1=Active)
  - **Bit 5**: Lock Max Temperature (1=Active)
  - **Bit 7**: Lock Appliance (1=Active)

#### Register 0x000F - Motor Power Percentage
- **Typ**: Unsigned Word
- **Zakres**: 0-100%
- **Sensor**: `sensor.aertecnica_motor_power`
- **Jednostka**: %

#### Register 0x0010 - Pressure Setpoint
- **Typ**: Unsigned Word
- **Zakres**: 0-500 mbar
- **Sensor**: `sensor.aertecnica_pressure_setpoint`
- **Jednostka**: mbar
- **Opis**: Docelowa wartość ciśnienia dla PID

#### Register 0x0011 - Residual Maximum Time
- **Typ**: Unsigned Word
- **Zakres**: 0-255 min / 0-15300 s
- **Sensor**: `sensor.aertecnica_residual_max_time`
- **Jednostka**: min lub s (zależnie od flagi)
- **Opis**: Pozostały czas do osiągnięcia maksymalnego czasu pracy

---

### Rejestry do zapisu (Write)

#### Register 0x003F - Reset Control
- **Typ**: Unsigned Word (16-bit flags)
- **Adres**: 0x003F (63 decimal)
- **Funkcja**: Write Single Register (0x06)
- **Dostęp**: Slave ID = 1 (lub Broadcast ID = 0)

**Bity sterujące:**

| Bit | Funkcja | Opis |
|-----|---------|------|
| 0 | Lock Reset Control | 1 = Reset wszystkich blokad |
| 1 | Full Bag Reset Control | 1 = Reset licznika worka |
| 2 | Dirty Filter Reset Control | 1 = Reset licznika filtra |
| 3 | Motor Hours Reset Control | 1 = Reset godzin silnika |
| 4 | Serial Start Control | 1 = Włącz silnik |
| 5 | Serial Stop Control | 1 = Wyłącz silnik |

**Wykorzystanie w integracji:**

1. **Włączanie silnika** - `switch.aertecnica_motor` → ON
   ```python
   await write_register(0x003F, 0x0010)  # Bit 4 = 1
   ```

2. **Wyłączanie silnika** - `switch.aertecnica_motor` → OFF
   ```python
   await write_register(0x003F, 0x0020)  # Bit 5 = 1
   ```

3. **Reset blokad** - `button.aertecnica_reset_lock`
   ```python
   await write_register(0x003F, 0x0001)  # Bit 0 = 1
   ```

---

## Mapowanie encji Home Assistant

### Sensory (15 encji)

| Entity ID | Nazwa | Rejestr | Typ | Jednostka |
|-----------|-------|---------|-----|-----------|
| `sensor.aertecnica_card_model` | Card Model | 0x0000 | string | - |
| `sensor.aertecnica_card_hours` | Card Hours | 0x0002 | float | h |
| `sensor.aertecnica_motor_hours` | Motor Hours | 0x0003 | float | h |
| `sensor.aertecnica_bag_hours` | Bag Hours | 0x0004 | float | h |
| `sensor.aertecnica_filter_hours` | Filter Hours | 0x0005 | float | h |
| `sensor.aertecnica_bag_level` | Bag Level | 0x0006 | int | - |
| `sensor.aertecnica_filter_level` | Filter Level | 0x0007 | int | - |
| `sensor.aertecnica_pressure_level` | Pressure Level | 0x0008 | string | - |
| `sensor.aertecnica_pressure_1` | Pressure 1 | 0x0009 | int | mbar |
| `sensor.aertecnica_pressure_2` | Pressure 2 | 0x000A | int | mbar |
| `sensor.aertecnica_pressure_diff` | Pressure Differential | 0x000B | int | mbar |
| `sensor.aertecnica_temperature` | Temperature | 0x000C | float | °C |
| `sensor.aertecnica_motor_power` | Motor Power | 0x000F | int | % |
| `sensor.aertecnica_pressure_setpoint` | Pressure Setpoint | 0x0010 | int | mbar |
| `sensor.aertecnica_residual_max_time` | Residual Max Time | 0x0011 | float | min/s |

### Sensory binarne (5 encji)

| Entity ID | Nazwa | Rejestr | Bit | Klasa |
|-----------|-------|---------|-----|-------|
| `binary_sensor.aertecnica_motor_status` | Motor Status | 0x000D | 4 | running |
| `binary_sensor.aertecnica_standby_status` | Standby Status | 0x000D | 6 | - |
| `binary_sensor.aertecnica_micro_line_closed` | Micro Line Closed | 0x000D | 2 | - |
| `binary_sensor.aertecnica_pre_alarm` | Pre-Alarm | 0x000D | 8-15 | problem |
| `binary_sensor.aertecnica_lock` | Lock | 0x000E | 0-7 | problem |

### Przełączniki (1 encja)

| Entity ID | Nazwa | Rejestr zapisu | Funkcja |
|-----------|-------|----------------|---------|
| `switch.aertecnica_motor` | Motor | 0x003F | Start/Stop silnika (Bit 4/5) |

### Przyciski (1 encja)

| Entity ID | Nazwa | Rejestr zapisu | Funkcja |
|-----------|-------|----------------|---------|
| `button.aertecnica_reset_lock` | Reset Lock | 0x003F | Reset blokad (Bit 0) |

---

## Atrybuty encji

Wiele sensorów zawiera dodatkowe atrybuty z informacjami diagnostycznymi:

### `switch.aertecnica_motor`

```yaml
state: on/off
attributes:
  motor_power: 75  # Aktualna moc w %
  standby_active: false
  start_stop_active: true
  any_lock_active: false
  any_prealarm_active: false
  active_locks: []  # Lista aktywnych blokad
  active_prealarms: []  # Lista aktywnych prealarmów
```

### `sensor.aertecnica_temperature`

```yaml
state: 45.5
attributes:
  prealarm_max_temp: false
  lock_max_temperature: false
  temp_reset_prohibited: false
```

### `sensor.aertecnica_bag_level`

```yaml
state: 2
attributes:
  prealarm: false
  lock: false
```

### `sensor.aertecnica_motor_power`

```yaml
state: 75
attributes:
  motor_on: true
  standby_active: false
  pid_mode: 2  # 0=Disabled, 1=Max Limiter, 2=Maintain Pressure
```

---

## Częstotliwość odpytywania

- **Domyślny scan_interval**: 2 sekundy
- **Konfigurowalne**: 1-60 sekund (do zmiany w każdej chwili w opcjach integracji: **Ustawienia** → **Urządzenia i usługi** → **Konfiguruj**)
- **Zgodność z protokołem**: Master wysyła 4 broadcasty/sekundę (normalnie), 1 broadcast/2s (w przypadku blokady)

---

## Wymagania sprzętowe

### Dla Modbus RTU (Serial)

**Wymagane:**
- Konwerter USB → RS485 (np. CH340, FTDI)
- Kabel RS485 2-żyłowy (A+, B-) + opcjonalnie GND
- Dostęp do płyty głównej Aertecnica

**Połączenie:**
```
USB/RS485 Converter          Aertecnica Board
┌─────────────┐              ┌──────────────┐
│ A+ (yellow) │─────────────→│ A+ (Modbus)  │
│ B- (blue)   │─────────────→│ B- (Modbus)  │
│ GND (black) │─────────────→│ GND          │
└─────────────┘              └──────────────┘
```

### Dla Modbus TCP

**Wymagane:**
- Bramka Modbus RTU → TCP (np. USR-TCP232-410s, Elfin EW11)
- Połączenie sieciowe z Home Assistant

**Konfiguracja bramki:**
- Serial: 19200 baud, 8N1
- Network: Static IP
- Mode: TCP Server (port 502)

---

## Przykłady automatyzacji

### 1. Automatyczne włączanie odkurzacza

```yaml
automation:
  - id: vacuum_morning_start
    alias: "Odkurzacz - Start poranny"
    trigger:
      - platform: time
        at: "08:00:00"
    condition:
      - condition: state
        entity_id: binary_sensor.home_occupied
        state: "off"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.aertecnica_motor
```

### 2. Powiadomienie o konieczności wymiany worka

```yaml
automation:
  - id: vacuum_bag_full
    alias: "Odkurzacz - Pełny worek"
    trigger:
      - platform: numeric_state
        entity_id: sensor.aertecnica_bag_level
        above: 4
    action:
      - service: notify.mobile_app
        data:
          title: "Odkurzacz - Konserwacja"
          message: "Worek odkurzacza jest prawie pełny (poziom {{ states('sensor.aertecnica_bag_level') }}/5)"
          data:
            priority: high
            tag: vacuum_maintenance
```

### 3. Alarm przegrzania

```yaml
automation:
  - id: vacuum_overheat
    alias: "Odkurzacz - Przegrzanie"
    trigger:
      - platform: numeric_state
        entity_id: sensor.aertecnica_temperature
        above: 80
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.aertecnica_motor
      - service: notify.all_devices
        data:
          title: "🚨 ALARM - Odkurzacz"
          message: "Temperatura silnika {{ states('sensor.aertecnica_temperature') }}°C! Odkurzacz został wyłączony."
```

### 4. Raport konserwacji co tydzień

```yaml
automation:
  - id: vacuum_weekly_report
    alias: "Odkurzacz - Raport tygodniowy"
    trigger:
      - platform: time
        at: "20:00:00"
    condition:
      - condition: time
        weekday: sun
    action:
      - service: notify.mobile_app
        data:
          title: "Odkurzacz - Raport tygodniowy"
          message: |
            Godziny pracy silnika: {{ states('sensor.aertecnica_motor_hours') }}h
            Worek: {{ states('sensor.aertecnica_bag_hours') }}h (poziom {{ states('sensor.aertecnica_bag_level') }}/5)
            Filtr: {{ states('sensor.aertecnica_filter_hours') }}h (poziom {{ states('sensor.aertecnica_filter_level') }}/5)
            Temperatura: {{ states('sensor.aertecnica_temperature') }}°C
```

---

## Logowanie i diagnostyka

### Włączenie logów debug

W `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.aertecnica: debug
    custom_components.aertecnica.modbus_client: debug
    custom_components.aertecnica.coordinator: debug
    pymodbus: debug
```

### Typowe komunikaty logów

**Poprawne połączenie:**
```
INFO: Connected to Aertecnica Modbus device
DEBUG: Successfully updated data: {...}
```

**Błąd połączenia:**
```
ERROR: Error connecting to Modbus device: [Errno 2] No such file or directory: '/dev/ttyUSB0'
ERROR: Failed to connect to Aertecnica Modbus device
```

**Błąd odczytu rejestru:**
```
ERROR: Error reading register 0x0000: Modbus Error: [...]
```

---

## Bezpieczeństwo i uwagi

⚠️ **Ważne informacje:**

1. **Nie ingeruj w parametry PID** - integracja odczytuje, ale nie zapisuje parametrów PID
2. **Reset blokad** - funkcja dostępna tylko gdy urządzenie pozwala (bit 7 rejestru status)
3. **Temperatura** - system automatycznie wyłącza się przy przekroczeniu progu
4. **Broadcast** - Master (Aertecnica) wysyła dane automatycznie, integracja tylko nasłuchuje
5. **Slave ID** - domyślnie 1, nie zmieniaj bez konsultacji z dokumentacją

---

## Wsparcie techniczne

**Problemy z integracją:**
- GitHub Issues: https://github.com/sirLeone/HABorysowskiAertecnica/issues

**Dokumentacja:**
- Pełna dokumentacja: [README.md](README.md)
- Dokumentacja polska: [README.pl.md](README.pl.md)
- Dokumentacja techniczna: [claude.md](claude.md)
- Protokół Modbus: [Modbus_English.pdf](Modbus_English.pdf)

---

**Wersja integracji**: 0.1.0
**Wymagania**: Home Assistant 2023.1+, pymodbus 3.5+
**Licencja**: MIT

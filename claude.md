# Projekt Integracji Aertecnica/Borysowski dla Home Assistant

## Opis Projektu

Integracja do Home Assistant umożliwiająca komunikację z centralnym odkurzaczem włoskiej firmy Aertecnica (w Polsce znanym jako Borysowski) za pomocą protokołu Modbus. Integracja będzie dostępna w HACS (Home Assistant Community Store) i instalowalna bezpośrednio z HACS.

## Cel Projektu

Stworzenie pełnowartościowej integracji Home Assistant, która pozwoli na:
- Monitorowanie stanu centralnego odkurzacza
- Sterowanie odkurzaczem
- Odczyt parametrów pracy (czas pracy, moc, itp.)
- Diagnostykę błędów
- Automatyzację pracy odkurzacza

## Wymagania Techniczne

### Home Assistant
- Kompatybilność z Home Assistant Core 2023.1+
- Wsparcie dla Home Assistant OS, Supervised, Container i Core
- Zgodność z Config Flow (konfiguracja przez UI)

### Komunikacja
- Protokół: Modbus RTU/TCP
- Wsparcie dla pymodbus lub asyncio-modbus
- Asynchroniczna komunikacja (asyncio)
- Obsługa błędów połączenia i retry logic

### HACS
- Spełnienie wszystkich wymagań HACS Default Repository
- Prawidłowa struktura katalogów
- Kompletna dokumentacja
- Versioning zgodny z Semantic Versioning 2.0.0

## Architektura Integracji

### Struktura Plików

```
custom_components/
└── aertecnica/
    ├── __init__.py              # Inicjalizacja integracji
    ├── manifest.json            # Manifest integracji
    ├── config_flow.py           # UI konfiguracji
    ├── const.py                 # Stałe i definicje
    ├── sensor.py                # Sensory (stan, parametry)
    ├── switch.py                # Przełączniki (włącz/wyłącz)
    ├── coordinator.py           # Data Update Coordinator
    ├── modbus_client.py         # Klient Modbus
    ├── strings.json             # Tłumaczenia (EN)
    ├── translations/
    │   ├── en.json             # Tłumaczenia angielskie
    │   └── pl.json             # Tłumaczenia polskie
    └── services.yaml            # Definicje serwisów
```

### Dodatkowe Pliki Wymagane przez HACS

```
.
├── README.md                    # Dokumentacja główna (EN)
├── README.pl.md                 # Dokumentacja polska
├── LICENSE                      # Licencja (już istnieje)
├── hacs.json                    # Konfiguracja HACS
├── .github/
│   └── workflows/
│       ├── validate.yml        # Walidacja HACS
│       └── release.yml         # Automatyczne wydania
└── info.md                      # Info dla HACS
```

## Wymagania HACS

### Obowiązkowe Elementy

1. **Repository Structure**
   - `custom_components/<domain>/` z wszystkimi plikami integracji
   - `hacs.json` w katalogu głównym
   - `README.md` w języku angielskim

2. **manifest.json**
   ```json
   {
     "domain": "aertecnica",
     "name": "Aertecnica Central Vacuum",
     "codeowners": ["@username"],
     "config_flow": true,
     "documentation": "https://github.com/username/HABorysowskiAertecnica",
     "issue_tracker": "https://github.com/username/HABorysowskiAertecnica/issues",
     "requirements": ["pymodbus>=3.0.0"],
     "version": "0.1.0",
     "iot_class": "local_polling"
   }
   ```

3. **hacs.json**
   ```json
   {
     "name": "Aertecnica Central Vacuum",
     "render_readme": true,
     "domains": ["sensor", "switch"]
   }
   ```

4. **Versioning**
   - Tagi Git zgodne z Semantic Versioning (np. v1.0.0)
   - Releases na GitHub

5. **Documentation**
   - Szczegółowy README.md
   - Instrukcja instalacji
   - Przykłady konfiguracji
   - Opis parametrów Modbus

## Komunikacja Modbus

### Parametry Połączenia

Integracja powinna obsługiwać:
- **Modbus RTU**: przez port szeregowy (RS485)
  - Port: /dev/ttyUSB0, /dev/ttyAMA0, itp.
  - Baudrate: 9600, 19200, 38400, 115200
  - Data bits: 8
  - Stop bits: 1
  - Parity: None, Even, Odd

- **Modbus TCP**: przez sieć
  - Host: adres IP urządzenia lub gateway Modbus
  - Port: 502 (domyślny)

### Rejestry Modbus (Do Ustalenia)

Należy zidentyfikować następujące rejestry:
- Stan urządzenia (ON/OFF)
- Tryb pracy
- Moc silnika (%)
- Czas pracy (godziny)
- Status błędów
- Temperatura silnika
- Status filtra
- Licznik włączeń

**UWAGA**: Dokładna mapa rejestrów musi być uzyskana z dokumentacji technicznej Aertecnica lub poprzez reverse engineering.

### Przykładowa Mapa Rejestrów (Przykład - Do Weryfikacji)

```python
REGISTERS = {
    "status": {
        "address": 0,
        "type": "holding",
        "data_type": "uint16"
    },
    "power": {
        "address": 1,
        "type": "holding",
        "data_type": "uint16"
    },
    "operating_hours": {
        "address": 10,
        "type": "holding",
        "data_type": "uint32"
    },
    # ... więcej rejestrów
}
```

## Implementacja

### Faza 1: Podstawowa Struktura
- [x] Utworzenie repozytorium
- [ ] Utworzenie struktury katalogów
- [ ] Przygotowanie manifest.json
- [ ] Przygotowanie hacs.json
- [ ] Config Flow (podstawowa konfiguracja)

### Faza 2: Komunikacja Modbus
- [ ] Implementacja klasy ModbusClient
- [ ] Obsługa Modbus RTU
- [ ] Obsługa Modbus TCP
- [ ] Obsługa błędów i reconnect
- [ ] Testy jednostkowe komunikacji

### Faza 3: Sensory i Encje
- [ ] Coordinator dla aktualizacji danych
- [ ] Sensor - Stan urządzenia
- [ ] Sensor - Moc
- [ ] Sensor - Czas pracy
- [ ] Switch - Włącz/Wyłącz
- [ ] Obsługa atrybutów dodatkowych

### Faza 4: Zaawansowane Funkcje
- [ ] Serwisy niestandardowe
- [ ] Diagnostyka i logowanie
- [ ] Obsługa błędów urządzenia
- [ ] Konfiguracja częstotliwości odpytywania

### Faza 5: Dokumentacja i HACS
- [ ] Kompletny README.md (EN)
- [ ] README.pl.md (PL)
- [ ] info.md dla HACS
- [ ] Przykłady automatyzacji
- [ ] GitHub Actions dla walidacji

### Faza 6: Testy i Release
- [ ] Testy integracyjne
- [ ] Testy na prawdziwym urządzeniu
- [ ] Pierwszy release (v1.0.0)
- [ ] Dodanie do HACS

## Encje Home Assistant

### Sensory (sensor.py)

1. **Status Sensor**
   - Nazwa: `sensor.aertecnica_status`
   - Stan: on/off/error/standby
   - Atrybuty: error_code, last_updated

2. **Power Sensor**
   - Nazwa: `sensor.aertecnica_power`
   - Stan: 0-100%
   - Unit: %

3. **Operating Hours**
   - Nazwa: `sensor.aertecnica_operating_hours`
   - Stan: liczba godzin
   - Unit: h

4. **Motor Temperature**
   - Nazwa: `sensor.aertecnica_temperature`
   - Stan: temperatura
   - Unit: °C

### Przełączniki (switch.py)

1. **Main Switch**
   - Nazwa: `switch.aertecnica_vacuum`
   - Akcje: włącz/wyłącz odkurzacz

### Opcjonalne Encje

- **Binary Sensor**: Filter Status (czysty/brudny)
- **Binary Sensor**: Error Status
- **Select**: Power Mode (low/medium/high)

## Konfiguracja przez UI (Config Flow)

### Krok 1: Wybór Typu Połączenia
- Modbus RTU (Serial)
- Modbus TCP

### Krok 2a: Konfiguracja RTU
- Port szeregowy
- Baudrate
- Parity
- Slave ID

### Krok 2b: Konfiguracja TCP
- Host
- Port
- Slave ID

### Krok 3: Opcje
- Częstotliwość odpytywania (scan_interval)
- Nazwa integracji

## Services (Serwisy)

Niestandardowe serwisy dla zaawansowanej kontroli:

```yaml
set_power_level:
  description: Ustawienie poziomu mocy odkurzacza
  fields:
    level:
      description: Poziom mocy (0-100)
      example: 75

reset_filter_counter:
  description: Reset licznika filtra
  fields: {}

get_diagnostics:
  description: Pobierz informacje diagnostyczne
  fields: {}
```

## Przykładowe Automatyzacje

### Automatyczne Włączanie
```yaml
automation:
  - alias: "Włącz odkurzacz o 10:00"
    trigger:
      platform: time
      at: "10:00:00"
    action:
      service: switch.turn_on
      target:
        entity_id: switch.aertecnica_vacuum
```

### Powiadomienie o Błędzie
```yaml
automation:
  - alias: "Powiadomienie o błędzie odkurzacza"
    trigger:
      platform: state
      entity_id: sensor.aertecnica_status
      to: "error"
    action:
      service: notify.mobile_app
      data:
        message: "Odkurzacz zgłosił błąd!"
```

## Testy

### Testy Jednostkowe
- Testy komunikacji Modbus (mock)
- Testy parsowania danych
- Testy coordinator
- Testy config flow

### Testy Integracyjne
- Test na emulatorze Modbus
- Test z prawdziwym urządzeniem
- Test różnych scenariuszy błędów

## Bezpieczeństwo i Wydajność

### Bezpieczeństwo
- Walidacja danych wejściowych
- Obsługa timeout połączeń
- Bezpieczne logowanie (bez haseł/kluczy)

### Wydajność
- Asynchroniczna komunikacja
- Buforowanie danych
- Inteligentny polling (tylko gdy potrzeba)
- Limity retry przy błędach

## Logowanie i Diagnostyka

```python
import logging
_LOGGER = logging.getLogger(__name__)

# Poziomy logowania:
# DEBUG - szczegóły komunikacji Modbus
# INFO - ważne wydarzenia (połączenie, rozłączenie)
# WARNING - błędy tymczasowe, retry
# ERROR - błędy krytyczne
```

## Licencja

Projekt na licencji Apache 2.0 (już istnieje w repozytorium).

## Kontakt i Wsparcie

- **Issues**: GitHub Issues dla zgłoszeń błędów
- **Discussions**: GitHub Discussions dla pytań
- **Pull Requests**: Wkład społeczności mile widziany

## Roadmap

### v1.0.0 - MVP (Minimum Viable Product)
- Podstawowa komunikacja Modbus
- Sensory: status, moc, czas pracy
- Switch: włącz/wyłącz
- Instalacja przez HACS

### v1.1.0 - Rozszerzone funkcje
- Dodatkowe sensory
- Niestandardowe serwisy
- Więcej opcji konfiguracji

### v2.0.0 - Zaawansowane
- Wsparcie dla wielu urządzeń
- Statystyki i wykresy
- Predykcja konserwacji

## Notatki Techniczne

### Wymagane Biblioteki Python
- `pymodbus>=3.0.0` - komunikacja Modbus
- `homeassistant>=2023.1.0` - API Home Assistant

### Testowanie Lokalne
```bash
# Instalacja Home Assistant dev
python3 -m venv venv
source venv/bin/activate
pip install homeassistant

# Kopiowanie integracji
mkdir -p config/custom_components
cp -r custom_components/aertecnica config/custom_components/

# Uruchomienie HA
hass -c config
```

### Debug Modbus
```bash
# Test połączenia Modbus (pymodbus-console)
pip install pymodbus[repl]
pymodbus.console tcp --host 192.168.1.100 --port 502
```

## Checklist przed Release

- [ ] Wszystkie pliki w odpowiedniej strukturze
- [ ] manifest.json poprawny i kompletny
- [ ] hacs.json poprawny
- [ ] README.md kompletny (EN)
- [ ] README.pl.md kompletny (PL)
- [ ] Testy jednostkowe przechodzą
- [ ] Testy na prawdziwym urządzeniu
- [ ] Dokumentacja API Modbus
- [ ] Przykłady automatyzacji
- [ ] Tag wersji (v1.0.0)
- [ ] GitHub Release z opisem zmian
- [ ] Zgłoszenie do HACS

## Zasoby

### Dokumentacja
- [Home Assistant Integration Development](https://developers.home-assistant.io/)
- [HACS Documentation](https://hacs.xyz/)
- [PyModbus Documentation](https://pymodbus.readthedocs.io/)

### Przykładowe Integracje Modbus
- `homeassistant/components/modbus/`
- Inne integracje HACS używające Modbus

### Narzędzia
- [HACS Action](https://github.com/hacs/action) - CI/CD
- [hassfest](https://github.com/home-assistant/hassfest) - Walidacja
- [Home Assistant VSCode Extension](https://marketplace.visualstudio.com/items?itemName=keesschollaart.vscode-home-assistant)

## Status Projektu

**Aktualna wersja**: 0.0.1 (Development)
**Data ostatniej aktualizacji**: 2026-01-23
**Status**: Faza planowania i dokumentacji

---

## Następne Kroki

1. ✅ Utworzenie dokumentacji projektu (claude.md)
2. Uzyskanie dokumentacji technicznej Aertecnica (mapa rejestrów Modbus)
3. Utworzenie struktury katalogów
4. Implementacja podstawowego Config Flow
5. Implementacja komunikacji Modbus
6. Testy z urządzeniem

---

**Uwaga**: Ten dokument jest żywym dokumentem i będzie aktualizowany w miarę postępu projektu.
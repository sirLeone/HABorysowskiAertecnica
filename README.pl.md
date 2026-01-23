# Aertecnica / Borysowski - Integracja dla Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License](https://img.shields.io/github/license/sirLeone/HABorysowskiAertecnica)](LICENSE)

Integracja Home Assistant dla centralnych odkurzaczy Aertecnica (znanych w Polsce jako Borysowski). Integracja wykorzystuje protokół Modbus RTU/TCP do komunikacji z centralą odkurzacza.

**[English version / Wersja angielska](README.md)**

## Funkcje

- **Pełne wsparcie Modbus**: Połączenia RTU (szeregowe) i TCP
- **Monitorowanie w czasie rzeczywistym**:
  - Status silnika i procent mocy
  - Godziny pracy (karta, silnik, worek, filtr)
  - Odczyty ciśnienia (2 czujniki + różnica)
  - Monitorowanie temperatury
  - Poziomy worka i filtra
- **Sterowanie silnikiem**: Zdalne włączanie/wyłączanie silnika odkurzacza
- **System alarmów**: Prealarmy i blokady dla potrzeb konserwacji
- **Łatwa konfiguracja**: Config flow z konfiguracją przez interfejs UI
- **Zgodność z HACS**: Instalacja bezpośrednio z HACS

## Obsługiwane modele

- Aertecnica Perfect
- Aertecnica Classic
- Kompatybilne urządzenia sprzedawane jako Borysowski w Polsce

## Instalacja

### HACS (Zalecane)

1. Otwórz HACS w Home Assistant
2. Kliknij "Integracje"
3. Kliknij trzy kropki w prawym górnym rogu
4. Wybierz "Repozytoria niestandardowe"
5. Dodaj URL tego repozytorium: `https://github.com/sirLeone/HABorysowskiAertecnica`
6. Wybierz kategorię: "Integration"
7. Kliknij "Dodaj"
8. Znajdź "Aertecnica Central Vacuum" w HACS i kliknij "Pobierz"
9. Uruchom ponownie Home Assistant

### Instalacja ręczna

1. Pobierz najnowszą wersję z GitHub
2. Skopiuj folder `custom_components/aertecnica` do katalogu `custom_components` w Home Assistant
3. Uruchom ponownie Home Assistant

## Konfiguracja

### Dodawanie integracji

1. Przejdź do **Ustawienia** → **Urządzenia i usługi**
2. Kliknij **Dodaj integrację**
3. Wyszukaj **Aertecnica Central Vacuum**
4. Wybierz typ połączenia:
   - **Modbus TCP**: Dla połączeń sieciowych (wymaga bramki Modbus)
   - **Modbus RTU**: Dla bezpośrednich połączeń szeregowych

#### Konfiguracja Modbus TCP

- **Host**: Adres IP bramki Modbus lub urządzenia
- **Port**: Port Modbus (domyślnie: 502)
- **Slave ID**: ID urządzenia (domyślnie: 1)
- **Interwał skanowania**: Jak często odpytywać urządzenie w sekundach (domyślnie: 2)

#### Konfiguracja Modbus RTU

- **Port szeregowy**: Ścieżka portu (np. `/dev/ttyUSB0`)
- **Prędkość transmisji**: 19200 (zgodnie ze specyfikacją Aertecnica)
- **Slave ID**: ID urządzenia (domyślnie: 1)
- **Interwał skanowania**: Jak często odpytywać urządzenie w sekundach (domyślnie: 2)

## Encje

### Sensory

Integracja tworzy następujące sensory:

| Sensor | Opis | Jednostka |
|--------|------|-----------|
| Card Model | Model urządzenia (Perfect/Classic) | - |
| Card Hours | Całkowite godziny pracy systemu | h |
| Motor Hours | Godziny pracy silnika | h |
| Bag Hours | Godziny użytkowania worka | h |
| Filter Hours | Godziny użytkowania filtra | h |
| Bag Level | Poziom napełnienia worka (0-5) | - |
| Filter Level | Poziom zabrudzenia filtra (0-5) | - |
| Pressure Level | Ogólny status ciśnienia | - |
| Pressure 1 | Główny czujnik ciśnienia | mbar |
| Pressure 2 | Drugorzędny czujnik ciśnienia | mbar |
| Pressure Differential | Różnica ciśnień | mbar |
| Temperature | Temperatura silnika | °C |
| Motor Power | Aktualna moc silnika | % |
| Pressure Setpoint | Docelowe ustawienie ciśnienia | mbar |
| Residual Max Time | Pozostały czas pracy | min/s |

### Przełączniki

| Przełącznik | Opis |
|-------------|------|
| Motor | Włącz/wyłącz silnik odkurzacza |

### Atrybuty

Wiele sensorów zawiera dodatkowe atrybuty ze szczegółowymi informacjami:

- **Przełącznik silnika**: Pokazuje aktywne blokady i prealarmy
- **Sensor temperatury**: Alarmy temperatury i status resetu
- **Sensory worka/filtra**: Status prealarmu i blokady
- **Moc silnika**: Tryb PID, status silnika, status standby

## Przykładowe automatyzacje

### Automatyczne uruchomienie o określonej godzinie

```yaml
automation:
  - alias: "Uruchom odkurzacz o 10:00"
    trigger:
      - platform: time
        at: "10:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.aertecnica_motor
```

### Powiadomienie o błędzie

```yaml
automation:
  - alias: "Powiadomienie o błędzie odkurzacza"
    trigger:
      - platform: state
        entity_id: switch.aertecnica_motor
        attribute: any_lock_active
        to: true
    action:
      - service: notify.mobile_app
        data:
          title: "Błąd odkurzacza"
          message: "System odkurzacza ma błędy: {{ state_attr('switch.aertecnica_motor', 'active_locks') }}"
```

### Przypomnienie o wymianie filtra

```yaml
automation:
  - alias: "Przypomnienie o wymianie filtra"
    trigger:
      - platform: numeric_state
        entity_id: sensor.aertecnica_filter_level
        above: 4
    action:
      - service: notify.mobile_app
        data:
          title: "Konserwacja odkurzacza"
          message: "Filtr wymaga wkrótce wymiany!"
```

## Komunikacja Modbus

Integracja implementuje protokół Modbus firmy Aertecnica zgodnie z oficjalną dokumentacją:

- **Protokół**: Modbus RTU
- **Format danych**: 8 bitów danych, 1 bit stopu, brak parzystości
- **Prędkość transmisji**: 19200 bps
- **Master ID**: 1
- **Tryb broadcast**: Master wysyła broadcasty (ID=0)
- **Baza rejestrów**: 0x0000 (rejestry Holding seria 4000x)

Szczegółowa mapa rejestrów znajduje się w [dokumentacji Modbus](Modbus_English.pdf).

## Rozwiązywanie problemów

### Problemy z połączeniem

**Problem**: Nie można połączyć się z urządzeniem

**Rozwiązania**:
- Sprawdź ustawienia Modbus (prędkość transmisji, port szeregowy, adres IP)
- Sprawdź połączenia fizyczne
- Upewnij się, że żadne inne oprogramowanie nie używa portu szeregowego
- Sprawdź ustawienia zapory dla połączeń TCP
- Sprawdź, czy urządzenie jest włączone i odpowiada

### Brak aktualizacji danych

**Problem**: Sensory pokazują "Nieznany" lub przestarzałe wartości

**Rozwiązania**:
- Sprawdź interwał skanowania (może być konieczne zwiększenie)
- Sprawdź, czy połączenie Modbus jest stabilne
- Sprawdź logi Home Assistant pod kątem błędów
- Uruchom ponownie integrację

### Logowanie debugowania

Włącz logowanie debugowania, aby rozwiązać problemy:

```yaml
logger:
  default: info
  logs:
    custom_components.aertecnica: debug
    pymodbus: debug
```

## Wymagania sprzętowe

### Dla Modbus RTU (Szeregowy)

- Konwerter USB na RS485
- Połączenie kabla RS485 z płytą sterującą Aertecnica
- Prawidłowe okablowanie (A+, B-, GND)

### Dla Modbus TCP

- Bramka Modbus RTU na TCP
- Połączenie sieciowe z Home Assistant

## Współpraca

Współpraca jest mile widziana! Zapraszam do przesyłania Pull Requestów.

## Wsparcie

- **Zgłoszenia**: [GitHub Issues](https://github.com/sirLeone/HABorysowskiAertecnica/issues)
- **Dokumentacja**: [Dokumentacja techniczna](claude.md)

## Licencja

Ten projekt jest objęty licencją MIT - zobacz plik [LICENSE](LICENSE) po szczegóły.

## Podziękowania

- Oparte na specyfikacji protokołu Modbus firmy Aertecnica
- Opracowane dla społeczności Home Assistant
- Specjalne podziękowania dla wszystkich współtwórców

## Zastrzeżenie

To jest nieoficjalna integracja niezwiązana z Aertecnica S.p.A. Używasz na własne ryzyko.

---

**Aertecnica** jest znakiem towarowym Aertecnica S.p.A.
**Borysowski** jest nazwą marki używaną w Polsce dla produktów Aertecnica.

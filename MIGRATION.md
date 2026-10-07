# Migracja z `esphome_samsung_hvac_bus` (samsung_ac) na `samsung_nasa`

Konfiguracja: [`samsung_hvac.yaml`](samsung_hvac.yaml). Zastępuje `esphome_samsung_hvac_bus.yaml` z repozytorium `antrov/esphome_samsung_hvac_bus`.

## Jak Home Assistant rozpoznaje encje ESPHome

`unique_id` = **MAC urządzenia + platforma + hash nazwy encji**. `entity_id`, historia, statystyki, obszary, automatyzacje i dashboardy są przypięte do `unique_id`. Ciągłość wymaga więc trzech rzeczy:

1. ten sam układ ESP32 (ten sam MAC) i `esphome.name: samsung_hvac`,
2. dokładnie te same nazwy encji (wielkość liter i spacje się liczą),
3. ta sama platforma encji (`sensor` zostaje `sensor`, `number` zostaje `number` itd.).

Jednostka, `device_class` i `state_class` nie zmieniają `unique_id`, ale zmiana jednostki przy czujniku ze statystykami powoduje w HA komunikat o niezgodnych jednostkach. Dlatego także je zachowałem.

## Mapowanie encji

| Opcja w `samsung_ac` | Platforma | Wiadomość NASA | Jednostka NASA | Nazwa w HA | Źródło nazwy |
|---|---|---|---|---|---|
| `error_code` | sensor | `0x8235` | 10.00.00 | `error_code` | yaml |
| `outdoor_instantaneous_power` | sensor | `0x8413` | 10.00.00 | `Outdoor Instantaneous Power` | yaml |
| `outdoor_cumulative_energy` | sensor | `0x8414` | 10.00.00 | `Outdoor Cumulative Energy` | yaml |
| `outdoor_current` | sensor | `0x8217` | 10.00.00 | `Outdoor Current` | yaml |
| `outdoor_voltage` | sensor | `0x24FC` | 10.00.00 | `Outdoor Voltage` | yaml |
| `outdoor_temperature` | sensor | `0x8204` | 10.00.00 | `Outdoor temperature` | yaml |
| `water_temperature` | sensor | `0x4237` | 20.00.00 | `Warm water` | yaml |
| `water_target_temperature` | number | `0x4235` | 20.00.00 | `Hot Water Target Temperature` | yaml |
| `water_heater_mode` | select | `0x4066` | 20.00.00 | `Hotwater Mode` | yaml |
| `flow` | sensor | `0x42E9` | 20.00.00 | `Flow` | lista encji w HA |
| `water_outlet_zone1_temperature` | sensor | `0x42D8` | 20.00.00 | `Water Outlet Zone 1` | lista encji w HA |
| `water_outlet_zone2_temperature` | sensor | `0x42D9` | 20.00.00 | `Water Outlet Zone 2` | lista encji w HA |
| `threeway_valve_tank` | binary_sensor | `0x4067` | 20.00.00 | `Threeway Valve on Tank` | lista encji w HA |
| `heating_curve_shift` | number | `0x4248` | 20.00.00 | `Heating Curve Shift` | lista encji w HA |

**Nazwy z listy encji w HA.** Pięć encji z kodu forka (`main`) nie miało nazw w repozytorium (prywatny yaml jest w `.gitignore`). Nazwy zostały potwierdzone na liście encji urządzenia `Samsung HVAC` w HA.

Czego nie przenoszę: w `esphome_samsung_hvac_bus.yaml` urządzenie `20.00.00` miało wszystkie wpisy w komentarzu (brak `climate`, `room_temperature` itd.), więc nic z niego nie przenoszę.

## Świadome różnice

- **`friendly_name`.** Stary plik miał `Climate`, ale w HA urządzenie nazywa się `Samsung HVAC` (stąd `entity_id` typu `sensor.samsung_hvac_*`), więc tak je nazwałem.
- **Adres jednostki dla `0x4xxx`.** W starym pliku encje CWU stały pod `10.00.00` (skopiowane z `example.yaml` upstreamu). Obie implementacje kierują wiadomość do encji po adresie nadawcy, a wiadomości `0x4xxx` wysyła jednostka wewnętrzna (hydro) `20.00.00`, więc tu są odczytywane z `20.00.00`. Jeśli po wgraniu `Warm water`, `Hot Water Target Temperature` lub `Hotwater Mode` są `unknown`, sprawdź w logu linie `Undefined s:… d:… 0x4237 …` (flaga `debug_log_undefined_messages` jest włączona) i zmień adres.
- **Opcje selecta `Hotwater Mode`.** `samsung_nasa` nazywa pierwszą opcję `Economy`, a `samsung_ac` używał `Eco`. Zmiana nazwy opcji zmieniłaby stany w historii i zepsuła wywołania `select.select_option` z `"Eco"`. Dodałem do platformy `select` opcjonalny parametr `options` (zmiana w `components/samsung_nasa/select/__init__.py`, opisana w README). Bez `options` zachowanie się nie zmienia.
- **`error_code`.** Komponent dodaje filtr `delta: 1.0` (publikuje tylko przy zmianie kodu).
- **Ikony.** Czujniki temperatury i number mają ikonę `mdi:thermometer` (HA użyłby jej i tak jako domyślnej dla temperatury), a select `mdi:form-dropdown` zamiast domyślnej ikony HA.
- **`device_class: water`** przy `Flow` i temperaturach `Water Outlet Zone*` oraz jednostka `lpm` są zachowane z forka. HA może logować ostrzeżenie o niezgodnej jednostce dla tej klasy. Zmiana na `temperature` / `volume_flow_rate` nie zmienia `unique_id`, ale zmiana jednostki przy `Flow` wywoła komunikat o niezgodnych jednostkach statystyk.
- **Konfiguracja ESPHome.** `api: password` i `ota: password` (puste) usunięte. Bez klucza szyfrowania HA nie prosi o ponowne uwierzytelnienie. Wymagane ESPHome ≥ 2026.5. Komponent `samsung_ac` z `main` nie ładuje się na ESPHome 2026.x (`number.NUMBER_SCHEMA` usunięte).
- **Debug.** `debug_log_messages` i `debug_log_undefined_messages` zostały `true`, jak w Twoim pliku. `non_nasa_keepalive` nie istnieje (ten komponent obsługuje tylko NASA).

## Co sprawdziłem

- `esphome config` na ESPHome 2026.6.5: konfiguracja jest poprawna.
- Odciski wszystkich 14 encji (domena, `object_id`, klucz, jednostka, `device_class`, `state_class`, ikona, dokładność, kategoria, filtry, min/max/step, opcje, wiadomość) wyciągnięte ze źródła (ESPHome 2024.12.4 + komponent z `main`) i z celu. Pola są zgodne, poza różnicami wyżej.
- Klucze encji zapisane w wygenerowanym `main.cpp` (`esphome compile --only-generate`) są identyczne z kluczami policzonymi z nazw źródła (14/14).
- Zmiana w `select`: bez `options` bez zmian, zła liczba opcji i duplikaty dają czytelny błąd, `example.yaml` nadal przechodzi walidację.

Nie sprawdzone: kompilacja firmware do końca (pobieranie toolchaina przez proxy sesji się nie powiodło) i działanie na sprzęcie. Nie miałem dostępu do rejestru encji Twojego HA.

## Przed wgraniem

1. Dodaj do `secrets.yaml` `wifi_ssid` i `wifi_password`.
2. Wgraj na to samo ESP32 (ten sam MAC).
3. Po pierwszym połączeniu nie powinny pojawić się encje z sufiksem `_2`. Jeśli się pojawią, nazwa lub platforma różni się od starej.
4. Powrót do poprzedniego stanu: wgraj stary firmware (`esphome_samsung_hvac_bus.yaml` na ESPHome zgodnym z `samsung_ac`).

Po zmergowaniu gałęzi do `main` zmień `ref:` w `external_components` na `main`.

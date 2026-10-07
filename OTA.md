# Aktualizacja OTA działającego urządzenia (`samsung_hvac`)

Instrukcja przejścia z firmware `samsung_ac` na `samsung_nasa` bez rozkręcania urządzenia. Konfiguracja: [`samsung_hvac.yaml`](samsung_hvac.yaml), opis zmian: [`MIGRATION.md`](MIGRATION.md).

## Zanim zaczniesz

1. **Wymagane ESPHome ≥ 2026.5** (dodatek *ESPHome Device Builder* w HA lub CLI). Starsze nie zbudują tej konfiguracji.
2. **To samo Wi-Fi.** Firmware po OTA łączy się z siecią z `secrets.yaml`. Skopiuj `secrets.yaml.example` jako `secrets.yaml` i wpisz dane identyczne jak w obecnym firmware. Pliku `secrets.yaml` nie commituj (jest w `.gitignore`).
3. **Urządzenie działa i jest widoczne** w HA (Ustawienia → Urządzenia → ESPHome → `Samsung HVAC`). Zanotuj jego adres IP.
4. **Zachowaj możliwość powrotu.** Nie kasuj starego `esphome_samsung_hvac_bus.yaml` ani komponentu `samsung_ac` z `main`. Stary firmware zbudujesz tylko na starszym ESPHome (np. 2024.12), nie na 2026.x.
5. Pod ręką miej kabel USB do ATOM-a. To jedyny sposób odzyskania urządzenia, gdyby OTA się nie udało.

## Wariant A: dodatek ESPHome w Home Assistant

1. W dodatku ESPHome utwórz nową konfigurację i wklej zawartość `samsung_hvac.yaml`. Komponent pobierze się sam z GitHuba (`ref: claude/bold-tesla-l2fjw5`). Po zmergowaniu PR zmień `ref` na `main`.
2. W `secrets.yaml` dodatku wpisz `wifi_ssid` i `wifi_password`.
3. Kliknij **Validate**. Ma być „Configuration is valid”.
4. Kliknij **Install → Wirelessly**. Pierwsza kompilacja trwa kilka minut.
5. Poczekaj, aż urządzenie się zrestartuje i ponownie połączy z HA (do 2 min).

## Wariant B: CLI

```bash
git clone https://github.com/antrov/esphome-samsung-nasa && cd esphome-samsung-nasa
git checkout claude/bold-tesla-l2fjw5        # po zmergowaniu PR: main
cp secrets.yaml.example secrets.yaml         # i uzupełnij Wi-Fi
esphome config samsung_hvac.yaml             # walidacja
esphome run samsung_hvac.yaml --device <IP_URZADZENIA>   # kompilacja i OTA
```

Do kompilacji z lokalnych plików (zamiast pobierania z GitHuba) zmień w `external_components` źródło na `- source: components`.

## Po aktualizacji

1. Log urządzenia (HA → urządzenie → *Logi*, albo `esphome logs samsung_hvac.yaml`) powinien pokazać `Auto configured NASA device 20.00.00` i `10.00.00`, a po chwili `Discovered devices`.
2. W HA nie powinny pojawić się encje z sufiksem `_2`. Jeśli się pojawią, nazwa lub platforma różni się od starej (patrz `MIGRATION.md`).
3. Sprawdź, czy wartości napływają: `Outdoor temperature`, `Outdoor Instantaneous Power`, `Warm water`, `Hot Water Target Temperature`, `Hotwater Mode`.
4. Jeśli encje `0x4xxx` (`Warm water`, `Hot Water Target Temperature`, `Hotwater Mode`, `Flow`, `Water Outlet Zone 1/2`, `Threeway Valve on Tank`, `Heating Curve Shift`) są `unknown`, w logu szukaj linii `Undefined s:… d:… 0x4237 …`. Pokazują, z jakiego adresu faktycznie przychodzą wiadomości. Popraw `address:` urządzenia `nasa_device_1` w `samsung_hvac.yaml` i zainstaluj ponownie.
5. Gdy wszystko działa, wyłącz gadatliwe logi: `debug_log_messages: false` i `debug_log_undefined_messages: false`.

## Gdy coś pójdzie nie tak

| Objaw | Co robić |
|---|---|
| OTA kończy się błędem lub urządzenie nie wstaje | ESP32 po nieudanym starcie wraca do poprzedniego firmware (tryb awaryjny ESPHome). Poczekaj kilka minut. |
| Urządzenie wstało, ale nie ma go w sieci | Prawdopodobnie złe dane Wi-Fi. Połącz się z siecią `samsung_hvac` (punkt dostępowy), otwórz portal i wpisz właściwe dane, albo wgraj ponownie przez USB. |
| Błąd „firmware too large” przy OTA | Zbuduj najpierw minimalny firmware pośredni (np. samo `wifi`, `ota`, `api`), wgraj go OTA, a potem wgraj docelowy. |
| Trzeba wrócić do starego firmware | Zbuduj `esphome_samsung_hvac_bus.yaml` na ESPHome 2024.12 i wgraj przez OTA lub USB. Encje zachowają `unique_id` (te same nazwy). |

Wgranie przez USB (gdy OTA zawodzi): podłącz ATOM-a i uruchom `esphome run samsung_hvac.yaml --device /dev/ttyUSB0` (na Windows `COM3` itp.). Alternatywnie wgraj plik `firmware.factory.bin` z `.esphome/build/samsung_hvac/.pioenvs/samsung_hvac/` przez https://web.esphome.io.

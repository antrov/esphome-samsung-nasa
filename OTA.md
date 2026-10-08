# Aktualizacja OTA działającego urządzenia (`samsung_hvac`)

Instrukcja przejścia z firmware `samsung_ac` na `samsung_nasa` bez rozkręcania urządzenia. Konfiguracja: [`samsung_hvac.yaml`](samsung_hvac.yaml), opis zmian: [`MIGRATION.md`](MIGRATION.md).

## Zanim zaczniesz

1. **Wymagane ESPHome ≥ 2026.5** (dodatek *ESPHome Device Builder* w HA lub CLI). Starsze nie zbudują tej konfiguracji.
2. **To samo Wi-Fi.** Firmware po OTA łączy się z siecią z `secrets.yaml`. Skopiuj `secrets.yaml.example` jako `secrets.yaml` i wpisz dane identyczne jak w obecnym firmware. Pliku `secrets.yaml` nie commituj (jest w `.gitignore`).
3. **Urządzenie działa i jest widoczne** w HA (Ustawienia → Urządzenia → ESPHome → `Samsung HVAC`). Zanotuj jego adres IP.
4. **Zachowaj możliwość powrotu.** Nie kasuj starego `esphome_samsung_hvac_bus.yaml` ani komponentu `samsung_ac` z `main`. Stary firmware zbudujesz tylko na starszym ESPHome (np. 2024.12), nie na 2026.x.
5. Pod ręką miej kabel USB do ATOM-a. To jedyny sposób odzyskania urządzenia, gdyby OTA się nie udało.

## Wariant A: dodatek ESPHome w Home Assistant

1. W dodatku ESPHome utwórz nową konfigurację i wklej zawartość `samsung_hvac.yaml`. Komponent pobierze się sam z GitHuba (domyślna gałąź repozytorium).
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
| OTA kończy się błędem w trakcie wgrywania | Uszkodzony lub przerwany obraz nie zostaje uruchomiony, więc urządzenie dalej działa na starym firmware. Ponów OTA. |
| Firmware się wgrał, ale urządzenie restartuje się w pętli | Po kilku nieudanych startach ESPHome uruchamia tryb awaryjny (tylko Wi-Fi i OTA). Wgraj poprawny firmware przez OTA lub USB (sekcja niżej). |
| Urządzenie wstało, ale nie ma go w sieci | Prawdopodobnie złe dane Wi-Fi. Połącz się z siecią `samsung_hvac` (punkt dostępowy), otwórz portal i wpisz właściwe dane, albo wgraj ponownie przez USB. |
| Błąd „firmware too large” przy OTA | Zbuduj najpierw minimalny firmware pośredni (np. samo `wifi`, `ota`, `api`), wgraj go OTA, a potem wgraj docelowy. |
| Trzeba wrócić do starego firmware | Zbuduj `esphome_samsung_hvac_bus.yaml` na ESPHome 2024.12 i wgraj przez OTA lub USB. Encje zachowają `unique_id` (te same nazwy). |

Wgranie przez USB (gdy OTA zawodzi): podłącz ATOM-a i uruchom `esphome run samsung_hvac.yaml --device /dev/ttyUSB0` (na Windows `COM3` itp.). Alternatywnie wgraj plik `firmware.factory.bin` z `.esphome/build/samsung_hvac/.pioenvs/samsung_hvac/` przez https://web.esphome.io.

## Elementy konfiguracji, które przyjąłem bez weryfikacji

Nic z poniższego nie jest w stanie fizycznie uszkodzić ESP32. Najgorszy skutek to urządzenie niedostępne w sieci albo pętla restartów, a z obu da się wyjść przez USB (następna sekcja). Nie sprawdziłem żadnego z tych punktów na sprzęcie, a firmware nie został w tej sesji skompilowany do końca.

| Element | Założenie | Skutek, jeśli jest błędne |
|---|---|---|
| Dane Wi-Fi w `secrets.yaml` | Takie same jak w działającym firmware (nie mam ich) | Urządzenie nie łączy się z siecią i po chwili uruchamia punkt dostępowy `samsung_hvac` |
| Szyfrowanie API i hasło OTA | Brak (jak w Twoim `esphome_samsung_hvac_bus.yaml`, który miał puste hasła) | Jeśli działający firmware ma klucz API lub hasło OTA, OTA odrzuci hasło albo HA nie połączy się po aktualizacji i poprosi o ponowne uwierzytelnienie |
| Skok wersji ESPHome (2024.12 → 2026.6) i `framework: arduino` | OTA przez tak dużą różnicę przejdzie, a obraz zmieści się w partycji | Błąd „firmware too large” albo odrzucenie obrazu (urządzenie zostaje na starym firmware) |
| Adres jednostki dla wiadomości `0x4xxx` (`20.00.00`) | Dane CWU wysyła jednostka hydro, nie zewnętrzna | Encje CWU i obiegu są `unknown`, bez wpływu na ESP32 |
| Zapis do pompy (`Hot Water Target Temperature`, `Hotwater Mode`, `Heating Curve Shift`) | Zakresy i przeliczenia z komponentu są poprawne, także dla wartości ujemnych `Heating Curve Shift` | Nie dotyczy ESP32, ale pompa może dostać złą wartość. Przy pierwszym użyciu sprawdź na wyświetlaczu pompy, że ustawiona wartość się zgadza |
| Piny UART (`GPIO26`/`GPIO32`) i parzystość `EVEN` | Wzięte z Twojego pliku, zgodne z Tail485 | Brak danych z magistrali, urządzenie działa, ale encje nie dostają wartości |
| `debug_log_messages: true` | Logi aż tak nie obciążą pętli | Wolniejsze działanie lub opóźnienia. Wyłącz po sprawdzeniu |

## Odzyskiwanie urządzenia

Poziomy od najłatwiejszego:

1. **Zła sieć Wi-Fi.** Połącz się z siecią Wi-Fi `samsung_hvac`, otwórz portal (zwykle `192.168.4.1`) i wpisz właściwe dane. Albo popraw `secrets.yaml` i wgraj przez USB.
2. **Pętla restartów.** Po kilku nieudanych startach urządzenie wchodzi w tryb awaryjny. Wgraj poprawną konfigurację przez OTA (`esphome run samsung_hvac.yaml --device <IP>`).
3. **Brak połączenia z HA po OTA** (klucz API). Usuń urządzenie w HA i dodaj ponownie, albo wgraj konfigurację z kluczem, którego oczekuje HA.
4. **Wgranie przez USB** (zawsze działa, bo bootloader ROM układu ESP32 nie jest nadpisywany przez OTA):
   - Podłącz M5Atom Lite kablem USB-C do komputera.
   - `esphome run samsung_hvac.yaml --device /dev/ttyUSB0` (Linux/macOS: `/dev/ttyUSB0` lub `/dev/cu.usbserial-*`, Windows: `COM3` itp.). Jeśli ESPHome nie przełączy układu w tryb wgrywania, wejdź w niego ręcznie zgodnie z dokumentacją M5Stack (przytrzymanie przycisku przy podłączaniu).
   - Alternatywnie wgraj `firmware.factory.bin` przez https://web.esphome.io (Chrome lub Edge, przycisk *Connect*, potem *Install*). Plik leży w `.esphome/build/samsung_hvac/.pioenvs/samsung_hvac/`.
   - Ostateczność: *Erase* w web.esphome.io i wgranie od nowa. Kasuje zapisane ustawienia Wi-Fi, więc wgrywasz z `secrets.yaml`.
5. **Powrót do `samsung_ac`.** Zbuduj `esphome_samsung_hvac_bus.yaml` na ESPHome 2024.12 i wgraj przez USB lub OTA.

Przed OTA zrób **Validate** i kompilację w ESPHome. Jeśli się nie skompiluje, urządzenia to nie dotyczy, bo nic jeszcze nie zostało wgrane.

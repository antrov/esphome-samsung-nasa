# Katalog wpisów pompy ciepła (Samsung EHS / NASA)

Ten katalog opisuje **wszystko, co jest wystawione z pompy ciepła w `samsung_hvac.yaml`**: komunikaty NASA (rejestry), encje w Home Assistant, ustawienia serwisowe (FSV). Dla każdego wpisu znajdziesz nie tylko ID i nazwę, ale też: co to jest, w jakich jednostkach/wartościach, **na co wpływa** i skąd pochodzi ta wiedza.

> **Zasada utrzymania:** każda zmiana encji, komunikatu lub jego zachowania musi być odzwierciedlona w tym katalogu **w tym samym commicie**. Wymóg dla ludzi i agentów jest w [`AGENTS.md`](../AGENTS.md); spójność sprawdza `python3 tools/check_catalog.py`.

## Spis plików

| Plik | Zakres |
|---|---|
| [`control.md`](control.md) | Tryby pracy, tryb cichy, tryb wyjazdu, odniesienie temperatury, statusy ogólne (thermo, defrost) |
| [`zones.md`](zones.md) | Strefy 1 i 2: włączanie, temperatury zadane i pomiary wylotu, termostaty zewnętrzne, zawory, pompa obiegowa, krzywa grzewcza |
| [`dhw.md`](dhw.md) | Ciepła woda użytkowa (CWU): włączenie, tryb, temperatura zadana i w zasobniku, zawór 3-drożny, grzałka booster |
| [`hydraulics.md`](hydraulics.md) | Temperatury wody (wlot, wylot, grzałka, zawór mieszający), przepływ, temperatury czynnika na wymienniku płytowym |
| [`outdoor-unit.md`](outdoor-unit.md) | Jednostka zewnętrzna: stan pracy, sprężarka, zawory, defrost, czujniki obiegu chłodniczego, falownik, wentylator |
| [`energy-diagnostics.md`](energy-diagnostics.md) | Moc i energia (pobór, produkcja ciepła, COP), napięcie i prąd, liczniki życia urządzenia, kody błędów |
| [`fsv.md`](fsv.md) | Ustawienia serwisowe FSV wystawione w YAML (limity 10xx, termostaty 20xx, CWU 30xx, strefy 40xx, wyjazd 50xx) |
| [`unused.md`](unused.md) | Czego **nie** ma w YAML: komunikaty widziane na magistrali, gotowe w komponencie FSV-y (kandydaci), ustawienia bez znanego komunikatu |

## Jak czytać tabele

Każdy wiersz = **jeden komunikat NASA** (jedno ID). Jeśli ten sam komunikat jest wystawiony jako kilka encji (np. `0x4067` jako sensor, binary_sensor i text_sensor), wszystkie encje są wymienione w jednym wierszu.

| Kolumna | Znaczenie |
|---|---|
| **ID** | Numer komunikatu NASA (`0x4235`) i urządzenie: **IN** = jednostka wewnętrzna / Control Kit `20.00.00` (`nasa_device_1`), **OUT** = jednostka zewnętrzna `10.00.00` (`nasa_device_2`) |
| **Encja** | Dokładna nazwa w YAML/HA w apostrofach (od niej zależy `unique_id` w HA – nie zmieniaj, patrz [`MIGRATION.md`](../MIGRATION.md)) i platforma. *number*, *select*, *switch* = odczyt i zapis; *sensor*, *binary_sensor*, *text_sensor* = tylko odczyt |
| **Wartości** | Jednostka, skala po stronie komponentu, zakres/opcje; pod spodem `log:` = przykładowa wartość z zapisu 08.10.2026 |
| **Co to jest** | Znaczenie komunikatu |
| **Na co wpływa, uwagi** | Skutki zmiany lub interpretacji, powiązane FSV i komunikaty, pułapki |
| **Źr.** | Skąd pochodzi opis (poniżej) |

### Tagi źródeł (kolumna „Źr.")

| Tag | Źródło | Wiarygodność |
|---|---|---|
| **M** | Instrukcja Samsunga do sterownika przewodowego / Control Kit – [`MIM-E03EN.pdf`](../MIM-E03EN.pdf), str. 6–46 | wysoka (producent) |
| **P** | Lista kodów NASA – [`samsung_nasa_protocol.md`](../samsung_nasa_protocol.md) / [`NASA.pdf`](../NASA.pdf) (nieoficjalna, od społeczności) | średnia; część nazw to tylko `??` |
| **K** | Kod komponentu: rejestry w [`components/samsung_nasa/nasa/*.py`](../components/samsung_nasa/nasa) (skalowanie, zakresy, mapowania tekstów) | pewna co do tego, *co robi komponent* |
| **L** | Obserwacja w logu ESPHome z 08.10.2026 (21:48–21:53, instalacja właściciela) | fakt, ale pojedyncza próbka z 5 minut |
| **W** | Wnioskowanie / hipoteza – spójne z danymi, lecz niepotwierdzone dokumentacją | niska; do weryfikacji |

### O wartościach „log"

Wartości oznaczone `log:` pochodzą z jednego, pięciominutowego zapisu z 08.10.2026 (pompa grzała strefę 1, w trakcie zmieniano ustawienia stref, na końcu zasobnik CWU). To **przykłady i migawka konfiguracji**, nie wartości stałe. Brak próbki (`brak próbek`) znaczy tylko, że komunikat nie pojawił się w tym oknie (np. wysyłany rzadko lub nieobsługiwany przez ten model). Aby odświeżyć przykłady, zbierz nowy zapis (`esphome logs samsung_hvac.yaml`), podsumuj go skryptem [`tools/collect_logs.py`](../tools/collect_logs.py) (opcja `--from-file`) i zaktualizuj w katalogu wartości oraz datę.

### Domyślne wartości FSV

Domyślne wartości FSV w [`fsv.md`](fsv.md) pochodzą z kolumny instrukcji dla **MIM-E03CN / MIM-E03EN / AE\*\*\*CXYB\*G** (Control Kit). Jednostki hydrauliczne R32 (AE\*\*\*RNW/CNW) mają w kilku miejscach inne domyślne (np. FSV 3011, 3022, 3031, 3043).

## Znane problemy i niejasności

Obserwacje, które warto znać, zanim zaufasz konkretnej encji (szczegóły przy właściwych wierszach):

1. **Czujniki bez danych zwracają „śmieci".** Jednostka wysyła `65535` (0xFFFF = brak czujnika) lub `65036` (= −50,0 °C jako int16) tam, gdzie nie ma czujnika. Encje `High pressure` i `Low pressure` (≈ 642 679 kPa) oraz `TW1 sensor reading` i `TW2 sensor reading` (−50 °C) **usunięto z YAML 08.10.2026** (powód i opisy: [`unused.md`](unused.md)). Nadal wystawione, ale bez danych w tym modelu (pokazują −0,1 °C): `0x821A` temperatura ssania oraz `0x829F` i `0x82A0` temperatury nasycenia – do usunięcia, jeśli przeszkadzają.
2. **Nazwy encji.** Mylące nazwy poprawiono 08.10.2026 (lista starych i nowych: [`MIGRATION.md`](../MIGRATION.md), sekcja „Zmiany po migracji"; w wierszach katalogu stara nazwa jest podana jako „Wcześniej…"). Zostawione celowo, bo ich zmiana tworzy nowe encje w HA bez powodu merytorycznego: literówka „Compresor" w nazwach `0x820A` i `0x821A` oraz dwie spacje w `Silence mode  On/Off control`. `Zone 2 room temperature` (`0x42D4`) w tej instalacji pokazuje temperaturę wody, nie pokoju, ale nazwa odpowiada znaczeniu komunikatu.
3. **`device_class: water` przy °C / lpm.** Trzy czujniki ustawione bezpośrednio w YAML (`Flow`, `Water Outlet Zone 1/2`) mają `device_class: water`, który w HA oznacza objętość wody; HA może ostrzegać o niezgodnej jednostce. Odziedziczone z poprzedniej konfiguracji – decyzja o zmianie wymaga przeczytania [`MIGRATION.md`](../MIGRATION.md).
4. **`0x42CE` (FSV 3046) – niezgodna jednostka.** Jednostka zgłasza minuty (w logu 480 = 8 h), a definicja w `numbers.py` zakłada godziny 1–24; dlatego encja nie jest wystawiona (patrz [`unused.md`](unused.md)).
5. **`0x823B` i `0x42E8`.** Wartości po przeskalowaniu (150–170 „V" DC link, 17–20 „V" czujnika przepływu) wyglądają na niezgodne ze skalą/etykietą – traktuj jako wskaźniki względne.
6. **`0x8240` – kW czy %?** Lista kodów mówi „wartość w procentach", komponent przelicza ×0,1 jako kW; brak próbek w logu.
7. **`0x8061` – różne mapowania.** Lista kodów podaje inne wartości (255 = brak defrostu) niż komponent (0 = brak); w logu było 0, więc mapowanie komponentu zgadza się z obserwacją.

## Źródła i ograniczenia

- Główne źródła to instrukcja producenta w repo (**M**), lista kodów NASA (**P**), kod komponentu (**K**) i log (**L**).
- Przy tworzeniu katalogu (08.10.2026) nie udało się pobrać stron zewnętrznych: środowisko sesji blokowało hosty (m.in. `community.openenergymonitor.org`, `*.samsung.com`, `en.wikipedia.org`), a wyszukiwanie ogólne nie zwróciło opisów konkretnych komunikatów. Opisy bez tagu **M** należy więc traktować jako dobrze uzasadnione, ale nieweryfikowane u producenta. Uzupełnienia z dokumentacji serwisowej Samsunga są mile widziane – dodaj je ze źródłem.
- Ogólne wyjaśnienia działania (np. obieg chłodniczy, falownik) to wiedza ogólna o pompach ciepła, oznaczona **W**, gdy dotyczy interpretacji konkretnego czujnika.

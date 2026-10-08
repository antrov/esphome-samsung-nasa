# Czego nie ma w YAML (kandydaci i ślepe zaułki)

Ten plik **nie opisuje używanych encji** – służy do decyzji, co jeszcze warto wystawić. Gdy dodasz któryś z poniższych komunikatów do `samsung_hvac.yaml`, **przenieś jego wiersz** do właściwego pliku tematycznego (zob. [`README.md`](README.md)) i uzupełnij pełny opis. Skrypt `tools/check_catalog.py` pilnuje, żeby ID nie występowało jednocześnie tutaj i w YAML.

## A. Widziane na magistrali w logu 08.10.2026, bez encji

Kolumna „Nazwa NASA" to nazwa z listy kodów ([`samsung_nasa_protocol.md`](../samsung_nasa_protocol.md)); `??` znaczy, że nazwa nie jest znana. Interpretacje to hipotezy (**W**). Wiersze z adnotacją „usunięta z YAML" to encje świadomie wycofane, bo ten model nie dostarcza danych.

| ID | Nazwa NASA | Wartości w logu | Uwagi i hipoteza |
|---|---|---|---|
| `0x4059`<br>IN | `ENUM_IN_??` | 1 → 0 o 21:49:55 | Zmieniło się w tej samej sekundzie, gdy wyłączono strefę 1 (`0x4000`) i zawór 3-drożny poszedł na zbiornik. Możliwe: żądanie/stan ogrzewania strefy 1 (thermo strefy 1). Do potwierdzenia testem: włączać/wyłączać strefę 1 przy strefie 2 w tle. |
| `0x4211`<br>IN | `VAR_IN_CAPACITY_REQUEST` | 51 | Lista kodów: „kW, dzielenie przez 8,6" → ok. 5,9 kW zapotrzebowania na moc. Ciekawe do porównania z `0x4426`. |
| `0x4212`<br>IN | `VAR_IN_CAPACITY_ABSOLUTE` | 51 | Jak wyżej – wartość bezwzględna. |
| `0x420C`<br>IN | `NASA_INDOOR_OUTER_TEMP` | 15,4–15,6 °C (÷10) | Kopia temperatury zewnętrznej (`0x8204`) po stronie jednostki wewnętrznej. Zbędna, gdy jest `0x8204`. |
| `0x4229`<br>IN | `VAR_IN_MODEL_INFORMATION` | 115 | Kod modelu/informacji o jednostce wewnętrznej; wartości nie da się zinterpretować bez tablicy producenta. |
| `0x42CE`<br>IN | `VAR_IN_FSV_3046` | 480 | FSV 3046 (maks. czas dezynfekcji). Jednostka zgłasza **minuty** (480 = 8 h = wartość domyślna), a definicja w `numbers.py` zakłada godziny 1–24 – przed wystawieniem trzeba poprawić skalowanie (÷60 / ×60). |
| `0x8229`<br>OUT | `VAR_OUT_LOAD_OUTEEV1` | 480 → 376 → 0 → 159 → 176 → 189 → 206 | Położenie głównego zaworu rozprężnego EEV1 (kroki); po starcie sprężarki otwierał się stopniowo. Przydatne do diagnostyki obiegu. |
| `0x82DB`<br>OUT | `VAR_OUT_PHASE_CURRENT` | 0, 5–9 | Prąd fazowy falownika (jednostka niepotwierdzona). |
| `0x8248`<br>OUT | `NASA_OUTDOOR_SAFETY_START` | 6 → 3 → 0 → 1 → 2 | Numer kroku sekwencji bezpiecznego rozruchu (zbiega się z `0x8001` = 1 Safety). |
| `0x8247`<br>OUT | `NASA_OUTDOOR_DEFROST_STEP` | 0 | Krok odszraniania po stronie jednostki zewnętrznej (porównaj `0x8061`). |
| `0x800D`<br>OUT | `ENUM_OUT_STATE_FAN_OPER` | 0 → 1 o 21:49:25 | Wentylator jednostki zewnętrznej w pracy. Jest gotowy w komponencie jako `text_sensor`, ale nie dodany do YAML. |
| `0x82DE`<br>OUT | `NASA_OUTDOOR_EVA_IN` | 65036 (−50 °C) | Gotowy `sensor` w komponencie; ten model nie dostarcza wartości – nie ma sensu go dodawać. |
| `0x8206`<br>OUT | `VAR_OUT_SENSOR_HIGHPRESS` | 65535 | Ciśnienie po stronie tłoczenia. Encja `High pressure` **usunięta z YAML 08.10.2026**: model nie raportuje (0xFFFF = brak czujnika), po przeliczeniu (× 9,80665) w HA wychodziło ≈ 642 679 kPa. Wracaj do niej tylko, gdy jednostka zacznie wysyłać realne wartości. Błędy 291/407/507 dotyczą wysokiego ciśnienia. |
| `0x8208`<br>OUT | `VAR_OUT_SENSOR_LOWPRESS` | 65535 | Ciśnienie po stronie ssania. Encja `Low pressure` **usunięta z YAML 08.10.2026** z tego samego powodu co `0x8206`. Błędy 296/410/443 dotyczą niskiego ciśnienia. |
| `0x82DF`<br>OUT | `VAR_OUT_SENSOR_TW1` | 65036 (−50 °C) | Temperatura wody „TW1" z jednostki zewnętrznej (protokół: `Water In 1 for EHS`). Encja `TW1 sensor reading` **usunięta z YAML 08.10.2026**: stała 65036 = −50 °C. README forka podaje, że na innych modelach jest równa `0x4238` (wylot), choć nazwa z protokołu sugeruje wlot – numeracja TW1/TW2 bywa niespójna. Użyj `0x4236`/`0x4238`. |
| `0x82E0`<br>OUT | `VAR_OUT_SENSOR_TW2` | 65036 (−50 °C) | Temperatura wody „TW2" z jednostki zewnętrznej (protokół: `Water In 2 for EHS`). Encja `TW2 sensor reading` **usunięta z YAML 08.10.2026** z tego samego powodu co `0x82DF` (README forka: na innych modelach równa `0x4236`, czyli powrotowi). |

Inne nieopisane komunikaty, które zmieniły się przy starcie sprężarki: `0x8032` (255 → 18), `0x8033` (0 → 1), `0x805E` (0 → 1), `0x4401` (15 → 93), `0x8239` (95 → 56). Bez dokumentacji nie warto ich wystawiać.

## B. Gotowe w komponencie (FSV), ale bez encji w YAML

Wszystkie poniższe mają już definicje w `components/samsung_nasa/nasa/*.py`; wystarczy dodać wpis z `message: 0x…` lub `fsv: NNNN`. Opisy według instrukcji ([**M**](../MIM-E03EN.pdf), kolumna MIM-E03EN; domyślne · zakres). Nie były w logu 08.10.2026 – wartości nieznane.

| ID | FSV · typ | Co ustawia (domyślnie · zakres) |
|---|---|---|
| `0x4254`<br>IN | 2011 · number | Krzywa grzewcza: dolny punkt temperatury zewnętrznej (zimno) (−10 · −20…5 °C) |
| `0x4255`<br>IN | 2012 · number | Krzywa grzewcza: górny punkt temperatury zewnętrznej (ciepło) (15 · 10…20 °C) |
| `0x4256`<br>IN | 2021 · number | WL1 (podłogówka): woda przy dolnym punkcie / zimno (40 · 17…65/70/75 °C) |
| `0x4257`<br>IN | 2022 · number | WL1: woda przy górnym punkcie / ciepło (25 · 17…65/70/75 °C) |
| `0x4258`<br>IN | 2031 · number | WL2 (FCU/grzejniki): woda przy zimnie (50 · 17…65/70/75 °C) |
| `0x4259`<br>IN | 2032 · number | WL2: woda przy cieple (35 · 17…65/70/75 °C) |
| `0x4093`<br>IN | 2041 · select | Typ krzywej grzewczej, gdy nie ma 2 stref ani termostatu: 1 WL1, 2 WL2 (1 · 1…2) |
| `0x425A`<br>IN | 2051 · number | Krzywa chłodzenia: dolny punkt temperatury zewnętrznej (30 · 25…35 °C) |
| `0x425B`<br>IN | 2052 · number | Krzywa chłodzenia: górny punkt temperatury zewnętrznej (40 · 35…45 °C) |
| `0x425C`<br>IN | 2061 · number | WL1 chłodzenie: woda przy dolnym punkcie (25 · 5…25 °C) |
| `0x425D`<br>IN | 2062 · number | WL1 chłodzenie: woda przy górnym punkcie (18 · 5…25 °C) |
| `0x425E`<br>IN | 2071 · number | WL2 chłodzenie: woda przy dolnym punkcie (18 · 5…25 °C) |
| `0x425F`<br>IN | 2072 · number | WL2 chłodzenie: woda przy górnym punkcie (5 · 5…25 °C) |
| `0x4094`<br>IN | 2081 · select | Typ krzywej chłodzenia: 1 WL1, 2 WL2 (1 · 1…2); nie schodź WL1 poniżej 16 °C (kondensacja na podłodze) |
| `0x42ED`<br>IN | 3081 · number | Moc 1. stopnia grzałki backup do liczenia energii (2 · 1…6 kW) |
| `0x42EE`<br>IN | 3082 · number | Moc 2. stopnia grzałki backup (2 · 0…6 kW) |
| `0x42EF`<br>IN | 3083 · number | Moc grzałki booster (3 · 1…6 kW) |
| `0x409E`<br>IN | 4011 · select | Priorytet: 0 CWU, 1 ogrzewanie (tylko poniżej progu FSV 4012) (0) |
| `0x426D`<br>IN | 4012 · number | Temperatura zewnętrzna, poniżej której priorytet ma ogrzewanie (0 · −15…20 °C) |
| `0x426E`<br>IN | 4013 · number | Temperatura zewnętrzna wyłączająca ogrzewanie w cieple dni (35/45 · 10…35/45 °C) |
| `0x409F`<br>IN | 4021 · select | Grzałka backup: 0 brak, 1 dwustopniowa, 2 jednostopniowa (0) |
| `0x40A0`<br>IN | 4022 · select | Priorytet grzałek: 0 obie, 1 backup, 2 booster (0) |
| `0x40A1`<br>IN | 4023 · switch | Kompensacja zimna: grzałka backup tylko poniżej progu FSV 4024 (Tak) |
| `0x4270`<br>IN | 4024 · number | Próg temperatury zewnętrznej dla grzałki backup (0 · −25…35 °C) |
| `0x4271`<br>IN | 4025 · number | Próg temperatury wody, poniżej którego grzałka backup pracuje w trakcie defrostu (15 · 10…55 °C) |
| `0x40A2`<br>IN | 4031 · switch | Zewnętrzny kocioł jako dodatkowe źródło ciepła (Nie) |
| `0x40A3`<br>IN | 4032 · switch | Priorytet kotła nad pompą ciepła (Nie) |
| `0x4272`<br>IN | 4033 · number | Temperatura zewnętrzna, poniżej której pracuje kocioł zamiast pompy (−15 · −20…5 °C) |
| `0x40C0`<br>IN | 4041 · select | Zawór mieszający: 0 brak, 1 wg ΔT, 2 wg krzywej (0) |
| `0x4286`<br>IN | 4042 · number | Docelowe ΔT zaworu mieszającego, grzanie (10 · 5…15 °C) |
| `0x4287`<br>IN | 4043 · number | Docelowe ΔT zaworu mieszającego, chłodzenie (10 · 5…15 °C) |
| `0x40C1`<br>IN | 4044 · number | Współczynnik regulacji zaworu mieszającego (2 · 1…5) |
| `0x4288`<br>IN | 4045 · number | Interwał regulacji zaworu mieszającego (2 · 1…30) |
| `0x4289`<br>IN | 4046 · number | Czas pełnego przebiegu zaworu mieszającego (9 · 6…24, krok 3) |
| `0x40C2`<br>IN | 4051 · select | Pompa inwerterowa: 0 brak, 1 użycie + wyjście 100 %, 2 użycie + 70 % (1) |
| `0x428A`<br>IN | 4052 · number | Docelowa różnica Tw2−Tw1 pompy inwerterowej (5 · 2…8 °C) |
| `0x40C3`<br>IN | 4053 · number | Współczynnik zmian PWM pompy (2 · 1…3) |
| `0x427C`<br>IN | 5021 · number | O ile obniżyć cel CWU w trybie Economic (5 · 0…40 °C) |
| `0x42F0`<br>IN | 5023 · number | Temperatura włączenia grzania CWU w trybie oszczędnym (25 · 0…40 °C) |
| `0x40A4`<br>IN | 5041 · switch | Sterowanie szczytem mocy (Power Peak Control) – wymuszone wyłączenie wg styku (Nie) |
| `0x40A5`<br>IN | 5042 · select | Co wyłączać przy styku szczytu: 0 grzałkę backup · 1 backup + booster · 2 backup + sprężarkę · 3 wszystko (0) |
| `0x40A6`<br>IN | 5043 · select | Aktywny poziom napięcia na wejściu szczytu: 1 wysoki, 0 niski (1) |
| `0x40A7`<br>IN | 5051 · switch | Frequency Ratio Control – ograniczenie częstotliwości sprężarki sygnałem 0–10 V lub Modbus DR; pokazuje „DR" na sterowniku (Nie) |
| `0x411B`<br>IN | 5081 · switch | Sterowanie PV (fotowoltaika) – podbicie/obniżenie nastaw (Nie); nie łączyć ze sterowaniem szczytem mocy |
| `0x42DB`<br>IN | 5082 · number | Przesunięcie nastaw przy PV, chłodzenie (2 · 1…20 °C) |
| `0x42DC`<br>IN | 5083 · number | Przesunięcie nastaw przy PV, grzanie (2 · 1…50 °C) |
| `0x411C`<br>IN | 5091 · switch | Smart Grid (SG Ready) – 4 tryby wg dwóch styków (Nie) |
| `0x42DD`<br>IN | 5092 · number | Smart Grid: podbicie nastaw grzania (2 · 1…50 °C) |
| `0x42DE`<br>IN | 5093 · number | Smart Grid: podbicie nastawy CWU (5 · 1…40 °C) |
| `0x411D`<br>IN | 5094 · switch | Smart Grid, tryb 4: cel CWU 0 = wg FSV 3021, 1 = 70 °C (0) |

## C. Ustawienia z instrukcji bez encji w komponencie

Brak znanego komunikatu NASA w rejestrach komponentu (część ma wpis w liście kodów, ale bez definicji); da się je zmienić tylko na sterowniku przewodowym.

| Ustawienie | Co robi | Uwagi |
|---|---|---|
| **FSV 4062 / 4063** | Zachowanie pompy/zaworu 2-drożnego strefy 1 / 2 przy *thermo OFF*: 0 pompa wyłączona · 1 włączona · **2 cykl 7 min wył. / 3 min wł. (domyślnie)** | Wyjaśnia, dlaczego po wyłączeniu stref pompa obiegowa „na chwilę" się załącza ([`zones.md`](zones.md)). |
| **FSV 1061–1064** | Histereza thermo: woda grzanie · woda chłodzenie · pokój grzanie · pokój chłodzenie (domyślnie 0 · 1 · 0 · 1; zakres 0–7 °C) | Większa histereza = rzadsze starty sprężarki, większe wahania temperatury. |
| **FSV 4054** | Minimalne wyjście PWM pompy: 0 → 25 %, 1 → 35 %, 2 → 45 %, 3 → 55 % | Dopełnienie FSV 4051–4053 (`0x40C4`). |
| **FSV 5031 / 5032 / 5033** | Instalacje A2A + A2W (klimatyzatory + hydro): maks. czas priorytetu A2A (30 min), min. czas bez priorytetu (5 min), priorytet 0 A2A / 1 CWU | Wiadomości `0x427D`, `0x427E`, `0x4107` są w liście kodów, ale nie w rejestrach komponentu. |
| **FSV 6022** | Minimalny czas pracy po starcie jednostki zewnętrznej (5 · 5…30 min) | Ogranicza zbyt częste starty sprężarki. |
| **FSV 6031** | Opcjonalne wyłączanie jednostki zewnętrznej przy długiej pracy na niskiej częstotliwości w grzaniu (Tak) | Podnosi efektywność, ale zmienia cykle pracy. |
| **FSV 6041** | Typ sterowania przy termostacie: 0 zawór 2-drożny · 1 pompa wtórna | Zależy od hydrauliki. |
| **FSV 3046** (`0x42CE`) | Maksymalny czas dezynfekcji (8 h · 1…24 h) | Komunikat jest w komponencie, ale z błędnym skalowaniem – zob. sekcja A. |
| Funkcje sterownika (nie FSV) | Okno „Quiet Mode Automatic Time", kalibracja czujnika pokojowego, harmonogramy (dzienny/tygodniowy/roczny/święta), **Energy → Target Energy Consumption / Target Operation Time + alarm**, wybór „Cool & Heat / Heat only", wybór strefy, odniesienie temperatury | Cele energii i czasu pracy (dzienne/tygodniowe limity i alarmy) to funkcja samego sterownika przewodowego – nie ma dla niej komunikatu NASA, więc z HA jej nie ustawisz. |

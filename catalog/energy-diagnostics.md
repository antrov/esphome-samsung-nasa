# Energia, zasilanie i diagnostyka

Pobór prądu, produkcja ciepła (do liczenia COP), parametry zasilania jednostki zewnętrznej, liczniki życia urządzenia i kody błędów. Legenda kolumn i tagów źródeł: [`README.md`](README.md). Czujniki obiegu chłodniczego i falownika: [`outdoor-unit.md`](outdoor-unit.md).

## Jak policzyć COP z tych wpisów

- **COP chwilowy** ≈ `0x4426` ÷ `0x8413` (moc cieplna oddana ÷ moc elektryczna, oba w W). Wartości odświeżają się w różnych momentach i przy rozruchu mocno „skaczą", więc sensowny jest raczej wynik uśredniony. W `samsung_hvac.yaml` nie ma takiego czujnika.
- **COP skumulowany** ≈ `0x4427` ÷ `0x8414` (kWh ÷ kWh). W chwili zapisu logu: 48 580,4 kWh ÷ 17 151,8 kWh ≈ **2,83** (licznik życiowy od instalacji, w tym CWU i ogrzewanie). W `samsung_hvac.yaml` nie ma takiego czujnika.
- **COP godzinowy i dzienny** nie są liczone w ESPHome (usunięte 11.10.2026): właściciel liczy je w Home Assistant z liczników `0x4427` i `0x8414`.
- **Grzałka booster jest wliczana po obu stronach.** Gdy pracuje (`0x4087` = On), pompa dolicza ok. 3,1 kW do poboru (`0x8413`, `0x8414`) i ok. 3,1–3,2 kW do ciepła (`0x4426`, `0x4427`) – log 08.11.2026, godzina z grzałką: licznik `0x8414` +5,84 kWh przy 2,69 kWh z `0x8411`; licznik `0x4427` +6,97 kWh przy 3,87 kWh policzonych z przepływu i ΔT. COP z tych liczników jest więc wtedy średnią sprężarki i grzałki. **COP samej sprężarki** = moc cieplna z `0x42E9` × ΔT (zob. [`hydraulics.md`](hydraulics.md)) ÷ `0x8411`.
- Licznik `0x8414` nie obejmuje pomp obiegowych ani grzałki backup zmierzonych osobno – poza grzałką booster (wyżej) liczy jednostkę zewnętrzną. Energię grzałek i pomp szacuje sama pompa na podstawie FSV 3081–3083 (zob. [`unused.md`](unused.md)); instrukcja zastrzega, że pomiary produktu mogą różnić się od rzeczywistego zużycia.

## Wpisy

| ID | Encja | Wartości | Co to jest | Na co wpływa, uwagi | Źr. |
|---|---|---|---|---|---|
| `0x8413`<br>OUT | `Outdoor Instantaneous Power` *(sensor)* | W<br>log: **15–1745**<br>log 07–09.11.2026: **14–6100** | Chwilowa moc elektryczna – suma modułów (`LVAR_OUT_CONTROL_WATTMETER_1W_1MIN_SUM`). | Dla Home Assistant: moc urządzenia (`device_class: power`). Rośnie z częstotliwością sprężarki (`0x8238`). **Zawiera grzałkę booster**: 08.11.2026, gdy grzałka pracowała (`0x4087` = On), wskazanie było o ok. 3,1 kW wyższe niż `0x8411` (6,0 vs 2,9 kW przy prądzie sprężarki 12,4 A). To samo dotyczy licznika `0x8414` oraz ciepła `0x4426` i `0x4427`. Skąd pompa bierze moc grzałki, nie wiadomo – możliwe, że z FSV 3083 (domyślnie 3 kW); potwierdzi to odczyt FSV 3083. Lista kodów mówi o odświeżaniu co ok. 30 s; w logu co ok. 44 s. | P K L W |
| `0x8411`<br>OUT | `Outdoor unit inst. power consumed` *(sensor)* | W<br>log: **0–1652**<br>log 07–09.11.2026: **0–2970** | Moc chwilowa pojedynczej jednostki zewnętrznej (`WATTMETER_1UNIT`). | Moc samej jednostki zewnętrznej (sprężarka, wentylator, elektronika). Równa `0x8413`, dopóki nie pracuje grzałka booster; z grzałką `0x8413` jest wyższe o ok. 3,1 kW (log 08.11.2026). Jedyny odczyt mocy bez grzałki – do COP samej sprężarki dziel przez niego moc cieplną policzoną z przepływu i ΔT. Lista kodów: „not used by the controller", odświeżany rzadziej. | P K L |
| `0x8414`<br>OUT | `Outdoor Cumulative Energy` *(sensor)* | kWh (surowo Wh × 0,001), `total_increasing`<br>log: **17 151,826 → 17 151,889** | Skumulowane zużycie energii elektrycznej jednostki zewnętrznej (`WATTMETER_ALL_UNIT_ACCUM`). | Nadaje się do panelu Energia w HA. Jednostka zewnętrzna plus grzałka booster, gdy pracuje (log 08.11.2026: +3,15 kWh w godzinie z grzałką ponad to, co wynika z `0x8411`). Mianownik skumulowanego COP (COP godzinowy i dzienny liczy właściciel w Home Assistant). Czujnik ma w YAML `id: heat_pump_cumulative_energy` – potrzebne temu wyliczeniu. | P K L |
| `0x8217`<br>OUT | `Outdoor Current` *(sensor)* | A (surowo × 0,1)<br>log: **0 → 7,9**<br>log 07–09.11.2026: **0–16,0** | Prąd sprężarki 1 (`SENSOR_CT1`; w YAML „Outdoor Current"). | Rośnie z obciążeniem; 230 V × 7,9 A ≈ 1,8 kW, zgodnie z `0x8413`. Błędy 462/464/485 dotyczą nadprądów i czujnika prądu. W zapisie 07–09.11.2026 normalna praca do ok. 13,4 A; oba błędy 462 poprzedził skok prądu w kilkanaście sekund przy stałej częstotliwości (10,9 → 13,4 A przy 81 Hz; 12,1 → 16,0 A przy 74 Hz). Błędy 464 przy nieudanych rozruchach zapisały się przy 0–1,1 A, bo próbka co ok. 11–22 s nie łapie krótkiego impulsu. | P K L |
| `0x24FC`<br>OUT | `Outdoor Voltage` *(sensor)* | V<br>log: **212–215**<br>log 07–09.11.2026: **199–221**, mediana 212 | Napięcie zasilania mierzone przez jednostkę zewnętrzną (`LVAR_NM_OUT_SENSOR_VOLTAGE`). | Do monitorowania jakości zasilania. Błędy 466/483/488 dotyczą nad-/podnapięć i czujnika napięcia. W zapisie 07–09.11.2026 napięcie **nie spadało z obciążeniem** (średnio 211 V przy 0 A i 213–214 V przy 10–16 A), więc nie widać słabego styku ani przeciążonej linii; odczyty 199–202 V wystąpiły tylko trzy razy, zawsze w pierwszych minutach po ponownym połączeniu ESP. Mediana 212 V to ok. 8 % poniżej 230 V – dokładność pomiaru jednostki nieznana, warto porównać z miernikiem. | P K L W |
| `0x4284`<br>IN | `Indoor unit power consumption` *(sensor)* | W<br>log: brak próbek | Moc pobierana przez jednostkę wewnętrzną (`NASA_INDOOR_POWER_CONSUMPTION`). | Ten model prawdopodobnie jej nie raportuje. Dokładność zależy od FSV 3081–3083 (moce grzałek). | P K |
| `0x4426`<br>IN | `Heat pump produced power (last minute)` *(sensor)* | W (int16)<br>log: **0 → 3990 → 2630 → 4031** | Moc cieplna oddana przez pompę w ostatniej minucie (`LVAR_IN_4426`). Wcześniej nazywana `Heat pump produced energy (last minute)` – nazwa myliła, bo jednostką jest wat, nie kWh. | Licznik własny pompy; licznik COP chwilowego (zob. wyżej). Spada do 0 przy postoju i podczas odszraniania. Bez grzałki zgadza się z mocą policzoną z przepływu i ΔT (log 07–09.11.2026: różnica do 3 %); z pracującą grzałką booster jest o ok. 3,1–3,2 kW wyższy. | P K L |
| `0x4427`<br>IN | `Heat pump produced energy (total)` *(sensor)* | kWh (surowo Wh × 0,001), `total_increasing`<br>log: **48 580,404 → 48 580,580** | Skumulowana energia cieplna oddana przez pompę od instalacji (`LVAR_IN_4427`). | Licznik życiowy ciepła (CWU + ogrzewanie); licznik COP skumulowanego (wyżej) oraz COP godzinowego i dziennego (`COP - Hourly`, `COP - Daily`). Pomiar produktu – może odbiegać od licznika ciepła. Czujnik ma w YAML `id: heat_pump_produced_energy` – potrzebne temu wyliczeniu. | P K L |
| `0x4423`<br>IN | `Days since installation` *(sensor)* | dni (surowo minuty ÷ 1440)<br>log: **1616,6 d** (2 327 872 min ≈ 4,4 roku) | Czas od daty instalacji wpisanej w menu serwisowym (`LVAR_IN_MINS_SINCE_INST`). | Informacyjnie (gwarancja, przeglądy). Nie wpływa na sterowanie. | P K L |
| `0x4424`<br>IN | `Hours active since installation` *(sensor)* | godziny (surowo minuty ÷ 60)<br>log: **17 329 h** (1 039 743 min) | Czas aktywnej pracy od instalacji (`LVAR_IN_MINS_ACTIVE_SINCE_INST`). | Informacyjnie; ok. 45 % czasu od instalacji (porównaj `0x4423`). Nie wpływa na sterowanie. | P K L |
| `0x8235`<br>OUT | `error_code` *(sensor)*<br>`Error description (text)` *(text_sensor)* | liczba = numer błędu (0 = brak), text: opis; 91 kodów w komponencie, inne → „Unknown (N)"<br>log: **0**<br>log 07–09.11.2026: **0, 416, 462, 464** | Aktywny kod błędu układu (`VAR_OUT_ERROR_CODE`) – ten sam numer, co „Exxx" na sterowniku. Sensor ma kategorię *diagnostic* i publikuje tylko zmiany. | Przydatne do powiadomień. Kody związane z hydrauliką: 911 niski przepływ, 913 wyłącznik przepływu, 914 błędne podłączenie termostatu, 919 niewykonana dezynfekcja, 920 błąd karty SD (FSV). Czujniki wody: 897–904, 910, 916. Błędy sprężarki/falownika: głównie 4xx. Pełna lista: `text_sensors.py` (mapowanie). Zachowanie zaobserwowane 07–09.11.2026: błąd 464 kasuje się sam po ok. 60 s, błąd 462 po 4–6 s, a jednostka ponawia rozruch po ok. 3,5 min; **po 9 błędach 464 z rzędu w 28 min (jeden w czasie pracy i 8 nieudanych ponowień rozruchu) kod został na stałe**, a strefy i CWU wyłączyły się (`0x4000`, `0x411E`, `0x4065` = Off) do ręcznego włączenia. Błąd 416 pozostał aktywny przez 66 min, choć sprężarka w tym czasie pracowała. Opis zdarzenia: sekcja „Zapis awarii" niżej. | P K L |

## Zapis awarii 07–09.11.2026 (błędy 464, 462, 416)

Źródło: eksport historii Home Assistant (CSV, 141 encji, 07.11 08:00 – 09.11 11:00 czasu polskiego; w pliku czasy są w UTC, tutaj podane jako CET = UTC+1). Drugi eksport (09.11 16:00 – 10.11 09:40) opisuje podsekcja „Ciąg dalszy". Fakty poniżej to odczyty z tego zapisu [**L**]; wnioski są oznaczone jako hipotezy [**W**]. Pompa miała wtedy ok. 1646 dni i 17 660 h pracy (`0x4423`, `0x4424`).

### Przebieg

| Kiedy (CET) | Co zapisano |
|---|---|
| 07.11 09:58 | Pierwszy błąd **464** w stanie ustalonym: 15 Hz, 2,7 A, 0,66 kW, tłoczenie 45 °C przy celu 70 °C, IPM 27 °C, sieć 217 V. Po 3,5 min rozruch udany. |
| 07.11 18:30 – 08.11 06:30 | Praca jeszcze poprawna: 35–50 Hz, 65–85 W ciepła na 1 Hz, COP 2,0–2,7 przy −2…−6 °C na zewnątrz i wodzie 32–34 °C, odszranianie co 1,5–2,5 h. |
| 08.11 06:38 | Błąd **462** przy starcie ładowania CWU: 81 Hz (zlecone 87 Hz), prąd 10,9 → 13,4 A tuż przed wyłączeniem. |
| 08.11 06:52 – 08:00 | CWU z grzałką booster; COP sprężarki 1,4–1,7. |
| 08.11 08:02 | Błąd **464** przy 41 Hz, minutę po przełączeniu zaworu z CWU na ogrzewanie; tłoczenie 97 °C, góra sprężarki 90 °C. |
| 08.11 08:15 – 09:40 | Moc cieplna na 1 Hz spada z 65 do 10 W; o 09:25 przy 15 Hz pobór 0,47 kW (dobę wcześniej 0,67 kW) i brak ciepła; czynnik na wymienniku płytowym chłodniejszy od wody (`0x4206` 25–31 °C przy wodzie 31–34 °C). |
| 08.11 09:41 – 10:09 | Błąd **464** przy rozpędzaniu do 40 Hz, potem 8 nieudanych rozruchów gorącej sprężarki co ok. 3,5 min; po dziewiątym błędzie z rzędu blokada do 23:32. |
| 08.11 23:33 – 23:57 | Po ręcznym włączeniu 7 nieudanych rozruchów (464) zimnej sprężarki (−3 °C). |
| 09.11 00:01 – 02:30 | Rozruch udany: 78 Hz, 3,0 kW, początkowo 5 kW ciepła (COP 1,7), po 2,5 h ok. 0,3 kW; tłoczenie do 110 °C przy celu 72 °C; `0x8218` cieplejszy od powietrza. |
| 09.11 03:39 | Błąd **462** przy 74 Hz, prąd 12,1 → 16,0 A. |
| 09.11 06:37 | Błąd **416** po odczycie tłoczenia 116,5 °C. |
| 09.11 07:45 – 10:07 | Obroty rosną z 40 do 76 Hz, pobór z 1,2 do 2,9 kW; ciepła mniej niż pobranej energii (od 08:00: 4,1 kWh z 4,8 kWh, COP 0,85), parownik w temperaturze powietrza. |
| 09.11 10:35 – 11:00 | 56 Hz, 1,5 kW, brak ciepła, **tłoczenie 27–31 °C** przy celu 62 °C (sprężarka tłoczy mokrą mieszaninę). |

Bilans 09.11 00:00 – 11:00: pobrane 21,3 kWh, oddane 14,3 kWh (COP 0,67). Dla porównania noc 07/08.11 (18:30 – 06:30): 15,3 kWh → 30,2 kWh (COP 1,97). Razem błąd 464 wystąpił 18 razy, 462 dwa razy, 416 raz.

### Ciąg dalszy 09.11 16:00 – 10.11 09:40 (bez błędów)

Drugi eksport, 17,7 h; między 11:00 a 16:00 09.11 danych nie ma. Fakty [**L**]:

- `0x8235` = 0 przez cały czas, żadnego odszraniania (`0x8061` = 0) przy −2…+4 °C na zewnątrz, sprężarka pracuje bez przerwy na 55–78 Hz. Jeden rozruch (09.11 21:07, po włączeniu strefy 1) udany za pierwszym razem.
- Bilans: 45,3 kWh pobrane, 34,3 kWh oddane, **COP 0,76** (licznik `0x4427` i moc z przepływu × ΔT zgodne do 3 %).
- Tłoczenie `0x820A` trzyma się celu `0x8223` (68–72 °C), chwilowo do 94,7 °C po rozruchu; najniżej 45,8 °C. IPM do 39 °C, przepływ 28,7–29,9 L/min, napięcie 207–220 V.
- Sprawność zmienia się z temperaturą wody powrotnej `0x4236`:

| Okres (CET) | Powrót | Sprężarka | Pobór → ciepło | COP | `0x8218` − `0x8204` |
|---|---|---|---|---|---|
| 09.11 16:00 – 21:00 (tylko strefa 2) | 30,6 °C | 60–72 Hz | 12,4 → 7,3 kWh | 0,59 | +1,9 K |
| 09.11 21:30 – 10.11 01:00 | 26,1 °C | 60–68 Hz | 6,9 → 8,3 kWh | 1,19 | −1,2 K |
| 10.11 01:00 – 09:40 | 28,8 °C | 72–78 Hz | 24,2 → 19,0 kWh | 0,79 | +1,0 K |

Wniosek [**W**]: usterka trwa, choć nie ma już kodów błędów, przegrzewania ani mokrej pracy. Dwukrotna zmiana COP przy zmianie temperatury wody o 4,5 K pasuje do przecieku między stroną wysokiego i niskiego ciśnienia (im wyższe ciśnienie skraplania, tym więcej gazu wraca na ssanie), czyli do sprężarki lub zaworu 4-drożnego. Brak odszraniań przez wiele godzin pracy przy temperaturze bliskiej 0 °C jest dodatkowym objawem, że parownik nie pobiera ciepła.

### Co wykluczają dane

- **Hydraulika**: przepływ `0x42E9` stały 29,5–30,3 L/min (CWU ok. 25 L/min) przez cały zapis, bez błędów 911/913.
- **Zasilanie**: napięcie `0x24FC` nie spada z obciążeniem, szyna DC `0x823B` bez załamań przed błędami.
- **Przegrzanie falownika**: IPM `0x8254` najwyżej 44 °C.
- **Brak czynnika** [W]: 09.11 tłoczenie spadało do temperatury nasycenia (27–31 °C), co wymaga cieczy w obiegu, a parownik był cieplejszy od powietrza, nie zimniejszy.

### Hipoteza [W]

Obieg przestał sprężać: gorący gaz wraca na stronę ssawną zamiast do skraplacza (nieszczelność wewnętrzna sprężarki albo zawór 4-drożny w położeniu pośrednim), a nadprądy 462/464 i nieudane rozruchy wskazują na mechaniczne uszkodzenie sprężarki. Tłoczenie na przemian dużo powyżej i dużo poniżej celu `0x8223` pasuje też do niesprawnego zaworu rozprężnego jako przyczyny pierwotnej (zalewanie sprężarki cieczą). Rozstrzygnie pomiar serwisowy: ciśnienia ssania i tłoczenia, rezystancja uzwojeń i izolacji sprężarki, test przełączania zaworu 4-drożnego oraz położenie EEV (`0x8229`, dodane po awarii).

### Sygnatury, które warto monitorować

Wszystkie przy pracującej sprężarce (`0x8238` > 0), poza odszranianiem:

1. `0x820A` − `0x8223` > 15 K dłużej niż 10 min przy stałej częstotliwości.
2. `0x8218` ≥ `0x8204` (parownik nie zimniejszy od powietrza) dłużej niż 20 min.
3. Moc cieplna z `0x42E9` i ΔT poniżej 40 W na 1 Hz (sprawna praca: 65–85 W/Hz przy wodzie 32–34 °C).
4. `0x4206` < `0x4238` w trybie grzania.
5. Dowolny kod 4xx w `0x8235`, także taki, który sam się skasował.
6. COP poniżej 1,5 przez godzinę ciągłej pracy bez grzałki (moc z przepływu i ΔT ÷ `0x8411`) – także wtedy, gdy `0x8235` = 0: 09–10.11.2026 pompa pracowała 17,7 h bez kodu błędu z COP 0,76.

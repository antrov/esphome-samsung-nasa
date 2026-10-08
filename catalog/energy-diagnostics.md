# Energia, zasilanie i diagnostyka

Pobór prądu, produkcja ciepła (do liczenia COP), parametry zasilania jednostki zewnętrznej, liczniki życia urządzenia i kody błędów. Legenda kolumn i tagów źródeł: [`README.md`](README.md). Czujniki obiegu chłodniczego i falownika: [`outdoor-unit.md`](outdoor-unit.md).

## Jak policzyć COP z tych wpisów

- **COP chwilowy** ≈ `0x4426` ÷ `0x8413` (moc cieplna oddana ÷ moc elektryczna jednostki zewnętrznej, oba w W). Wartości odświeżają się w różnych momentach i przy rozruchu mocno „skaczą", więc sensowny jest raczej wynik uśredniony.
- **COP skumulowany** ≈ `0x4427` ÷ `0x8414` (kWh ÷ kWh). W chwili zapisu logu: 48 580,4 kWh ÷ 17 151,8 kWh ≈ **2,83** (licznik życiowy od instalacji, w tym CWU i ogrzewanie).
- Przykładowe czujniki szablonowe (reset o północy, COP liczony z różnic) są w sekcji „COP" głównego [`README.md`](../README.md#cop-coefficient-of-performance).
- Licznik `0x8414` obejmuje **tylko jednostkę zewnętrzną** (bez pomp i grzałek modułu hydraulicznego). Energię grzałek i pomp szacuje sama pompa na podstawie FSV 3081–3083 (zob. [`unused.md`](unused.md)); instrukcja zastrzega, że pomiary produktu mogą różnić się od rzeczywistego zużycia.

## Wpisy

| ID | Encja | Wartości | Co to jest | Na co wpływa, uwagi | Źr. |
|---|---|---|---|---|---|
| `0x8413`<br>OUT | `Outdoor Instantaneous Power` *(sensor)* | W<br>log: **15–1745** | Chwilowa moc elektryczna pobierana przez jednostkę zewnętrzną – suma modułów (`LVAR_OUT_CONTROL_WATTMETER_1W_1MIN_SUM`). | Dla Home Assistant: moc urządzenia (`device_class: power`). Rośnie z częstotliwością sprężarki (`0x8238`). Lista kodów mówi o odświeżaniu co ok. 30 s; w logu co ok. 44 s. | P K L |
| `0x8411`<br>OUT | `Outdoor unit inst. power consumed` *(sensor)* | W<br>log: **0–1652** | Moc chwilowa pojedynczej jednostki zewnętrznej (`WATTMETER_1UNIT`). | Duplikat `0x8413` dla jednej jednostki; lista kodów: „not used by the controller", odświeżany rzadziej. Wystarczy `0x8413`. | P K L |
| `0x8414`<br>OUT | `Outdoor Cumulative Energy` *(sensor)* | kWh (surowo Wh × 0,001), `total_increasing`<br>log: **17 151,826 → 17 151,889** | Skumulowane zużycie energii elektrycznej jednostki zewnętrznej (`WATTMETER_ALL_UNIT_ACCUM`). | Nadaje się do panelu Energia w HA. Tylko jednostka zewnętrzna. Mianownik skumulowanego COP. | P K L |
| `0x8217`<br>OUT | `Outdoor Current` *(sensor)* | A (surowo × 0,1)<br>log: **0 → 7,9** | Prąd sprężarki 1 (`SENSOR_CT1`; w YAML „Outdoor Current"). | Rośnie z obciążeniem; 230 V × 7,9 A ≈ 1,8 kW, zgodnie z `0x8413`. Błędy 462/464/485 dotyczą nadprądów i czujnika prądu. | P K L |
| `0x24FC`<br>OUT | `Outdoor Voltage` *(sensor)* | V<br>log: **212–215** | Napięcie zasilania mierzone przez jednostkę zewnętrzną (`LVAR_NM_OUT_SENSOR_VOLTAGE`). | Do monitorowania jakości zasilania; spadek obciążeniowy widać przy rozruchu. Błędy 466/483/488 dotyczą nad-/podnapięć i czujnika napięcia. | P K L |
| `0x4284`<br>IN | `Indoor unit power consumption` *(sensor)* | W<br>log: brak próbek | Moc pobierana przez jednostkę wewnętrzną (`NASA_INDOOR_POWER_CONSUMPTION`). | Ten model prawdopodobnie jej nie raportuje. Dokładność zależy od FSV 3081–3083 (moce grzałek). | P K |
| `0x4426`<br>IN | `Heat pump produced energy (last minute)` *(sensor)* | W (int16)<br>log: **0 → 3990 → 2630 → 4031** | Moc cieplna oddana przez pompę w ostatniej minucie (`LVAR_IN_4426`). Mimo nazwy „energy" jednostką jest wat. | Licznik własny pompy; licznik COP chwilowego (zob. wyżej). Spada do 0 przy postoju i podczas odszraniania. | P K L |
| `0x4427`<br>IN | `Heat pump produced energy (total)` *(sensor)* | kWh (surowo Wh × 0,001), `total_increasing`<br>log: **48 580,404 → 48 580,580** | Skumulowana energia cieplna oddana przez pompę od instalacji (`LVAR_IN_4427`). | Licznik życiowy ciepła (CWU + ogrzewanie); licznik COP skumulowanego (wyżej). Pomiar produktu – może odbiegać od licznika ciepła. | P K L |
| `0x4423`<br>IN | `Days since installation` *(sensor)* | dni (surowo minuty ÷ 1440)<br>log: **1616,6 d** (2 327 872 min ≈ 4,4 roku) | Czas od daty instalacji wpisanej w menu serwisowym (`LVAR_IN_MINS_SINCE_INST`). | Informacyjnie (gwarancja, przeglądy). Nie wpływa na sterowanie. | P K L |
| `0x4424`<br>IN | `Hours active since installation` *(sensor)* | godziny (surowo minuty ÷ 60)<br>log: **17 329 h** (1 039 743 min) | Czas aktywnej pracy od instalacji (`LVAR_IN_MINS_ACTIVE_SINCE_INST`). | Informacyjnie; ok. 45 % czasu od instalacji (porównaj `0x4423`). Nie wpływa na sterowanie. | P K L |
| `0x8235`<br>OUT | `error_code` *(sensor)*<br>`Error description (text)` *(text_sensor)* | liczba = numer błędu (0 = brak), text: opis; 91 kodów w komponencie, inne → „Unknown (N)"<br>log: **0** | Aktywny kod błędu układu (`VAR_OUT_ERROR_CODE`) – ten sam numer, co „Exxx" na sterowniku. Sensor ma kategorię *diagnostic* i publikuje tylko zmiany. | Przydatne do powiadomień. Kody związane z hydrauliką: 911 niski przepływ, 913 wyłącznik przepływu, 914 błędne podłączenie termostatu, 919 niewykonana dezynfekcja, 920 błąd karty SD (FSV). Czujniki wody: 897–904, 910, 916. Błędy sprężarki/falownika: głównie 4xx. Pełna lista: `text_sensors.py` (mapowanie). | P K L |

# Hydraulika: temperatury wody i przepływ

Czujniki temperatury wody w module hydraulicznym, przepływ oraz temperatury czynnika chłodniczego po stronie wymiennika płytowego. Legenda kolumn i tagów źródeł: [`README.md`](README.md). Temperatura zasobnika CWU (`0x4237`): [`dhw.md`](dhw.md). Temperatura zewnętrzna i obieg chłodniczy: [`outdoor-unit.md`](outdoor-unit.md).

## Mapa czujników

Instrukcja producenta opisuje czujniki wody (Tw1–Tw4) i pokazuje ich odczyty w menu serwisowym sterownika [M]. Przypisanie do komunikatów NASA wynika z nazw w protokole (`Hydro_WaterIn`, `Hydro_WaterOut`, `Hydro_HeaterOut`, `Hydro_MixingValve`) i z przebiegów w logu – to wniosek, nie jawna deklaracja producenta.

| Oznaczenie w instrukcji | Gdzie mierzy | Komunikat |
|---|---|---|
| **Tw1** (Inlet Water / PHE IN) | wlot wody do wymiennika płytowego – powrót z instalacji | `0x4236` |
| **Tw2** (Discharge Water / PHE OUT) | wylot z wymiennika – zasilanie | `0x4238` |
| **Tw3** (Backup Heater Outlet) | wylot za grzałką backup | `0x4239` |
| **Tw4** (Mixing Valve) | za zaworem mieszającym (drugi obieg) | `0x428C` |
| **Tt** (DHW Tank) | zasobnik CWU | `0x4237` ([`dhw.md`](dhw.md)) |
| **Teva_in / Teva_out** | czynnik chłodniczy po obu stronach wymiennika płytowego | `0x4205` / `0x4206` |

## Wpisy

| ID | Encja | Wartości | Co to jest | Na co wpływa, uwagi | Źr. |
|---|---|---|---|---|---|
| `0x4236`<br>IN | `Flow return temperature` *(sensor)* | °C (÷10)<br>log: **33,1–46,6** | Temperatura wody wracającej z instalacji do pompy (Tw1, `Hydro_WaterIn`). | Tylko odczyt. Różnica `0x4238` − `0x4236` (ΔT) mówi, ile ciepła oddaje woda w instalacji; docelowe ΔT pompy inwerterowej to FSV 4052 (domyślnie 5 °C). Duży przepływ przy małym ΔT oznacza zbędnie szybką pompę (większy pobór prądu). | M P K L |
| `0x4238`<br>IN | `Flow temperature` *(sensor)* | °C (÷10)<br>log: **34,0–50,0** | Temperatura wody zasilającej na wylocie z pompy (Tw2, `Hydro_WaterOut`). | Tylko odczyt. To wartość, którą pompa stara się doprowadzić do celu (`0x4247`/`0x42D7` lub `0x427F`; w danej chwili żądany cel to `0x4202`). Wysoka temperatura zasilania = wyższy pobór i niższe COP. | M P K L |
| `0x4239`<br>IN | `Water outlet heater temperature` *(sensor)* | °C (÷10)<br>log: **33,6–48,6** | Temperatura wody za grzałką backup (Tw3, `Hydro_HeaterOut`). | Tylko odczyt. Przy wyłączonej grzałce (`0x406C` = 0, tak było w logu) zbliżona do Tw1/Tw2; rośnie ponad Tw2 dopiero, gdy grzałka pracuje. | M P K L |
| `0x428C`<br>IN | `Mixing valve temperature` *(sensor)* | °C (÷10)<br>log: **27,0–33,5** | Temperatura wody za zaworem mieszającym (Tw4, `Hydro_MixingValve`) – dla obiegu niskotemperaturowego. | Tylko odczyt. Sensowna, gdy zawór mieszający jest skonfigurowany (FSV 4041–4046: 1 = regulacja wg ΔT, 2 = wg krzywej). W logu zbliżona do wylotów stref (`0x42D8`/`0x42D9`). | M P K L |
| `0x4202`<br>IN | `Heat DHW until this temperature` *(sensor)* | °C (÷10)<br>log: **32,5 → 35,5 → 32,5 → 70,0** | Bieżąca temperatura wody, jakiej jednostka wewnętrzna **żąda** od pompy ciepła (efektywny cel wylotu). Nazwa w YAML pochodzi z etykiety forka (`VAR_IN_DHW_HEAT_UNTIL`); w protokole to `VAR_IN_??`. | Tylko odczyt. W logu: 32,5 °C (strefa 1 = cel `0x4247`), 35,5 °C po włączeniu strefy 2 (= cel `0x42D7`), 70,0 °C w czasie ładowania zasobnika. Zachowuje się więc jak cel wylotu dla aktualnie obsługiwanego odbiornika, **nie** jak cel zasobnika (55 °C to `0x4235`). Pomaga zrozumieć, dlaczego pompa pracuje przy danej temperaturze. | K L W |
| `0x4204`<br>IN | `Water Out TW2` *(sensor)* | °C (÷10)<br>log: **25,5–29,8** | W protokole `NASA_MODIFIED_CURRENT_TEMP` („zmodyfikowana temperatura bieżąca"); etykieta forka `VAR_IN_WATER_OUT_TW2`. | Znaczenie niepewne. W README forka opisano jako „podobne do `0x4238`, ale 2 °C niższe" – w tym logu **nie** pasuje (wylot 34–50 °C, ta wartość 25–30 °C i zmienia się wolno). Nie traktuj jako wylotu z wymiennika. | P K L W |
| `0x4205`<br>IN | `EVA return temperature` *(sensor)* | °C (÷10)<br>log: **32,1–46,2** | Temperatura czynnika chłodniczego na wejściu wymiennika płytowego (Teva_in, `VAR_IN_TEMP_EVA_IN_F`). | Czujnik po stronie obiegu chłodniczego. W trybie grzania wymiennik jest skraplaczem: strona gazowa (`0x4206`) jest cieplejsza niż strona cieczowa (`0x4205`) – w logu po starcie sprężarki 52,0 vs 46,2 °C. Różnica zbliżona do zera = sprężarka nie pracuje. | M P K L W |
| `0x4206`<br>IN | `EVA flow temperature` *(sensor)* | °C (÷10)<br>log: **32,5–52,0** | Temperatura czynnika chłodniczego na wyjściu wymiennika płytowego (Teva_out, `VAR_IN_TEMP_EVA_OUT_F`). | Jak `0x4205`. Wraz z `0x4238` pokazuje skuteczność oddawania ciepła do wody (im mniejsza różnica czynnik–woda, tym lepiej). | M P K L W |
| `0x42E8`<br>IN | `Flow sensor voltage` *(sensor)* | V po skali ×0,1 (surowo 44; 171–202)<br>log: **4,4 · 17,1–20,2** | Surowy sygnał czujnika przepływu (`VAR_IN_FLOW_SENSOR_VOLTAGE`). | Po przeskalowaniu wartości 17–20 „V" są nierealistyczne dla czujnika przepływu – traktuj jako wskaźnik względny. W logu przepływ `0x42E9` rośnie liniowo z tą wartością (ok. 1,96 L/min na 1 jednostkę powyżej 4,4). | P K L W |
| `0x42E9`<br>IN | `Flow` *(sensor)* | L/min (÷10, `lpm`; `device_class: water` z YAML)<br>log: **0 → 30,8–31,0 → 24,9–25,5** | Przepływ wody przez obieg grzewczy (`VAR_IN_FLOW_SENSOR_CALC`). Lista kodów mówi o odświeżaniu co ok. 90 s; w tym logu przychodził co ok. 40 s. | Tylko odczyt. Zależy od prędkości pompy (`0x40C4`, FSV 4051–4054) i otwarcia zaworów stref. Zbyt mały przepływ → błąd 911 (niski przepływ) i ochrona pompy. Wraz z ΔT (`0x4238` − `0x4236`) pozwala oszacować moc cieplną: P ≈ 69,8 W · (L/min) · ΔT[K]. | M P K L |
| `0x82DF`<br>OUT | `TW1 sensor reading` *(sensor)* | °C (÷10)<br>log: **65036 → −50,0 °C = brak danych** | Temperatura wody „TW1" raportowana przez jednostkę zewnętrzną (protokół: `Water In 1 for EHS`). | README forka podaje, że na innych modelach jest równa `0x4238` (wylot), choć nazwa z protokołu sugeruje wlot – numeracja TW1/TW2 bywa niespójna. Ten model **nie dostarcza** tej wartości (stała 65036) – w HA wyświetla się jako −50 °C. Użyj `0x4236`/`0x4238`. | P K L |
| `0x82E0`<br>OUT | `TW2 sensor reading` *(sensor)* | °C (÷10)<br>log: **65036 → −50,0 °C = brak danych** | Temperatura wody „TW2" raportowana przez jednostkę zewnętrzną (protokół: `Water In 2 for EHS`). | Jak `0x82DF` (README forka: na innych modelach równa `0x4236`, czyli powrotowi). Użyj `0x4236`/`0x4238`. | P K L |

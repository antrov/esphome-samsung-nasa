# Ciepła woda użytkowa (CWU)

Podgrzewanie zasobnika: włączenie funkcji, tryb, temperatury, zawór 3-drożny i grzałka booster. Legenda kolumn i tagów źródeł: [`README.md`](README.md). Ustawienia serwisowe CWU (FSV 30xx, 1051/1052, 5019–5023): [`fsv.md`](fsv.md). Cel wylotu, którego pompa żąda w danej chwili (`0x4202`), jest w [`hydraulics.md`](hydraulics.md).

## Jak to działa (skrót z instrukcji producenta)

- **Włączenie funkcji.** FSV 3011 musi mieć wartość 1 lub 2 (w logu: 1) i musi być podłączony czujnik zasobnika. Włącznikiem w codziennym użyciu jest `0x4065`.
- **Kiedy pompa grzeje zasobnik.** Start, gdy temperatura w zasobniku spadnie poniżej *celu minus FSV 3023* (domyślnie 5 °C); stop po osiągnięciu celu plus FSV 3022 (domyślnie 2 °C). FSV 3011 = 1 oznacza start wg progu *thermo ON*, FSV 3011 = 2 – wg progu *thermo OFF* (czyli grzanie rusza wcześniej).
- **Pompa ciepła vs grzałka.** Samą pompą ciepła zasobnik grzeje się do FSV 3021 (maks. temperatura pompą, domyślnie 55/63/70 °C zależnie od jednostki zewnętrznej). Powyżej tego – tylko grzałka booster (jeśli jest i FSV 3031 = On).
- **Tryby** (`0x4066`):
  - **Economic (Eco)** – tylko pompa ciepła, cel obniżony o FSV 5021 (domyślnie 5 °C: nastawa 45 °C → praca do 40 °C); booster nie pracuje.
  - **Standard** – pompa ciepła, a grzałka booster dołącza po opóźnieniu FSV 3032 (domyślnie 20 min), jeśli zasobnik nadal nie osiągnął celu.
  - **Power** – opóźnienie boostera jest pomijane, grzałka startuje od razu (szybciej, ale dużo więcej energii). Wymaga zamontowanej grzałki.
  - **Force** – cała moc pompy ciepła tylko na CWU; domyślnie nie wyłącza się sama, czas ogranicza FSV 3051/3052.
- **Naprzemienność z ogrzewaniem.** Gdy naraz jest żądanie ogrzewania i CWU, pompa przełącza obieg: FSV 3024 (minimalny czas ogrzewania, 5 min), 3025 (maksymalny czas CWU, 30 min), 3026 (maksymalny czas ogrzewania, 3 h). Limity działają **tylko przy jednoczesnych żądaniach** – pojedyncze żądanie grzeje do skutku. FSV 4011 wybiera priorytet (0 = CWU, 1 = ogrzewanie, ale tylko poniżej progu temperatury zewnętrznej FSV 4012).
- **Dezynfekcja zasobnika.** FSV 3041–3046: cykliczne podgrzanie do 70 °C (domyślnie raz w tygodniu, w piątek; start 23:00 przy dezynfekcji grzałką lub 14:00 samą pompą R290). Nieosiągnięcie temperatury w czasie FSV 3046 kończy się błędem E919.

## Wpisy

| ID | Encja | Wartości | Co to jest | Na co wpływa, uwagi | Źr. |
|---|---|---|---|---|---|
| `0x4065`<br>IN | `DHW On/Off control` *(switch)* | 0 Off · 1 On<br>log: **On** | Włączenie/wyłączenie funkcji CWU (`ENUM_IN_WATER_HEATER_POWER`). | Wyłączenie = pompa przestaje ładować zasobnik (zostaje tylko ogrzewanie; zasobnik stygnie). Wymaga FSV 3011 = 1/2. | M P K L |
| `0x4066`<br>IN | `Hotwater Mode` *(select)*<br>`DHW mode (text)` *(text_sensor)* | select (opcje z YAML): Eco (0) · Standard (1) · Power (2) · Force (3); text_sensor: Economic · Standard · Power · Force<br>log: **Standard** | Tryb pracy CWU – kompromis między szybkością a oszczędnością energii (opis trybów wyżej). | Decyduje, czy i kiedy dołącza grzałka booster oraz czy cel jest obniżony (Eco). Tryb Force bez limitu czasu (FSV 3051 = Nie) trzyma pompę na CWU, dopóki nie zostanie wyłączony. Etykiety `Eco/Standard/Power/Force` ustawione w YAML zastępują domyślne „Economy…" z komponentu (zachowane dla historii HA). | M P K L |
| `0x4067`<br>IN | `DHW valve` *(sensor)*<br>`Threeway Valve on Tank` *(binary_sensor)*<br>`Water flow diversion (text)` *(text_sensor)* | 0 Room (ogrzewanie) · 1 Tank (zasobnik); text: „Room (Heating)" / „Tank (DHW)"; binary ON = zbiornik<br>log: **1** od 21:49:55 | Położenie zaworu 3-drożnego: dokąd płynie gorąca woda z pompy ciepła – do obiegów grzewczych albo do wężownicy zasobnika. | Wartość 1 oznacza aktywne ładowanie zasobnika – ogrzewanie jest wtedy chwilowo pozbawione ciepła (stąd naprzemienne cykle wg FSV 3024–3026). Kierunek domyślny bez zasilania: FSV 3071 (0 Room / 1 Tank). Najlepszy wskaźnik „pompa grzeje teraz CWU". | M P K L |
| `0x4235`<br>IN | `Hot Water Target Temperature` *(number)* | °C, krok 0,5, zakres 30–70 (z `model: EHS_MONO` 30–65; w YAML nie ustawiono)<br>log: **55,0** | Zadana temperatura wody w zasobniku CWU. | Jak wysoko ma być grzana woda. Realny zakres ogranicza FSV 1051 (maks.; w tej instalacji 55 °C = wartość zadana jest na limicie) i 1052 (min., 40 °C). Powyżej FSV 3021 dogrzewa już tylko grzałka booster. Wyższy cel = więcej energii i niższe COP. | M P K L |
| `0x4237`<br>IN | `Warm water` *(sensor)* | °C (÷10)<br>log: **48,1 → 47,5** | Temperatura w zasobniku CWU (czujnik Tt). | Tylko odczyt. Na jej podstawie pompa decyduje o starcie/końcu ładowania (progi FSV 3022/3023). W logu zasobnik był ok. 7 K poniżej celu 55 °C i lekko stygł, gdy po 21:49:55 zaczęło się ładowanie (woda grzewcza dopiero się rozgrzewała). | M P K L |
| `0x4087`<br>IN | `Booster Heater` *(binary_sensor)* | 0 Off · 1 On<br>log: **Off** | Elektryczna grzałka w zasobniku CWU (booster, BSH). | Dogrzewa CWU ponad możliwości pompy (FSV 3021) i w trybach Power/Force; w Economic nie pracuje. Użycie włącza FSV 3031, opóźnienie startu FSV 3032, histereza wyłączenia FSV 3033 (wyłączenie przy celu + FSV 3033). Duży pobór prądu. Dezynfekcja zwykle wymaga grzałki (poza wariantami R290). | M P K L |

## Przykład z logu 08.10.2026 – ładowanie zasobnika

Po wyłączeniu obu stref (21:49:54) zawór 3-drożny przeszedł na zbiornik (`0x4067` = 1, 21:49:55) i pompa zaczęła ładować CWU: cel wylotu (`0x4202`) wzrósł do 70,0 °C, temperatura wylotu (`0x4238`) rosła z 34 do 50 °C, sprężarka rozpędziła się do 55 Hz, a oddawana moc cieplna (`0x4426`) sięgnęła ok. 4 kW przy poborze ok. 1,7 kW (`0x8413`).

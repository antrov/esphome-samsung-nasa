# Instructions for AI agents and contributors

This repository is an ESPHome external component (`samsung_nasa`) plus the owner's Samsung EHS heat pump configuration (`samsung_hvac.yaml`).

## Mandatory: keep the catalogue in `catalog/` up to date

`catalog/` is the human-readable catalogue (in Polish) of every NASA message, Home Assistant entity and FSV setting used in `samsung_hvac.yaml`: ID, entity name, units/scaling, what it is, **what it affects**, and where the knowledge comes from. **Every change must be reflected there, in the same commit.**

You MUST update `catalog/` when you:

- add, remove or rename an entity, or change the message / `fsv` / options / filters / unit of an entity in `samsung_hvac.yaml` (or any YAML that represents the owner's installation);
- change a registry in `components/samsung_nasa/nasa/*.py` (`sensors.py`, `binary_sensors.py`, `numbers.py`, `selects.py`, `switches.py`, `text_sensors.py`, `fsv.py`, `nasa_labels.py`) in a way that alters scaling, ranges, options, mappings or labels of an entry that is in use;
- learn something from a log, a manual or a measurement that corrects or extends a description (even when no code changes);
- move a message into the YAML (move its row from `catalog/unused.md` to the right topic file) or retire one (move it back to `unused.md`).

How:

1. Find the row by message ID, e.g. `grep -rn "0x4235" catalog/`. There is one row per NASA message; if a message backs several entities, list all of them in the "Encja" cell as backticked, exact YAML names.
2. Keep six columns per row (ID/device, Encja, Wartości, Co to jest, Na co wpływa, Źr.). The legend and the source tags `M P K L W` are in `catalog/README.md`. Write in Polish.
3. State facts only with a source tag. If you infer, tag it `W` and say what would confirm it. Never invent semantics, ranges or defaults - write "brak próbek" / "nieznane" instead. Log values are examples and must be labelled `log:` with the date. Never put secrets, IP addresses or credentials in the catalogue.
4. Run `python3 tools/check_catalog.py` - it must print `catalog OK` (exit code 0). It checks that every message and entity in the YAML has a row, that no stale rows remain, and that rows have six columns and valid tags.
5. Mention the catalogue update in the commit message.

Entity names determine Home Assistant `unique_id`s (see `MIGRATION.md`). Never rename the 14 migrated entities from the mapping table in `MIGRATION.md`. Rename any other entity only for a good reason (e.g. the name is wrong in meaning), list every rename (old name, new name, reason) in the "Zmiany po migracji" section of `MIGRATION.md`, and keep the old name in the catalogue row as "Wcześniej `…`" (outside the "Encja" cell, which must contain only current names).

## Adding a sensor that is not in the component's registry

`samsung_hvac.yaml` loads the component with `external_components` from GitHub **without `ref`**, i.e. from the default branch (`main`). A change under `components/` reaches the firmware only after it is merged to `main`. A YAML entity whose message is missing from `main`'s registry is built as a "User configured" sensor with no unit, device class or scaling (a temperature of 40.0 shows up as 400).

- Define such a sensor completely in the YAML: `unit_of_measurement`, `device_class`, `state_class`, `accuracy_decimals` and `filters` (see `0x42D8`, `0x4239`). Temperatures need `lambda: return (int16_t)x;` followed by `multiply: 0.1`.
- Do not also add a registry entry on a feature branch: registry filters and YAML filters are concatenated, so a repeated `multiply: 0.1` would divide by 100 once the branch is merged.
- Check with `esphome config samsung_hvac.yaml`: the log says "Auto configured" (registry) or "User configured" (YAML) per message, and the printed config shows the filters that will apply.

## Other conventions

- Owner-facing documentation (`MIGRATION.md`, `catalog/`) is in Polish; code, YAML comments and commit messages are in English.
- Secrets live in `secrets.yaml` (git-ignored); never commit them.
- The Samsung manual (`MIM-E03EN.pdf`) is the authoritative source for FSV semantics; `samsung_nasa_protocol.md` is a community-maintained, partly unverified list of NASA codes.

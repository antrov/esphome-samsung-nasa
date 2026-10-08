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

## Other conventions

- Owner-facing documentation (`MIGRATION.md`, `catalog/`) is in Polish; code, YAML comments and commit messages are in English.
- Secrets live in `secrets.yaml` (git-ignored); never commit them.
- The Samsung manual (`MIM-E03EN.pdf`) is the authoritative source for FSV semantics; `samsung_nasa_protocol.md` is a community-maintained, partly unverified list of NASA codes.

#!/usr/bin/env python3
"""Check that catalog/*.md documents exactly the entities used in samsung_hvac.yaml.

Rules (see AGENTS.md and catalog/README.md):
  * every samsung_nasa message used in the YAML has one row in a topic file
    (catalog/*.md except README.md and unused.md), and the row lists every
    entity name of that message in backticks in its "Encja" column;
  * rows for messages that are no longer in the YAML (or entity names no longer
    in the YAML) are reported as stale;
  * a message must not be in the YAML and in catalog/unused.md at the same time;
  * rows must have 6 columns and valid source tags (M P K L W).

Usage:  python3 tools/check_catalog.py [path/to/config.yaml]
Exit status: 0 = consistent, 1 = problems found. Standard library only.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
FSV_MAP = ROOT / "components" / "samsung_nasa" / "nasa" / "fsv.py"
TAGS = {"M", "P", "K", "L", "W"}
ID_ROW = re.compile(r"^\|\s*`(0x[0-9A-Fa-f]{4})`")


def unquote(value):
    value = value.split(" #")[0].strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def yaml_entities(path):
    """Return {message_id: set(names)} for every `platform: samsung_nasa` entity."""
    fsv = {int(code): int(msg, 16) for code, msg in re.findall(r"(\d{4}):\s*(0x[0-9A-Fa-f]{4})", FSV_MAP.read_text())}
    entities, current = [], None
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^[A-Za-z_]+:", line):  # a new top-level key ends the previous entity
            current = None
            continue
        m = re.match(r"^\s*-\s*platform:\s*(\S+)", line)
        if m:
            current = {} if m.group(1) == "samsung_nasa" else None
            if current is not None:
                entities.append(current)
            continue
        m = re.match(r"^\s+(message|fsv|name):\s*(.+?)\s*$", line)
        if current is not None and m:
            current[m.group(1)] = unquote(m.group(2))
    found = defaultdict(set)
    for entity in entities:
        if "message" in entity:
            code = int(entity["message"], 16)
        elif "fsv" in entity:
            code = fsv[int(entity["fsv"])]
        else:
            continue
        found["0x%04X" % code].add(entity.get("name", ""))
    return found


def catalog_rows():
    """Return (used, unused): {id: [(file, lineno, cells)]} taken from the catalogue tables."""
    used, unused = defaultdict(list), defaultdict(list)
    for md in sorted(CATALOG.glob("*.md")):
        if md.name == "README.md":
            continue
        target = unused if md.name == "unused.md" else used
        for number, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            m = ID_ROW.match(line)
            if m:
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                target["0x%04X" % int(m.group(1), 16)].append((md.name, number, cells))
    return used, unused


def main():
    config = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "samsung_hvac.yaml"
    in_yaml = yaml_entities(config)
    used, unused = catalog_rows()
    problems = []

    for ident, names in sorted(in_yaml.items()):
        rows = used.get(ident)
        if not rows:
            problems.append(f"{ident}: used in {config.name} but has no row in catalog/ (entities: {sorted(n for n in names if n)})")
            continue
        fname, number, cells = rows[0]
        if len(rows) > 1:
            problems.append(f"{ident}: documented more than once ({', '.join(f'{f}:{n}' for f, n, _ in rows)})")
        documented = set(re.findall(r"`([^`]+)`", cells[1])) if len(cells) > 1 else set()
        for name in sorted(n for n in names if n and n not in documented):
            problems.append(f"{ident}: entity `{name}` is in the YAML but missing from the 'Encja' cell ({fname}:{number})")
        for name in sorted(documented - names):
            problems.append(f"{ident}: `{name}` is documented but not in the YAML for this message ({fname}:{number})")

    for ident, rows in sorted(used.items()):
        if ident not in in_yaml:
            problems.append(f"{ident}: documented in {rows[0][0]}:{rows[0][1]} but not used in {config.name} (move to unused.md or delete)")
        for fname, number, cells in rows:
            if len(cells) != 6:
                problems.append(f"{fname}:{number}: expected 6 columns, found {len(cells)}")
            elif not set(cells[5].split()) or not set(cells[5].split()) <= TAGS:
                problems.append(f"{fname}:{number}: bad source tags {cells[5]!r} (allowed: {' '.join(sorted(TAGS))})")

    for ident, rows in sorted(unused.items()):
        if ident in in_yaml:
            problems.append(f"{ident}: listed in unused.md:{rows[0][1]} but already used in {config.name} (move the row to a topic file)")

    if problems:
        print("catalog check FAILED:")
        for problem in problems:
            print("  - " + problem)
        return 1
    print(f"catalog OK: {len(in_yaml)} messages, {sum(len(names) for names in in_yaml.values())} entities documented")
    return 0


if __name__ == "__main__":
    sys.exit(main())

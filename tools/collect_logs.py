#!/usr/bin/env python3
"""Collect samsung_nasa logs from the device and condense them for pasting.

Runs `esphome logs` for a fixed time, saves the raw log and prints a compact
summary: one line per NASA message (last value, number of occurrences, whether
it changed) plus a timeline of value changes.

Examples:
  tools/collect_logs.py samsung_hvac.yaml --device 192.168.1.50 -d 60
  tools/collect_logs.py samsung_hvac.yaml --device /dev/cu.usbserial-0001 -d 120 --copy
  tools/collect_logs.py --cmd 'uvx --python 3.12 --from "esphome>=2026.5" esphome' samsung_hvac.yaml
  tools/collect_logs.py --from-file raw.log          # re-summarise an existing log
"""
import argparse
import queue
import re
import shlex
import subprocess
import sys
import threading
import time
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
TIME = re.compile(r"(\d{2}:\d{2}:\d{2})")
KNOWN = re.compile(r"Src:(\S+)\s+Dst:(\S+)\s+(0x[0-9A-Fa-f]+)\s*=\s*(\S+)")
UNDEF = re.compile(r"Undefined\s+s:(\S+)\s+d:(\S+)\s+(\w+)\s+([0-9A-Fa-f]{4})\s*=\s*(\S+)")


def capture(cmd, duration, raw_path):
    """Stream the command output for `duration` seconds, return the lines."""
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            stdin=subprocess.DEVNULL, text=True, errors="replace", bufsize=1)
    q = queue.Queue()

    def reader():
        for line in proc.stdout:
            q.put(line)
        q.put(None)

    threading.Thread(target=reader, daemon=True).start()
    lines, end = [], time.monotonic() + duration
    try:
        with open(raw_path, "w") as raw:
            while time.monotonic() < end:
                try:
                    line = q.get(timeout=0.5)
                except queue.Empty:
                    continue
                if line is None:
                    break
                raw.write(line)
                lines.append(line)
                if sys.stderr.isatty():
                    print(f"\r{len(lines)} lines, {int(end - time.monotonic())}s left ",
                          end="", file=sys.stderr)
    except KeyboardInterrupt:
        pass
    finally:
        exited = proc.poll()
        proc.terminate()
        print(file=sys.stderr)
    if exited is not None and not any(KNOWN.search(l) or UNDEF.search(l) for l in lines):
        print(f"esphome exited early (code {exited}) without NASA messages:", file=sys.stderr)
        print("".join(ANSI.sub("", l) for l in lines[-15:]), file=sys.stderr)
    return lines


def parse(lines):
    """Return (messages, other) where messages is keyed by (src, dst, kind, code)."""
    msgs = OrderedDict()
    other = []
    ts = ""
    for line in lines:
        text = ANSI.sub("", line).strip()
        if not text:
            continue
        m = TIME.search(text[:40])
        if m:
            ts = m.group(1)
        k, u = KNOWN.search(text), UNDEF.search(text)
        if k:
            src, dst, code, val = k.groups()
            key = (src, dst, "known", code.upper().replace("0X", "0x"))
        elif u:
            src, dst, kind, code, val = u.groups()
            key = (src, dst, kind, "0x" + code.upper())
        else:
            # keep timestamped lines with a real message (errors, warnings, ...);
            # the empty "[..][samsung_nasa:NNN]:" headers precede each NASA line
            if m and not text.endswith("]:"):
                other.append(text)
            continue
        e = msgs.setdefault(key, {"n": 0, "first": val, "last": val, "changes": []})
        e["n"] += 1
        if val != e["last"]:
            e["changes"].append((ts, e["last"], val))
        e["last"] = val
    return msgs, other


def render(msgs, other, duration):
    out = [f"# samsung_nasa log summary ({duration}, {sum(e['n'] for e in msgs.values())} "
           f"messages, {len(msgs)} unique)", ""]
    out.append("## Messages  (src -> dst  kind  code  last  [xN] [changed first->last])")
    for (src, dst, kind, code), e in sorted(msgs.items()):
        chg = f"  CHANGED {e['first']}->{e['last']} ({len(e['changes'])}x)" if e["changes"] else ""
        out.append(f"{src} -> {dst}  {kind:<12} {code}  {e['last']}  x{e['n']}{chg}")
    timeline = sorted((t, k, a, b) for k, e in msgs.items() for t, a, b in e["changes"])
    if timeline:
        out += ["", "## Timeline of value changes"]
        for t, (src, dst, kind, code), a, b in timeline:
            out.append(f"{t}  {src}->{dst} {kind} {code}: {a} -> {b}")
    if other:
        out += ["", "## Other log lines"]
        seen = OrderedDict()
        for line in other:
            seen[line] = seen.get(line, 0) + 1
        out += [f"{l}" + (f"  (x{c})" if c > 1 else "") for l, c in list(seen.items())[:200]]
    return "\n".join(out) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("config", nargs="?", default="samsung_hvac.yaml", help="ESPHome YAML (default: %(default)s)")
    p.add_argument("--device", help="IP/hostname or serial port; omit to let esphome ask")
    p.add_argument("-d", "--duration", type=int, default=60, help="capture seconds (default: %(default)s)")
    p.add_argument("--cmd", default="esphome", help="esphome command prefix (default: %(default)s)")
    p.add_argument("-o", "--out", help="output directory (default: ./logs)")
    p.add_argument("--from-file", help="skip capture, summarise this raw log file")
    p.add_argument("--copy", action="store_true", help="copy summary to the clipboard (pbcopy)")
    args = p.parse_args()

    out_dir = Path(args.out or "logs")
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    if args.from_file:
        lines = Path(args.from_file).read_text(errors="replace").splitlines()
    else:
        cmd = shlex.split(args.cmd) + ["logs", args.config]
        if args.device:
            cmd += ["--device", args.device]
        raw_path = out_dir / f"raw-{stamp}.log"
        print(f"Running: {' '.join(cmd)}", file=sys.stderr)
        lines = capture(cmd, args.duration, raw_path)
        print(f"Raw log: {raw_path}", file=sys.stderr)

    msgs, other = parse(lines)
    summary = render(msgs, other, "from file" if args.from_file else f"{args.duration}s")
    summary_path = out_dir / f"summary-{stamp}.txt"
    summary_path.write_text(summary)
    print(summary)
    print(f"Summary saved to {summary_path}", file=sys.stderr)
    if args.copy:
        subprocess.run(["pbcopy"], input=summary, text=True)
        print("Copied to clipboard.", file=sys.stderr)


if __name__ == "__main__":
    main()

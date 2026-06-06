#!/usr/bin/env python3
"""
Pokemon automation script manager.

Usage:
  python manager.py list                              list all scripts and status
  python manager.py start <name> [script args...]     start a script in background
  python manager.py stop <name|all>                   stop running script(s)
  python manager.py status                            show running scripts
  python manager.py logs <name> [-n N]                show last N lines of log

Examples:
  python manager.py list
  python manager.py start frlg:snorlax --switch_num 1
  python manager.py start swsh:eggs --switch_num 2
  python manager.py start home:sort --starting_box 1
  python manager.py status
  python manager.py stop frlg:snorlax
  python manager.py stop all
  python manager.py logs frlg:snorlax -n 100
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT / "scripts"
LOGS_DIR = ROOT / "logs"
STATE_FILE = ROOT / ".manager_state.json"

# Registry of all runnable scripts.
# 'path' is relative to the scripts/ directory.
# 'args_hint' is shown in `list` to remind you what args the script accepts.
REGISTRY: dict[str, dict] = {
    # --- FRLG ---
    "frlg:snorlax":  {"path": "frlg/snorlax.py",   "description": "Snorlax encounter hunt",        "args_hint": "--switch_num N"},
    "frlg:starters": {"path": "frlg/starters.py",  "description": "FRLG starter hunt",             "args_hint": "--switch_num N"},
    "frlg:wild":     {"path": "frlg/wild.py",       "description": "FRLG wild encounter hunt",      "args_hint": "--switch_num N"},
    "frlg:nugget":   {"path": "frlg/nugget.py",     "description": "Nugget farming",                "args_hint": "--switch_num N"},
    "frlg:xp_farm":  {"path": "frlg/xp_farm.py",   "description": "XP farming",                    "args_hint": "--switch_num N"},
    # --- BDSP ---
    "bdsp:eggs":     {"path": "bdsp/bdsp_eggs.py",     "description": "BDSP egg hatching",          "args_hint": ""},
    "bdsp:starters": {"path": "bdsp/bdsp_starters.py", "description": "BDSP starter hunt",          "args_hint": "--switch_num N"},
    "bdsp:unown":    {"path": "bdsp/unown.py",         "description": "Unown hunt",                 "args_hint": ""},
    # --- SWSH ---
    "swsh:eggs":     {"path": "swsh/swsh_eggs.py",        "description": "SWSH egg hatching",       "args_hint": ""},
    "swsh:fishing":  {"path": "swsh/fishing_hunt2.py",    "description": "Fishing hunt",            "args_hint": ""},
    "swsh:route":    {"path": "swsh/route_encounter.py",  "description": "Route encounter hunt",    "args_hint": ""},
    "swsh:wild":     {"path": "swsh/wild_encounter.py",   "description": "SWSH wild encounter",     "args_hint": ""},
    "swsh:watts":    {"path": "swsh/watt_farm.py",        "description": "Watt farming",            "args_hint": ""},
    # --- Dynamax Adventures ---
    "da":            {"path": "dynamax_adventures/da_main.py", "description": "Dynamax Adventure",  "args_hint": ""},
    # --- Scarlet/Violet ---
    "sv:eggs":       {"path": "sv_eggs.py",     "description": "SV egg hatching",                   "args_hint": "--switch_num N"},
    "sv:tera":       {"path": "tera_raid.py",   "description": "Tera raid automation",              "args_hint": ""},
    "sv:zone":       {"path": "za_zone_reset.py", "description": "Zone reset",                      "args_hint": ""},
    # --- Pokemon Home ---
    "home:census":   {"path": "home/census.py",     "description": "Home box census",               "args_hint": ""},
    "home:sort":     {"path": "home/home_sort.py",  "description": "Home box sorting",              "args_hint": "--starting_box N (required)"},
    # --- Tools ---
    "debug":         {"path": "services/debug_screen.py", "description": "Debug screen tool",       "args_hint": "--switch_num N [--image] [--x N --y N]"},
    "multi_press":   {"path": "services/multi_press.py",  "description": "Button press REPL",       "args_hint": "--switch_num N"},
    "odds":          {"path": "services/odds_calc.py",    "description": "Shiny odds calculator",   "args_hint": "--odds N --tries N"},
}


# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------

def _load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def _save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2))


def _is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def _clean_state(state: dict) -> dict:
    """Remove stale entries (processes that died on their own)."""
    return {name: entry for name, entry in state.items() if _is_running(entry["pid"])}


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_list(_args) -> None:
    state = _clean_state(_load_state())
    _save_state(state)

    print(f"\n{'NAME':<20} {'STATUS':<22} {'DESCRIPTION':<30}  ARGS")
    print("-" * 90)
    for name, info in sorted(REGISTRY.items()):
        entry = state.get(name)
        status = f"running  PID {entry['pid']}" if entry else "stopped"
        hint = info.get("args_hint", "")
        print(f"{name:<20} {status:<22} {info['description']:<30}  {hint}")
    print()


def cmd_start(args) -> None:
    name = args.name
    if name not in REGISTRY:
        print(f"Unknown script '{name}'. Run `list` to see available scripts.")
        sys.exit(1)

    state = _load_state()
    entry = state.get(name)
    if entry and _is_running(entry["pid"]):
        print(f"'{name}' is already running (PID {entry['pid']}). Stop it first.")
        sys.exit(1)

    LOGS_DIR.mkdir(exist_ok=True)
    log_path = LOGS_DIR / f"{name.replace(':', '_')}.log"
    script_path = SCRIPTS_DIR / REGISTRY[name]["path"]
    cmd = [sys.executable, str(script_path)] + (args.script_args or [])

    with log_path.open("a") as log_file:
        log_file.write(f"\n{'='*60}\nStarted: {datetime.now().isoformat()}\nCmd: {' '.join(cmd)}\n{'='*60}\n")
        log_file.flush()
        proc = subprocess.Popen(
            cmd,
            cwd=str(SCRIPTS_DIR),
            stdout=log_file,
            stderr=log_file,
        )

    state[name] = {
        "pid": proc.pid,
        "log": str(log_path),
        "started": datetime.now().isoformat(),
    }
    _save_state(state)
    print(f"Started '{name}'  PID {proc.pid}")
    print(f"Logs:   {log_path}")


def cmd_stop(args) -> None:
    state = _load_state()
    names = list(state.keys()) if args.name == "all" else [args.name]

    if not names:
        print("No scripts are running.")
        return

    changed = False
    for name in names:
        entry = state.get(name)
        if not entry:
            if args.name != "all":
                print(f"'{name}' is not running.")
            continue

        pid = entry["pid"]
        if not _is_running(pid):
            print(f"'{name}' already stopped (stale PID {pid}).")
            del state[name]
            changed = True
            continue

        try:
            os.kill(pid, signal.SIGTERM)
            for _ in range(20):
                time.sleep(0.2)
                if not _is_running(pid):
                    break
            else:
                os.kill(pid, signal.SIGKILL)
                print(f"Force-killed '{name}' (PID {pid})")
            del state[name]
            changed = True
            print(f"Stopped '{name}' (PID {pid})")
        except ProcessLookupError:
            del state[name]
            changed = True
            print(f"Stopped '{name}' (already gone)")

    if changed:
        _save_state(state)


def cmd_status(_args) -> None:
    state = _clean_state(_load_state())
    _save_state(state)

    if not state:
        print("No scripts are running.")
        return

    print(f"\n{'NAME':<20} {'PID':<8} {'STARTED'}")
    print("-" * 55)
    for name, entry in sorted(state.items()):
        print(f"{name:<20} {entry['pid']:<8} {entry['started']}")
    print()


def cmd_logs(args) -> None:
    state = _load_state()
    name = args.name
    entry = state.get(name)

    log_path = Path(entry["log"]) if entry else LOGS_DIR / f"{name.replace(':', '_')}.log"

    if not log_path.exists():
        print(f"No log file found for '{name}' at {log_path}")
        sys.exit(1)

    lines = log_path.read_text().splitlines()
    for line in lines[-args.lines:]:
        print(line)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pokemon automation script manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all scripts and their current status")

    p_start = sub.add_parser("start", help="Start a script in the background")
    p_start.add_argument("name", help="Script name from the registry (e.g. frlg:snorlax)")
    p_start.add_argument("script_args", nargs=argparse.REMAINDER, help="Args forwarded to the script")

    p_stop = sub.add_parser("stop", help="Stop a running script")
    p_stop.add_argument("name", help="Script name, or 'all' to stop everything")

    sub.add_parser("status", help="Show all currently running scripts")

    p_logs = sub.add_parser("logs", help="Print recent log output for a script")
    p_logs.add_argument("name", help="Script name")
    p_logs.add_argument("-n", "--lines", type=int, default=50, help="Lines to show (default: 50)")

    args = parser.parse_args()

    dispatch = {
        "list":   cmd_list,
        "start":  cmd_start,
        "stop":   cmd_stop,
        "status": cmd_status,
        "logs":   cmd_logs,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()

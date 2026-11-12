#!/usr/bin/env python3
"""Render model, context pressure, usage windows, and a scratchpad link."""

import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time


def number(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value):
        return value
    return None


def percentage(value):
    value = number(value)
    return None if value is None else min(100, max(0, value))


def reset_timer(timestamp, now):
    timestamp = number(timestamp)
    if timestamp is None:
        return ""
    minutes = max(0, math.ceil((timestamp - now) / 60))
    if minutes == 0:
        return "reset due"
    days, remainder = divmod(minutes, 1440)
    hours, minutes = divmod(remainder, 60)
    duration = f"{days}d{hours}h" if days else f"{hours}h{minutes:02d}m" if hours else f"{minutes}m"
    return f"↻ {duration}"


def scratchpad_link(session_id):
    # Keep the session ID a literal path component, never a glob or traversal.
    if not isinstance(session_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", session_id):
        return

    # Claude defaults to /tmp on macOS (not macOS's per-user $TMPDIR).
    # Search one project level rather than duplicating its path-escaping rules,
    # which have changed between releases. Never create a scratchpad ourselves.
    default_tmp = "/tmp" if sys.platform == "darwin" else tempfile.gettempdir()
    root = Path(os.environ.get("CLAUDE_CODE_TMPDIR") or default_tmp) / f"claude-{os.getuid()}"
    try:
        for project in sorted(root.iterdir()):
            scratchpad = project / session_id / "scratchpad"
            if scratchpad.is_dir():
                return f"\033]8;;{scratchpad.absolute().as_uri()}\033\\📁 scratchpad\033]8;;\033\\"
    except OSError:
        return


def render(data, now):
    parts = []
    model = data.get("model") or {}
    effort = (data.get("effort") or {}).get("level")
    name = model.get("display_name") or model.get("id")
    if name:
        parts.append(f"{name} · {effort}" if effort else name)
    elif effort:
        parts.append(f"effort {effort}")

    context = percentage((data.get("context_window") or {}).get("used_percentage"))
    if context is not None:
        # Standard ANSI colors use the terminal's palette (Nord in this repo).
        color = 31 if context >= 90 else 33 if context >= 70 else 32
        parts.append(f"\033[{color}mctx {context:g}%\033[0m")

    limits = data.get("rate_limits") or {}
    for key, label in [("five_hour", "5h"), ("seven_day", "7d")]:
        window = limits.get(key) or {}
        used = percentage(window.get("used_percentage"))
        if used is not None:
            timer = reset_timer(window.get("resets_at"), now)
            parts.append(f"{label} {used:g}%" + (f" {timer}" if timer else ""))

    link = scratchpad_link(data.get("session_id"))
    if link:
        parts.append(link)
    return " | ".join(parts)


def main():
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        return
    if isinstance(data, dict):
        line = render(data, time.time())
        if line:
            print(line)


if __name__ == "__main__":
    main()

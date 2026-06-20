#!/usr/bin/env python3
"""
xhs_helper.py — thin wrapper around xhs CLI for OpenClaw Skill
Usage:
  python3 xhs_helper.py read <note-id-or-url>
  python3 xhs_helper.py user <user-id-or-url>
  python3 xhs_helper.py comments <note-url> [--all] [--limit N]
  python3 xhs_helper.py status
"""

import sys
import json
import subprocess
import re
from pathlib import Path

XHS_BIN = "xhs"

def run_xhs(args, timeout=30):
    """Run xhs command, return (ok, data_or_error)"""
    try:
        result = subprocess.run(
            [XHS_BIN] + args,
            capture_output=True, text=True, timeout=timeout
        )
    except FileNotFoundError:
        return False, {"error": "xhs command not found. Install: uv tool install xiaohongshu-cli"}
    except subprocess.TimeoutExpired:
        return False, {"error": "xhs command timed out"}

    # Try parsing stdout as JSON
    try:
        out = json.loads(result.stdout.strip())
        ok = out.get("ok", False)
        if ok:
            return True, out.get("data", {})
        else:
            err = out.get("error", {})
            return False, {"error": err.get("message", str(err))}
    except json.JSONDecodeError:
        # Fallback: return raw stdout if not JSON
        if result.stdout.strip():
            return True, {"raw": result.stdout.strip()}
        return False, {"error": result.stderr.strip() or "unknown error"}


def extract_note_id(url_or_id: str) -> str:
    """Extract note ID from URL or return as-is if already raw ID"""
    url = url_or_id.strip()
    # Already a raw hex ID
    if re.match(r"^[0-9a-fA-F]{24,}$", url):
        return url
    # Parse from URL
    for pattern in [
        r"/explore/([0-9a-fA-F]{24,})",
        r"/discovery/item/([0-9a-fA-F]{24,})",
        r"/discovery/([0-9a-fA-F]{24,})",
        r"/note/([0-9a-fA-F]{24,})",
    ]:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    # Return as-is and let xhs handle it
    return url


def extract_user_id(url_or_id: str) -> str:
    """Extract user ID from URL or return as-is"""
    url = url_or_id.strip()
    if re.match(r"^[0-9a-fA-F]{24,}$", url):
        return url
    m = re.search(r"/user/profile/([0-9a-fA-F]{24,})", url)
    if m:
        return m.group(1)
    return url


def cmd_status():
    ok, data = run_xhs(["status", "--json"])
    print(json.dumps({"ok": ok, "data": data}, ensure_ascii=False))
    return 0 if ok else 1


def cmd_read(note_arg: str):
    note_id = extract_note_id(note_arg)
    ok, data = run_xhs(["read", note_id, "--json"])
    if not ok:
        print(json.dumps({"ok": False, "error": data.get("error")}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "data": data}, ensure_ascii=False))
    return 0


def cmd_user(user_arg: str):
    user_id = extract_user_id(user_arg)
    ok, data = run_xhs(["user", user_id, "--json"])
    if not ok:
        print(json.dumps({"ok": False, "error": data.get("error")}, ensure_ascii=False))
        return 1
    print(json.dumps({"ok": True, "data": data}, ensure_ascii=False))
    return 0


def cmd_comments(note_arg: str, fetch_all: bool = False, limit: int = 100):
    """Fetch comments for a note, optionally all pages."""
    note_id = extract_note_id(note_arg)
    args = ["comments", note_id, "--json"]
    if fetch_all:
        args.append("--all")

    ok, data = run_xhs(args, timeout=120)
    if not ok:
        print(json.dumps({"ok": False, "error": data.get("error")}, ensure_ascii=False))
        return 1

    comments = data.get("comments", []) if isinstance(data, dict) else []
    if limit and limit > 0:
        comments = comments[:limit]

    result = {"ok": True, "count": len(comments), "comments": comments}
    print(json.dumps(result, ensure_ascii=False))
    return 0


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: xhs_helper.py read|user|status <arg>"}))
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "status":
        sys.exit(cmd_status())
    elif cmd == "read":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: xhs_helper.py read <note-id-or-url>"}))
            sys.exit(1)
        sys.exit(cmd_read(sys.argv[2]))
    elif cmd == "user":
        if len(sys.argv) < 3:
            print(json.dumps({"error": "Usage: xhs_helper.py user <user-id-or-url>"}))
            sys.exit(1)
        sys.exit(cmd_user(sys.argv[2]))
    elif cmd == "comments":
        # Parse optional flags before positional arg
        fetch_all = "--all" in sys.argv
        limit = 100
        note_arg = None
        for a in sys.argv[2:]:
            if a == "--all":
                fetch_all = True
            elif a.startswith("--limit-"):
                try:
                    limit = int(a.split("=")[1])
                except (IndexError, ValueError):
                    pass
            elif not a.startswith("--"):
                note_arg = a
        if not note_arg:
            print(json.dumps({"error": "Usage: xhs_helper.py comments <note-url> [--all] [--limit-N]"}))
            sys.exit(1)
        sys.exit(cmd_comments(note_arg, fetch_all=fetch_all, limit=limit))
    else:
        print(json.dumps({"error": f"Unknown command: {cmd}"}))
        sys.exit(1)


if __name__ == "__main__":
    main()

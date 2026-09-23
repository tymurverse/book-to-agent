#!/usr/bin/env python3
"""
export — deploy an advisor anywhere, not just Claude Code.

An advisor skill (SKILL.md) runs in Claude Code, Cursor, Amp and other SKILL.md
agents as-is. This converts the same advisor into other homes:
  system   a plain system prompt you paste into a ChatGPT/Claude Project or an API call
  json     a portable "advisor card" (name, description, instructions) for your own app

One book -> one advisor -> usable everywhere. book-to-skill is Claude-Code-centric;
this is how book-to-agent goes wherever you work.

Usage:
    python export.py <advisor SKILL.md> --format system --out advisor.txt
    python export.py <advisor SKILL.md> --format json   --out advisor.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys


def _utf8():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def parse_skill(md: str) -> dict:
    """Split a SKILL.md into frontmatter (name/description) + body."""
    name, desc, body = "", "", md
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", md, re.S)
    if m:
        fm, body = m.group(1), m.group(2)
        nm = re.search(r"^name:\s*(.+)$", fm, re.M)
        dm = re.search(r"^description:\s*(.+)$", fm, re.M)
        name = (nm.group(1).strip() if nm else "").strip("\"'")
        desc = (dm.group(1).strip() if dm else "").strip("\"'")
    return {"name": name, "description": desc, "body": body.strip()}


def to_system_prompt(skill: dict) -> str:
    """A clean system prompt: the advisor's instructions, minus the Claude-Code frontmatter."""
    title = skill["name"].replace("-", " ").title() or "Advisor"
    lines = [f"You are {title}, an advisor.", ""]
    if skill["description"]:
        lines += [skill["description"], ""]
    lines.append("Follow these instructions exactly:")
    lines.append("")
    lines.append(skill["body"])
    return "\n".join(lines)


def to_card(skill: dict) -> dict:
    return {"name": skill["name"], "description": skill["description"],
            "instructions": skill["body"],
            "note": "Portable advisor card. Feed 'instructions' as the system prompt in any LLM app."}


def main(argv=None):
    _utf8()
    ap = argparse.ArgumentParser(description="Export an advisor skill to a system prompt or advisor card.")
    ap.add_argument("skill")
    ap.add_argument("--format", choices=["system", "json"], default="system")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        with open(a.skill, encoding="utf-8", errors="replace") as fh:
            skill = parse_skill(fh.read())
    except FileNotFoundError:
        raise SystemExit(f"SKILL.md not found: {a.skill}")
    out = to_system_prompt(skill) if a.format == "system" else json.dumps(to_card(skill), ensure_ascii=False, indent=1)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(out)
        print(f"exported {a.format} -> {a.out}  ({skill['name']})")
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

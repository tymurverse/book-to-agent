#!/usr/bin/env python3
"""
ground — the trust engine: verify a generated advisor is faithful to its source.

The #1 fear with "book -> AI advisor" is that the model invents frameworks the
author never taught. This checks the opposite: every framework the advisor claims
must be GROUNDED in the real source text. Each framework carries a few distinctive
"anchors" (phrases that should appear if it's genuinely in the book); this confirms
they're actually there, flags any that aren't as possible hallucinations, and
prints a single fidelity score.

Deterministic and offline — no model, no guessing. This is what lets the repo say
"every framework is grounded in the real book," and prove it.

Usage:
    python ground.py <source.txt> <frameworks.json> [--out report.json]

frameworks.json: [{"name": "...", "chapter": "...", "anchors": ["phrase", ...]}, ...]
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


def _norm(t: str) -> str:
    return re.sub(r"\s+", " ", (t or "").lower())


def score(source: str, frameworks: list, threshold: float = 0.6) -> dict:
    norm = _norm(source)
    results, covs = [], []
    for fw in frameworks:
        anchors = fw.get("anchors", []) or []
        # Word-boundary match on the whitespace-normalised text. This is what makes
        # the check trustworthy: an anchor like "flux" never matches "influx", and a
        # phrase split across a line-break in the source still matches.
        found = [a for a in anchors
                 if re.search(r"\b" + re.escape(_norm(a)) + r"\b", norm)]
        cov = len(found) / len(anchors) if anchors else 0.0
        grounded = bool(anchors) and cov >= threshold
        # evidence: a window of the source text around the first found anchor
        ev = ""
        if found:
            m = re.search(r"\b" + re.escape(_norm(found[0])) + r"\b", norm)
            if m:
                a0 = max(0, m.start() - 70)
                b0 = min(len(norm), m.end() + 70)
                ev = ("..." if a0 else "") + norm[a0:b0].strip() + ("..." if b0 < len(norm) else "")
        results.append({
            "name": fw.get("name", ""),
            "chapter": fw.get("chapter", ""),
            "anchors_total": len(anchors),
            "anchors_found": len(found),
            "coverage": round(cov, 2),
            "grounded": grounded,
            "missing_anchors": [a for a in anchors if a not in found],
            "evidence": ev,
        })
        covs.append(cov)
    grounded_ct = sum(1 for r in results if r["grounded"])
    total = len(results) or 1
    return {
        "tool": "ground", "tool_version": "1.0",
        "fidelity_score": round(100 * grounded_ct / total),
        "avg_coverage": round(100 * (sum(covs) / total)),
        "grounded": grounded_ct, "total": len(results),
        "flagged": [r["name"] for r in results if not r["grounded"]],
        "frameworks": results,
        "note": ("Fidelity = share of the advisor's frameworks that are provably present in the "
                 "source text. Flagged frameworks are NOT supported by the source — treat as possible "
                 "hallucination and cut or rewrite them. Deterministic anchor check, never guessed."),
    }


def render(d: dict) -> str:
    out = [f"FIDELITY {d['fidelity_score']}/100   ({d['grounded']}/{d['total']} frameworks grounded, "
           f"avg coverage {d['avg_coverage']}%)", ""]
    for r in d["frameworks"]:
        mark = "✓ grounded " if r["grounded"] else "✗ FLAGGED  "
        out.append(f"  {mark} {r['name']}  [{r['anchors_found']}/{r['anchors_total']} anchors]")
        if r["grounded"] and r["evidence"]:
            out.append(f"        source: \"{r['evidence']}\"")
        if not r["grounded"]:
            out.append(f"        ⚠ not found in source — possible hallucination, cut or rewrite it.")
    if d["flagged"]:
        out.append("\nFLAGGED (not in the book): " + ", ".join(d["flagged"]))
    out.append("\n" + d["note"])
    return "\n".join(out)


def main(argv=None):
    _utf8()
    ap = argparse.ArgumentParser(description="Verify an advisor's frameworks are grounded in the source book.")
    ap.add_argument("source")
    ap.add_argument("frameworks")
    ap.add_argument("--threshold", type=float, default=0.6)
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    try:
        with open(a.source, encoding="utf-8", errors="replace") as fh:
            src = fh.read()
    except FileNotFoundError:
        raise SystemExit(f"Source text not found: {a.source}")
    try:
        with open(a.frameworks, encoding="utf-8") as fh:
            fws = json.load(fh)
    except FileNotFoundError:
        raise SystemExit(f"frameworks file not found: {a.frameworks}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"{a.frameworks} is not valid JSON: {e}")
    if isinstance(fws, dict):
        fws = fws.get("frameworks", [])
    d = score(src, fws, threshold=a.threshold)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=1)
    print(render(d))
    return 0


if __name__ == "__main__":
    sys.exit(main())

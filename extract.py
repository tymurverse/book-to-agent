#!/usr/bin/env python3
"""
extract — pull clean text + a section skeleton from a book the user owns.

Step 1 of book-to-agent. It reads a local book file (PDF/EPUB/TXT/MD) the user
legally owns and produces (a) clean UTF-8 text to work from and (b) a "skeleton"
of the likely chapter/section headers, so the converter can map the book's real
structure before writing the advisor skill.

This is a local processing tool over the user's own file. The advisor skill built
from it must express the book's ideas in original words — never reproduce the text.
"""
from __future__ import annotations

import argparse
import re
import sys


def _utf8():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def read_book(path: str) -> str:
    low = path.lower()
    if low.endswith(".pdf"):
        return _read_pdf(path)
    if low.endswith(".epub"):
        return _read_epub(path)
    if low.endswith((".txt", ".md", ".markdown")):
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    raise SystemExit(f"Unsupported file type: {path}. Use PDF, EPUB, TXT or MD.")


def _read_pdf(path: str) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        raise SystemExit("PDF support needs pypdf:  pip install pypdf")
    r = PdfReader(path)
    return "\n".join((p.extract_text() or "") for p in r.pages)


def _read_epub(path: str) -> str:
    try:
        from ebooklib import epub
        import ebooklib
        from bs4 import BeautifulSoup
    except Exception:
        raise SystemExit("EPUB support needs:  pip install ebooklib beautifulsoup4")
    book = epub.read_epub(path)
    parts = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "lxml")
        parts.append(soup.get_text(" ", strip=True))
    return "\n".join(parts)


def clean(text: str) -> str:
    # normalise common PDF artefacts: smart quotes, ligatures, hyphenated line breaks
    repl = {"ﬁ": "fi", "ﬂ": "fl", "’": "'", "‘": "'",
            "“": '"', "”": '"', "–": "-", "—": "-", "…": "..."}
    for a, b in repl.items():
        text = text.replace(a, b)
    text = re.sub(r"-\n(\w)", r"\1", text)      # de-hyphenate across line breaks
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# words that mark a real framework/section header in most non-fiction business books
_HEADER_HINT = re.compile(
    r"(section|chapter|part|principle|framework|formula|equation|method|step|"
    r"law|rule|strategy|the \w+ (of|to)|how to)", re.I)


def skeleton(text: str, max_headers: int = 80) -> list:
    """Heuristic: short lines that look like headers (ALL CAPS, Title Case, or
    numbered/keyword lines). Not perfect — a map for the human/agent, not gospel."""
    out, seen = [], set()
    for raw in text.split("\n"):
        s = raw.strip()
        if not (4 <= len(s) <= 60):
            continue
        words = s.split()
        looks_header = (
            re.match(r"^(section|chapter|part)\b", s, re.I)
            or re.match(r"^\d+[\.\):]\s+\w", s)                 # "3. Pricing"
            or (s.isupper() and 1 < len(words) <= 8)            # ALL CAPS short line
            or (_HEADER_HINT.search(s) and len(words) <= 8 and s[:1].isupper())
        )
        if looks_header:
            key = re.sub(r"\s+", " ", s.lower())
            if key not in seen:
                seen.add(key)
                out.append(s)
        if len(out) >= max_headers:
            break
    return out


def main(argv=None):
    _utf8()
    ap = argparse.ArgumentParser(description="Extract clean text + section skeleton from a book you own.")
    ap.add_argument("book", help="path to a PDF/EPUB/TXT/MD you legally own")
    ap.add_argument("--out", help="write the cleaned full text here (UTF-8)")
    ap.add_argument("--skeleton", action="store_true", help="print the detected chapter/section headers")
    ap.add_argument("--max-chars", type=int, default=0, help="cap the text written (0 = no cap)")
    a = ap.parse_args(argv)

    try:
        text = clean(read_book(a.book))
    except FileNotFoundError:
        raise SystemExit(f"File not found: {a.book}")
    if a.max_chars:
        text = text[: a.max_chars]
    words = len(text.split())
    print(f"Extracted ~{words:,} words from {a.book}")

    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"  full text → {a.out}")

    if a.skeleton:
        sk = skeleton(text)
        print(f"\nSECTION SKELETON ({len(sk)} candidate headers):")
        for h in sk:
            print("  -", h)
    return 0


if __name__ == "__main__":
    sys.exit(main())

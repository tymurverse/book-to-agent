<p align="center">
  <img src="assets/logo.svg" alt="book-to-agent" width="128">
</p>

<h1 align="center">book-to-agent</h1>

<p align="center">
  <a href="https://github.com/tymurverse/book-to-agent/actions/workflows/tests.yml"><img src="https://github.com/tymurverse/book-to-agent/actions/workflows/tests.yml/badge.svg" alt="tests"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT"></a>
</p>

**Turn a book you own into an advisor that thinks and talks like its author — grounded in the real text, deployable anywhere.**

Not a summary. Not a search index. A *mentor* — the author's frameworks, their voice, and how they'd actually advise **you** on your live problem.

> `book-to-skill` gives your agent the book's **knowledge**.
> **`book-to-agent` gives it the author's judgment** — the method, the voice, and the advice.

---

## Why it's different: it's grounded, and it proves it

The number-one fear with "book → AI" is that the model **invents** things the author never taught. So book-to-agent refuses to ship on vibes. Every framework the advisor claims carries a few distinctive **anchors**, and a deterministic checker **verifies each one is actually in the book** — flagging anything that isn't as a possible hallucination, and printing a **fidelity score**.

```
$ python ground.py meditations.txt examples/the-stoic/frameworks.json
FIDELITY 100/100   (6/6 frameworks grounded, avg coverage 100%)

  ✓ grounded  Focus only on what's in your power   [1/1 anchors]
        source: "...it will no more be in thy power without all distraction as thou oughtest..."
  ✓ grounded  Live according to nature; accept what happens   [1/1 anchors]
        source: "...what is the nature of the universe, and what is mine--in particular..."
  ...

$ python ground.py artofwar.txt evals/hallucination-demo.json
FIDELITY 67/100   (2/3 frameworks grounded)
  ✗ FLAGGED   The Growth-Hacking Funnel   [0/3 anchors]
        ⚠ not found in source — possible hallucination, cut or rewrite it.
```

Point it at the *wrong* book and the score collapses — the check matches whole anchor phrases on word boundaries, so it can't be fooled by a stray common word. **An advisor you can't ground is one you can't trust.** This one you can.

---

## Try it now — the public-domain gallery

Ready-to-use advisors built from public-domain classics (100% legal to ship):

| Advisor | From | Use it for |
|---|---|---|
| **The Strategist** | *The Art of War* (Sun Tzu) | competition, negotiation, out-thinking a stronger rival |
| **The Stoic** | *Meditations* (Marcus Aurelius) | stress, anger, letting go of what you can't control |

Drop `examples/the-strategist/` into your Claude Code / Cursor skills folder and ask it a real question.

---

## Install

```bash
git clone https://github.com/tymurverse/book-to-agent.git
cd book-to-agent
pip install -r requirements.txt      # only needed for PDF/EPUB input + running the tests
```
Python 3.8+. Plain **TXT / MD** books need no dependencies at all — `pip install` only matters for PDF/EPUB extraction and the test suite.

## Reproduce the fidelity demo in 20 seconds

```bash
# grab the two public-domain sources from Project Gutenberg
curl -L https://www.gutenberg.org/cache/epub/132/pg132.txt  -o artofwar.txt      # The Art of War
curl -L https://www.gutenberg.org/cache/epub/2680/pg2680.txt -o meditations.txt  # Meditations

python ground.py artofwar.txt   examples/the-strategist/frameworks.json   # → 100/100
python ground.py meditations.txt examples/the-stoic/frameworks.json       # → 100/100
python ground.py artofwar.txt   evals/hallucination-demo.json             # → a made-up framework gets FLAGGED
```

---

## How it works

```
  a book file you OWN
        │
   ① extract   → clean text + structure (PDF · EPUB · TXT · MD)
   ② analyse   → split METHOD (the frameworks) from VOICE (the persona)
   ③ generate  → an advisor SKILL.md: Persona + Method + Workflow + Guardrails
   ④ ground    → verify every framework is in the source; print a fidelity score
   ⑤ export    → deploy to Claude Code, Cursor, a ChatGPT/Claude Project, or your API
```

Two ways to run it:
- **As a Claude Code skill** — the agent does the authoring in-session (no API key). See `SKILL.md`.
- **As Python tools** — `extract.py`, `ground.py`, `export.py` (bring your own model for the authoring step).

## Bring your own book

```bash
python extract.py "your-book.pdf" --out book.txt --skeleton    # ① read structure
#   ② + ③  the agent writes  your-advisor/SKILL.md + frameworks.json  (follow SKILL.md)
python ground.py book.txt your-advisor/frameworks.json          # ④ prove it's faithful
python export.py your-advisor/SKILL.md --format system          # ⑤ take it anywhere
```

## Copyright — the clean line

- **You bring a book you own. It stays yours.** book-to-agent never distributes copyrighted text.
- **Ideas aren't copyrightable; the author's exact words are.** Advisors express frameworks in *original phrasing* — the source is never reproduced.
- **Advisors advise "in the style of"** the author — they are not the author, and they're named neutrally.
- **The examples shipped here are public-domain** (Art of War, Meditations). The copyrighted ones you build stay private to you — the `.gitignore` keeps your book files and outputs out of git.

## Tests

```bash
python -m pytest -q      # extract + ground + export
```

## Contributing

Issues and PRs welcome — please open an issue to discuss anything substantial first.

## License

MIT — see [LICENSE](LICENSE).

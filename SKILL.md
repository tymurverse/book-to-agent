---
name: book-to-agent
description: Turn a non-fiction book the user legally owns into a ready-to-use advisor agent — a skill that gives advice in the author's voice using the book's frameworks. Use when the user wants to "turn this book into an agent/skill", build an advisor from an author (Hormozi, Ogilvy, Cialdini, etc.), or convert a business/marketing/self-improvement book into something an agent can apply. Produces a persona + method + workflow skill, copyright-clean.
---

# Book to Agent

You convert a book into a working **advisor agent**: a skill that gives real advice, in the author's style, using the author's frameworks — applied to the user's actual situation. The proven output shape is **Persona + Method + Workflow + Guardrails** (see the reference example `examples/the-strategist/SKILL.md`, built from the public-domain *Art of War*).

This is a **converter**: the user brings a book they legally own; you produce a derived *skill* that teaches the ideas in original words. You never reproduce the book's text.

## When NOT to proceed
- If the user hasn't provided a book file they own, ask for the path. Don't source a copy yourself.
- Fiction, poetry, or reference-only books don't convert well — this is for books with **teachable frameworks** (business, marketing, sales, negotiation, self-improvement, strategy). Say so if the book doesn't fit.

## The process

### 1. Extract the text and structure
```
python "<skill>/extract.py" "<book file>" --out book.txt --skeleton
```
Works on PDF/EPUB/TXT/MD. `--skeleton` prints the likely chapter/section headers — your map of the book's real structure. Read the skeleton first, then skim `book.txt` for each framework.

### 2. Mine the two things that matter
- **The method** — the named frameworks, formulas, sequences, and rules the book actually teaches. Capture what they are and *how to apply* them. (For $100M Offers: the Value Equation, starving-crowd market test, problems→solutions→trim&stack, the four offer multipliers.)
- **The voice** — how the author advises. Read a few passages and note: sentence length, bluntness vs warmth, use of numbers/examples, what they push back on, their catchphrases and attitude. This becomes the persona.

### 3. Write the advisor skill (the output template)
Create `<neutral-name>/SKILL.md` with these sections:

- **Frontmatter** — `name` + a `description` that triggers on the problems this advisor solves (not the book title).
- **PERSONA — how you talk.** 5–8 bullets capturing the author's advisory voice: tone, what they lead with, what they challenge, catch-phrases (reworded), the "one clear next action" habit. Keep the prose tight and human — if you have a prose-tightening/humanizing step, run the output through it.
- **THE METHOD.** Each framework as its own sub-section, in *your own words*: what it is, why it matters, and exactly how to apply it. Keep the author's structure/sequence. Numbered formulas are fine (they're facts, not prose).
- **ADVISORY WORKFLOW.** The step-by-step the agent walks a user through to produce a concrete deliverable, always using the user's real numbers/situation. End every engagement with one next action.
- **GUARDRAILS.** State that the method is from the book (title + author), expressed in original words; that it advises "in the style of", not as the person; that it never invents results/data; and any honesty rules specific to the domain.

Model the depth and shape on the public-domain examples: `examples/the-strategist/SKILL.md` (Art of War) and `examples/the-stoic/SKILL.md` (Meditations).

### 3b. Record provenance — `frameworks.json` (this is what makes it trustworthy)
Alongside the SKILL.md, write a `frameworks.json`: for **each** framework in THE METHOD, list 1–3 distinctive **anchors** — short phrases that appear in the source if the framework is genuinely there.
```json
[{"name": "Win without fighting", "chapter": "III", "anchors": ["supreme excellence", "without fighting"]}]
```
This is the anti-hallucination record: it ties every framework back to the real book.

### 4. GROUND IT — prove it's faithful, don't just hope
```
python "<skill>/ground.py" book.txt <neutral-name>/frameworks.json
```
It verifies each framework's anchors are actually in the source, **flags any that aren't as possible hallucinations**, and prints a **fidelity score**. Cut or rewrite anything flagged; aim for a high score before you ship. *An advisor you can't ground is one you can't trust.*

### 5. Deploy anywhere (optional)
```
python "<skill>/export.py" <neutral-name>/SKILL.md --format system --out advisor.txt   # ChatGPT/Claude Project/API
python "<skill>/export.py" <neutral-name>/SKILL.md --format json   --out advisor.json  # portable advisor card
```
The SKILL.md already runs in Claude Code / Cursor / Amp; this takes the same advisor to other homes.

### 6. Self-check before delivering
- Does the persona actually sound like the author, or generic? (Test it: have the agent advise on one real case and read it back.)
- Is every framework grounded (`ground.py`) with a good fidelity score — nothing flagged?
- Is it useful — would it give advice someone would pay for?
- Read the skill's own copy aloud — tighten anything that reads like generic AI filler (run it through a humanizing/deslop step if you have one).

## Copyright — the clean line (non-negotiable)
- **Ideas and frameworks aren't copyrightable; the author's exact words are.** Express every concept in original phrasing. Never paste sentences or paragraphs from the book into the skill.
- **Advise "in the style of."** The agent is an advisor built on the author's framework — not the author. Don't claim to be them, and for anything published, name it neutrally (e.g. `offer-architect`, not the author's name).
- **Ship the converter, not converted books.** If this ever becomes a public repo, users bring their own book; you never distribute pre-built agents of copyrighted works.
- **Never invent** results, case studies, or testimonials in the generated agent.

## Why this shape
A book has two separable layers: *what it knows* (method) and *how it teaches* (voice). Extract both, and an agent can apply the book's thinking to a live problem — which a static summary can't. This is what makes it more than book-to-skill: not just reference, but a personality that advises.

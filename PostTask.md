# Post-task improvements

Things the skill *can* do better in some environments, but doesn't do by default. The
production setup (mostly Linux servers, no desktop browser) ignores everything in this file. An
agent should only act on an item here when the user asks for it, or when the environment clearly
already has what the item needs.

---

## 1. Automated page checks with Playwright (disabled)

**Status:** disabled since 2026-10-08. Playwright is no longer in `requirements.txt`, and
`AGENTS.md` §4 doesn't call it. `scripts/check_page.py` is still in the repo, unchanged, so it
can be switched back on.

**Why it's off:** it needs a headless Chromium (about 150 MB plus system libraries), which is a
hassle on lean Linux servers and in CI. Without it, §4 relies on the checklist, two `grep`
checks (leftover `[placeholders]` and `data-sample` marks), and whatever preview the
environment already has.

### What it adds when it's on

`python scripts/check_page.py _output/<slug>/index.html` renders the page in Chromium at 1440,
1024, 768, 375 and 320px, and reports FAILs and WARNs for:

- horizontal overflow and clipped text
- tap targets under ~44px on mobile
- JavaScript errors, and whether the mobile menu opens and closes
- leftover `[placeholders]` and agent-written `data-sample` copy
- text contrast below ~4.5:1
- print mode: page count, black on white, no nav or buttons

Other modes:

- `--template` checks a template itself (bracket placeholders are expected there).
- `--compare <other.html>` pixel-diffs two versions, e.g. before and after editing a template.

The same Playwright install also lets the agent take desktop and phone screenshots to look at a
page before handing it off.

**What it has caught so far:** undersized tap targets in 9 profile templates, a 1px overflow in
Playful Dev Folio, and contrast problems in 9 of the 14 profile templates (the worst is Playful
Personal at about 2:1, white on pink/yellow; still unfixed).

### When it's worth turning on

- On a developer machine (Windows, macOS, desktop Linux) where building and editing templates.
- Before changing a template's CSS, layout or `--accent`, or adding a new template.
- When the user asks for proof the page works at every width, or for screenshots.
- Never required to build or publish a page.

### How to turn it on

Install it (Ubuntu, inside the skill's `.venv`; see README "Installing on Ubuntu"):

```bash
pip install "playwright>=1.50"
python -m playwright install --with-deps chromium   # may ask for sudo, installs Chromium's system libraries
python scripts/check_page.py templates/minimal-professional/template.html --template
```

On Windows or macOS, `pip install "playwright>=1.50"` then `python -m playwright install chromium`.

To make it part of the workflow again:

1. Add `playwright>=1.50` back to `requirements.txt`.
2. In `AGENTS.md` §4, say that when Playwright is available, `python scripts/check_page.py
   _output/<slug>/index.html` runs the whole checklist in one go (fix all FAILs; review WARNs).
3. In `AGENTS.md` §3.1, mention that `check_page.py` lists `data-sample` marks as WARNs.
4. In the README scripts table, change `check_page.py` back from "Disabled for now".

Proposal.md (§ on sample content) also plans a `check_page.py --final` mode that fails on
`data-guess` marks. That depends on this being turned back on.

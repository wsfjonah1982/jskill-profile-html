# Agent Instructions

You are an agent working with the **profile-html-templates** library. Your job is to take a
person's, company's, or business's information and turn it into a **single, finished, responsive
HTML page** — by picking the right template, cloning it, and replacing the placeholder content
with the real content. The page must look right on both a phone and a desktop; there is no
separate "mobile version," it's one file that adapts.

This document is the shared operating manual: the workflow, the build rules, and the output
contract that every page follows. What changes by industry (its design, the content it needs,
and which templates suit it) lives in one `Industry.md` per industry under `industries/`. Read
Step 0 first, every time.

---

## Step 0 — Pick the site's industry

Before anything else, work out what kind of site this is:

| The user wants... | Industry | Go to |
|---|---|---|
| A bio, résumé/CV, portfolio, startup pitch one-pager, agency/company homepage, or personal brand page | **OPC (one-person company)** | `industries/opc/Industry.md` |
| An online store / product catalog with a cart | **E-commerce** | `industries/ecommerce/Industry.md` |
| A restaurant, cafe, or similar food-service site with a menu | **Restaurant/cafe** | `industries/restaurant/Industry.md` |
| An online course, cohort program, or coaching offer | **Education** (courses/coaching) | `industries/education/Industry.md` |

If it's ambiguous which of these four it is, ask the user rather than guessing — the whole
downstream flow (design, intake questions, relevant templates) differs by industry.

**If the request clearly doesn't fit any of the four at all** (e.g. a blog/magazine, a real
estate listing site, a nonprofit/donation page, an event/conference page, a wedding site, or any
other site type with no `Industry.md` here) — **this skill is out of scope for it. Say so plainly
("No — this skill only builds OPC/profile, e-commerce, restaurant/cafe, and education
(course/coaching) pages") and stop.** Don't ask clarifying questions to try to fit it into one of the four, don't
improvise a new industry from scratch, and don't build a best-effort page outside this list.

Read the chosen industry's `Industry.md` once Step 0 has routed you. Each one has the same
parts:

1. **Design**: how pages in this industry should look and feel, and what they lead with.
2. **Content**: the intake questions and the content a page needs.
3. **Relevant templates**: which shared templates suit this industry, and when to pick each.
4. **Build** notes, limits and finish checks specific to the industry (data arrays, demo
   carts or forms, extra interactions to test).

Everything that doesn't change by industry stays in this document: Step 1 (precheck), Steps 5–8
(previews, build, publish), §3 (adapting a template), §3.1 (writing copy and marking sample
content), §4 (responsive checklist), §5 (designing a missing section), §6 (no fabricated proof
points), and §7 (output contract). Don't duplicate those inside an `Industry.md`; reference them.

**Templates are shared.** All templates live in one `templates/<slug>/` folder at the skill
root, with their metadata in `templates/index.json`. An `Industry.md` names the templates that
suit it, and the same template can be named by more than one industry.

---

## 1. The full workflow

For every request, follow this sequence. Do **not** skip the intake step or the preview step.

### Step 1 — Precheck, then check `_input/`

**Once per session** (not for every single page — just the first time this skill runs in a given
environment, or after touching `credential.json`/`config.json`), run `python scripts/precheck.py`
before doing any real work. TOS publishing is **optional**, and precheck covers both setups:

- **TOS configured** (access key, secret key and bucket all set, in `credential.json` or the
  matching environment variables): precheck confirms they load, then does a live
  publish→fetch→unpublish round-trip.
- **TOS not configured** (none of them set): precheck passes. Finished pages are kept locally
  (see §7). If `config.json` sets `local_publish_dir`, precheck checks that the folder is
  writable.
- **TOS partly configured:** precheck fails, because that's almost always a typo or a missing
  key, not a choice.

If it reports a failure, fix that first. Don't start building against a setup you haven't
confirmed works.

This skill defaults to reading prepared content rather than always starting from a live Q&A.
Before asking the user anything (Step 2 below):

1. Look for `_input/brief.md`. If it exists, read it — it already answers the industry, mood,
   name, and the content fields for whichever industry block is filled in. Copy `_input/brief.template.md`
   to `_input/brief.md` first if only the template is present and unfilled.
2. Look in `_input/images/` (and `_input/videos/` if relevant) for photos/logos/video the brief
   references by filename.
3. Only ask the user about fields that are **missing, blank, or ambiguous** in `_input/brief.md`
   — don't re-ask what it already answered.
4. If `_input/brief.md` doesn't exist at all, fall back to the fully interactive flow exactly as
   written below and in the industry's `Industry.md` — nothing changes in that case.

This step applies identically whichever industry Step 0 routed to.

### Step 2 — Ask about purpose and mood

Ask the questions in the **Content** section of the industry's `Industry.md`, per Step 1: only
what `_input/brief.md` didn't already answer. Wait for the answers. If the brief's **Mood**
field is filled in, use it — don't re-ask. If it's blank or vague (e.g. "nice"), ask; don't
guess the mood from the rest of the brief.

### Step 3 — Gather the actual content

Read from `_input/brief.md` (per Step 1) first; ask for (or read from a file/résumé/notes the
user provides directly) whatever it didn't cover. The industry's `Industry.md` lists the content
a page needs. If the user gives you a raw document (résumé PDF, LinkedIn export, company
one-pager, menu), extract it from that instead of re-asking for everything.

**You write any copy the user doesn't, yourself.** No script or third-party model API does
this. If the user would rather not write the copy, or says to "just fill in" what's missing, you
draft it from what they gave you. If they give only part of the content, you write sample copy
for the gaps. Either way, follow §3.1: never invent proof points, and mark every sample line.

### Step 4 — Pick candidates from the industry's relevant templates

Start from the **Relevant templates** in the industry's `Industry.md`, and read their entries in
`templates/index.json`. Match the stated mood (and, for OPC, `profile_type`: personal / company /
both) against each template's `mood`, `tone`, `best_for`, `formality`. **Pick three templates**
that are genuinely different from each other — not three variations on the same look. If the
industry lists fewer than three, or its `Industry.md` says a preview round isn't needed, follow
that.

### Step 5 — Build a hero-section preview of each candidate

For each of the 3 candidates:

1. Read the template's `template.html` to learn its structure and design system.
2. Take the **nav + hero section only** (the top of the page — name/company, tagline, primary
   CTA).
3. Replace the placeholder content with the user's **real** name/company and tagline — make the
   preview real, not generic.
4. Save each as a standalone file, e.g. `previews/01-<slug>.html`. It must be openable on its own
   (inline CSS/fonts — the templates already are self-contained single files, so this is just a
   truncated copy).

### Step 6 — Open all 3 previews, send paths, wait for the pick

Open each preview in the browser. Message the user:

> "Three options to compare:
>
> 1. **<Template A>** — <one-line tone description>
>    `/path/to/previews/01-template-a.html`
> 2. **<Template B>** — <one-line tone description>
>    `/path/to/previews/02-template-b.html`
> 3. **<Template C>** — <one-line tone description>
>    `/path/to/previews/03-template-c.html`
>
> Which one feels right? (Resize your browser window, or view on your phone, to check how it
> adapts.)"

Wait for the user to pick.

### Step 7 — Build the full page in the chosen template

1. Clone the chosen template's file into `_output/<slug>/` per §7 (or wherever the user directed
   instead).
2. Fill in every section per the rules in §3.
3. If the user's content needs more repeating items than the template's demo holds (more
   services, more work samples), duplicate the existing card/item markup — the CSS `grid`/`flex`
   layouts already reflow, so added items should not break the layout. If there are fewer items,
   remove the extras.
4. **If the content needs a section type the template doesn't have** (e.g. a pricing table, a
   FAQ, a team grid), design it from scratch using the template's design system — same fonts,
   colors, spacing scale, corner treatment, and component style as the rest of the page. Don't
   switch templates, don't import a different visual language. (See §5.)
5. Verify responsiveness (see §4) before calling it done.

### Step 8 — Publish the final page, send its location

Open the finished page in the browser to sanity-check it, then run `scripts/publish_site.py`
(see §7 below — this is the default last step, not optional) and message the user:

> "Done. Your page is live at `https://<bucket>.<tos-endpoint>/site/manual/<slug>/index.html`.
>
> [One line about which template you picked and why, plus any caveats.]"

If TOS isn't configured, the script keeps the page locally and prints its file location
instead. Say "Your page is ready at `<path>`" rather than "live", because it isn't public.

This applies to **every artifact you produce**: open hero previews locally and send their file
path (they're a mid-process comparison step, not the deliverable); the final page gets opened,
published, and handed off by the location `publish_site.py` prints.

---

## 2. What's in `templates/index.json`

One entry per template, for every industry. All paths in it are relative to the skill root.
Which industry a template suits is in the `Industry.md` files, not here.

```jsonc
{
  "slug": "dark-tech-modern",
  "name": "Dark Tech Modern",
  "tagline": "Dark canvas with a violet-to-cyan glow, built to pitch a product or business idea.",
  "profile_type": ["personal", "company"],
  "mood": ["modern", "confident", "technical", "ambitious"],
  "occasion": ["startup / SaaS landing page", "developer personal site", ...],
  "tone": ["sleek", "sharp", "forward-looking", "credible"],
  "formality": "medium",
  "density": "medium",
  "scheme": "dark",
  "sections": ["nav", "hero", "problem-solution", "features-grid", "metrics", "cta", "contact", "footer"],
  "best_for": "...",
  "avoid_for": "..."
}
```

| field | how to use it |
|---|---|
| `profile_type` | Hard filter first: does the template fit `personal`, `company`, or `both`? |
| `mood` | emotional adjectives — match against the user's stated feeling. |
| `occasion` | example use cases — soft signal, not a hard filter. |
| `tone` | voice/personality — match descriptors like "playful", "sober", "literary". |
| `formality` | sanity-check against the audience (a low-formality template for a formal advisory firm is a mismatch worth flagging). |
| `density` | how much content per screen the template comfortably holds. |
| `scheme` | `light` / `dark`. Hard signal if the user explicitly wants one. |
| `sections` | the section blocks the template ships with — tells you what's already there vs. what you'd need to design per §5. |
| `best_for` / `avoid_for` | lead with `best_for` when narrating your pick; treat `avoid_for` as a soft warning. |
| `inspired_by` | (some templates) the open-source template whose visual style it was rewritten from. Credit only — no code was copied; don't treat it as a matching signal. |
| `screenshot_desktop` / `screenshot_mobile` | paths to `screenshot-desktop.png` / `screenshot-mobile.png` inside each template's folder (`null` or empty if the template has none yet) — glance at them to compare candidates before building previews. |

---

## 3. How to adapt a chosen template

### Always preserve (this IS the design system)

- **Fonts** — whatever is imported from Google Fonts. Every template routes fonts through
  variables (`--font-display` / `--font-body` / `--font-mono`, or `--font` / `--mono`). Never
  substitute on your own; if the user asks for a different font, change the Google Fonts `<link>`
  and the matching variable only.
- **Color palette** — all colours live in CSS custom properties under `:root` (see the THEME
  comment at its top). Never recolor on your own. If the user asks for their brand colour,
  change `--accent` only — derived shades follow it — plus any secondary colours the THEME
  comment lists if they clash. For a dark accent, also set `--on-accent` (where present) to
  `#ffffff` so button text stays readable.
- **Layout grid & spacing scale** — the `clamp()` fluid type, the grid/flex structure, the padding rhythm.
- **Component classes** (e.g. `.card`, `.hero`, `.nav-link`) — they carry the visual identity.
- **The responsive behavior already built in** — breakpoints, the mobile nav toggle script, fluid type. Don't rewrite it; extend it.
- **Decorative elements** — borders, shadows, gradients, corner marks — they're part of the system.

### Always replace (this is the user's content)

- Name / company name, tagline, headings.
- Bio / about copy, service or experience descriptions, the business-idea pitch text.
- Proof points: work samples, case studies, testimonials, metrics.
- Contact details, social links. Keep only channels the user actually has — delete the other
  buttons/cards (email, LinkedIn, GitHub, X, website, …) rather than leaving placeholders or
  inventing a link. **Never put a home address or personal phone number on a public page** unless
  the user explicitly asks; a city or country is enough for "Based in".
- Bracketed text (`[Skill]`, `[Method]`, `[Value]`) is always the user's content — never ship it,
  and never treat bracketed demo examples as the user's real skills or results.
- Image placeholders — every `<div class="img-placeholder">` sits inside a sized slot (e.g.
  `.portrait`, `.avatar`, `.hero-art`, `.laptop .screen-inner`, `.shot`, `.thumb`); replace the
  placeholder div with a real `<img>` inside that slot, at the slot's aspect ratio, using only a real photo the user provided in `_input/images/`
  (per Step 1/brief.md). Run it through `scripts/fit_image.py --aspect <W:H>` first (matching
  the slot's aspect ratio) so it's cropped and sized to drop in cleanly — no network call, no
  credentials, purely local, and it strips EXIF (including GPS location). **This skill never
  generates images.** If no user photo exists for a slot, leave the template's placeholder block
  rather than breaking the layout or inventing one.

### Adding or removing repeated items

Templates use one markup block per repeatable item (a service card, a work-sample tile, a nav
link). To add more, duplicate that block and edit its content — the surrounding `grid`/`flex`
container already reflows. To remove, delete the block. Don't hand-adjust column counts or
widths; the CSS handles it.

### 3.1 Writing copy yourself, and marking sample content

You write all page copy yourself. No script or external model API does it for you. There are
two cases, and only the second one gets marked:

- **Drafting from the user's real material.** The user gave you facts but no finished wording
  ("write my bio from this résumé", "make the brief sound good"). Write it in the template's
  mood. This is the user's content in your words, so it isn't sample content. Every claim must
  still trace back to something they gave you. In the handoff, say which parts you wrote.
- **Sample content for gaps.** A field is blank, and the user doesn't want to fill it in. They
  may have said so up front ("fill in whatever's missing"), or you asked once (Step 1/3) and
  they said to go ahead. Write a generic stand-in in the right voice, and mark it.

**What can be sampled:** descriptive copy only. That means a tagline, an about paragraph,
service/feature/product/menu-item descriptions, course module summaries, section intros and CTA
lines. Keep it generic ("Clear, calm design for growing teams"). Don't state specific facts.

**What's never sampled (§6):** metrics, testimonials and reviews, client or employer names,
awards, credentials, years of experience, prices, hours, addresses and contact details. Don't
invent these, even with a mark on them. Keep the template's placeholder, drop the section, or
ask for them.

**How to mark it:** put `data-sample="<what it stands in for>"` on the smallest element that
holds the sample text, e.g. `<p class="bio" data-sample="about paragraph">…</p>`. The page
still looks finished, and the marks don't show on screen. They're what lets you, the user and
`scripts/check_page.py` (it lists them as WARNs) find every stand-in later. Then:

1. When you send the hero previews (Step 6), say if the tagline shown is a sample.
2. In the final handoff (§7), list every sample item under its own **"Sample content to
   replace"** line. Don't put it under general caveats.
3. When the user sends the real text, swap it in and remove that `data-sample` attribute.

---

## 4. Responsive checklist (must pass before you're done)

Every page produced with this skill must work on a phone and a desktop from **one HTML file** —
no separate mobile template, no server-side device detection. Before finishing, verify:

- [ ] `<meta name="viewport" content="width=device-width, initial-scale=1">` is present.
- [ ] Body text and headings use fluid sizing (`clamp()` or breakpoint-based `font-size`), not
      fixed pixel values that overflow small screens.
- [ ] Multi-column sections (services, work grid, features) collapse to a single column below
      the template's mobile breakpoint (typically ~640px).
- [ ] The nav collapses to a hamburger/menu toggle on small screens if it has more than ~3 links.
- [ ] No element causes horizontal scroll on a 375px-wide viewport (check images, long
      unbreakable text like URLs, and fixed-width containers).
- [ ] Tap targets (buttons, nav links) are at least ~44px tall on mobile.
- [ ] Images use `max-width: 100%; height: auto;` so they scale down instead of overflowing.
- [ ] Print / Save as PDF still works: every template ships a print stylesheet and a footer
      "Save as PDF" button. If you added a section (§5) or a dark block, check print preview
      (or a headless `page.pdf()`) — black on white, no nav/buttons, no card split across pages.
- [ ] Text contrast: body text and button text meet ~4.5:1 against their background — check
      again after any `--accent` change, and re-run `python scripts/theme_fallbacks.py <file>` so
      older browsers get the new colours too.
- [ ] Actually check it at a phone width (375–414px) and a desktop width (1280px+) before
      declaring the page done. If Playwright is available, `python scripts/check_page.py
      _output/<slug>/index.html` runs every check in this list in one go (fix all FAILs; review
      WARNs). Otherwise use whatever browser-preview/screenshot capability this
      environment provides (Playwright, a headless-browser CLI, an IDE live preview, or manual
      resize in any browser). If a template has interactive JS (an e-commerce cart, restaurant
      menu tabs, a course accordion, etc.), exercise it at both widths, not just render it.
- [ ] If no such capability exists in this environment, do a careful manual review of the CSS
      breakpoints and JS logic instead, and say plainly in your output (§7) that visual
      verification wasn't performed — don't claim it passed a check you couldn't run.

---

## 5. Designing a missing section (extending a template)

Some briefs need a section type a template doesn't ship with — e.g. a pricing table, an FAQ
accordion, a team grid, a press/logo strip. Design it using the template's existing system:

- **Same fonts and type scale** as the rest of the page (h1/h2/body/label weights, sizes, tracking).
- **Same color palette** — reuse existing `:root` variables; if you need an "accent" or "muted"
  tone that doesn't exist, use the closest existing variable rather than inventing a new color.
- **Same spacing rhythm** — match the padding/margin scale and grid-gap values already in use.
- **Same component grammar** — if cards elsewhere use a border + shadow + icon-over-title
  structure, new cards should too.
- **Same responsive pattern** — the new section must collapse the same way the rest of the page
  does (multi-column → single column on mobile).

Test: drop the new section between two existing ones. If it looks like a natural part of the
same page, you succeeded. If it looks grafted on from elsewhere, redo it.

---

## 6. Common pitfalls

- **Don't skip Step 1's precheck** the first time this skill runs somewhere — finding out
  credentials or publishing are broken after building the page wastes the whole build. (With no
  TOS configured, it's a quick check and passes.)
- **Don't skip intake for anything the brief leaves blank** — "person vs. company" and mood
  change the template pick entirely. But don't re-ask what `_input/brief.md` already answers
  (Step 1); ask only about missing or ambiguous fields.
- **Don't skip the hero previews.** Showing beats describing.
- **Don't substitute fonts or recolor** — that's the design system, not decoration.
- **Don't mix sections from two different templates** in one page — pick one, extend it (§5) if needed.
- **Don't ship a page you haven't checked at a mobile width.** "It's just CSS Grid, it'll be fine"
  is not verification — actually look at it narrow.
- **Don't invent fake metrics/testimonials as if they were the user's real data.** Placeholder
  numbers in the templates are demo content; when building the real page, use only what the user
  gave you, and leave a section out (or mark it TODO) rather than fabricate proof points.
  Sample content (§3.1) covers descriptive copy only, never proof points.
- **Don't ship unmarked sample copy.** Any text you made up to fill a gap gets a `data-sample`
  attribute and is listed in the handoff (§3.1). Otherwise it looks like the user wrote it.

---

## 7. Output contract

Write the finished page to `_output/<slug>/index.html` by default (`<slug>` = a short kebab-case
name for this site, e.g. `jane-doe-portfolio`), with an `assets/` folder alongside it for any local
images/videos copied in from `_input/` — unless the user has told you to put it somewhere else,
in which case follow that instead. Hero previews (Step 6) can live in a `previews/` folder next
to wherever you're building, they don't need to go in `_output/`.

For hero previews (Step 6), do both:

1. **Open the file** in whatever preview capability this environment has (a browser, an IDE
   preview pane, etc.). If nothing can render it, skip this and say so.
2. **Send the user the absolute file path** in your message, on its own line.

**For the final page, always publish it — this is the default last step, not an optional
extra.** Once it passes §4's responsive/interaction checklist, run
`scripts/publish_site.py --dir _output/<slug> --slug <slug>`. Where the page goes depends on
the setup (Step 1):

| Setup | What `publish_site.py` does | What it prints |
|---|---|---|
| TOS configured | pushes the site to BytePlus TOS object storage, public-read | the public URL |
| TOS not configured, `local_publish_dir` set in `config.json` | copies the site to `<local_publish_dir>/<slug>/` (a mounted share, a synced folder, a web server's root…), replacing any older copy | a `file://` location |
| TOS not configured, no `local_publish_dir` | leaves the site in `_output/<slug>/` | a `file://` location |

**Other file systems.** If the user names a folder to deliver into (a network drive, a synced
cloud folder, a web root), pass `--local-dir <folder>`. That copies the site to
`<folder>/<slug>/` and skips TOS for that run. If the environment only offers an external
storage or hosting service through a tool (a cloud drive connector, an artifact host, …),
*offer* it in one line, but don't upload without the user's OK. The skill's default only covers
TOS and local folders.

Then report to the user:
- **The location** `scripts/publish_site.py` prints. That's the public URL with TOS, otherwise
  the absolute local path (convert the `file://` URI to a plain path). Lead with it.
- A one-line note on which template you picked and why (the tone match).
- **Sample content to replace**, if there is any (§3.1): one short line per `data-sample` item,
  e.g. "about paragraph, the three service descriptions". Leave this line out if there's none.
- Any caveats (e.g. "left the testimonial section as a placeholder since you didn't give me one
  yet", "added a pricing section from scratch using the template's card style since none of the
  templates ship with one", or "couldn't visually verify responsiveness — no browser tooling in
  this environment").

With TOS, this pushes real files to a public bucket. Say so plainly when you do it, but don't
gate it behind a question each time. Running `publish_site.py` on the finished page is standard
behavior for this skill, every time, unless the user has explicitly said they just want the local
file. Republishing under the same slug is safe: `publish_site.py` replaces whatever is under that
slug with the new build. That means stale TOS objects are deleted, or the old copy in
`local_publish_dir` is replaced. On TOS, HTML is served with `Cache-Control: no-cache` so the
update shows immediately. Slugs must be lowercase kebab-case (letters, digits, hyphens), and
both scripts refuse anything else. Use `scripts/unpublish_site.py --slug <slug>` only to take a
site down entirely. It removes the TOS copy, or the `local_publish_dir` copy, and never the
build in `_output/`. Use `scripts/list_sites.py` to see everything that's currently published.

Do not narrate every step you took. The user wants the location + a one-line rationale.

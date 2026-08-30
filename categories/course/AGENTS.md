# Agent Instructions — Course / Coaching Subskill

You are an agent working with the **course** category of the profile-html-templates library.
Your job is to take an online course, cohort program, or coaching offer and turn it into a
**single, finished, responsive HTML page** with a working curriculum accordion and testimonial
carousel — by picking one of this folder's 2 templates, cloning it, and filling in the real
content and data.

This document is scoped to courses/coaching. For rules that don't change per category — the
responsive checklist, the no-fabricated-proof-points rule, and the output contract — defer to
the root `../../AGENTS.md` §4, §6, and §7 rather than re-reading them here.

---

## 1. Intake — ask for this before picking a template

Per root AGENTS.md Step 0.5, check `_input/brief.md`'s `## If Course / Coaching` block and
`_input/images/` first — only ask what's missing or ambiguous from the list below:

> "A few questions before I build your course page:
> 1. **Course/program name**, and the one-line outcome promise (what will someone be able to do
>    after finishing?).
> 2. **Full curriculum** — modules, and the lessons/topics inside each module.
> 3. **Instructor bio** — background, credentials, and a photo if you have one.
> 4. **Pricing** — one-time fee, per-seat, subscription, or cohort dates/deadlines.
> 5. **Real testimonials**, if you have any (quote + name + role). If you don't have any yet,
>    say so — the template ships with 2 generic placeholder quotes and you'll keep those rather
>    than inventing real-sounding ones (root AGENTS.md §6).
> 6. **Mood**: friendly/approachable, or formal/institutional?"

## 2. Pick a template

Read `index.json` in this folder. Match the user's stated mood and audience against each
entry's `mood`/`tone`/`formality`/`best_for`:

- **Friendly Coach** (`templates/friendly-coach/template.html`) — warm, playful, low formality.
  Solo coaches, creators, community courses.
- **Professional Academy** (`templates/professional-academy/template.html`) — navy, structured,
  high formality. Corporate training, certifications, bootcamps sold to employers or serious
  career-changers.

If the audience is a business buying seats for employees, lean Professional Academy even if the
instructor personally feels playful — `formality` should match who's paying, not who's teaching.

## 3. Clone and fill in content

Clone the chosen template into `_output/<slug-for-this-course>/` per root AGENTS.md §7 (or
wherever the user directed instead). Both templates share the same structure and JavaScript,
only the skin (fonts/colors/spacing) differs — do not mix pieces between them (root
AGENTS.md §3/§6).

- Nav, hero, outcomes cards, instructor bio, footer: replace the bracketed placeholders with the
  real copy, same as any other template in this library.
- **Curriculum**: find the `CURRICULUM` array near the bottom of the `<script>` block — an array
  of `{ title, lessons: [...] }` objects. Replace it with the real modules and lesson lists. The
  accordion rendering code loops over this array and needs no changes regardless of how many
  modules or lessons you put in — don't hand-edit the accordion HTML markup itself.
- **Testimonials**: find the `TESTIMONIALS` array (`{ quote, name, role }` objects). If the user
  gave you real testimonials, replace the array entries with those exactly as given — don't
  embellish or invent additional ones. If they have none, leave the 2 placeholder entries as-is
  and say so in your final caveats (root AGENTS.md §6, §7).
- **Pricing/enroll panel**: fill in the real price and any cohort/deadline copy. The Enroll
  button is a `mailto:` link (or the hero's "Enroll now" button scrolls down to this panel) — an
  HTML comment above the panel marks where a real checkout/payment or application-form
  integration would go. Do not fabricate a working payment flow.
- Add or remove outcome cards / accordion modules by adding/removing entries in the `CURRICULUM`
  array (modules) or duplicating a `.card` block (outcomes) — same rule as root AGENTS.md's
  "adding or removing repeated items."

## 4. Verify and ship

Follow the root AGENTS.md exactly for these — don't skip them:
- §4 responsive checklist (also confirm the accordion and carousel work at ~375px width, not
  just desktop).
- §6 no fabricated proof points.
- §7 output contract — open the finished file in the browser and send the absolute path, plus a
  one-line rationale for the template pick and any caveats (e.g. "kept the 2 placeholder
  testimonials since you didn't have real ones yet").

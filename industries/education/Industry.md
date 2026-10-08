# Education (Courses / Coaching)

Pages for an online course, cohort program, or coaching offer: one finished, responsive HTML page
with a working curriculum accordion and testimonial carousel.

This guide covers what's specific to courses and coaching. For everything shared (precheck,
§3.1 sample content, §4 responsive checklist, §6 no fabricated proof points, §7 output
contract), follow the root [`../../AGENTS.md`](../../AGENTS.md).

---

## 1. Design

A course page sells a transformation, so the design leads with the outcome and makes the
curriculum easy to scan.

- **Outcome first.** The hero states what someone will be able to do after finishing, then an
  outcomes card row backs it up.
- **The curriculum is the product.** Modules sit in an accordion so a long syllabus stays short
  on a phone. Keep module titles short and benefit-led.
- **The instructor builds trust.** Give them a bio section with real credentials and a photo if
  there is one.
- **Social proof, but only real.** The testimonial carousel shows real quotes. With none, it
  keeps the 2 generic placeholders and the handoff says so.
- **One enrol path.** Price, cohort dates or deadlines, and a single Enrol button. The hero CTA
  scrolls to that panel.
- **Formality follows the payer.** Friendly and rounded for individuals, navy and structured
  when an employer buys seats.

## 2. Content

Check `_input/brief.md`'s `## If Education (Course / Coaching)` block and `_input/images/` first (root
Step 1). Ask only what's missing or ambiguous from the list below:

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

## 3. Relevant templates

Both are in the shared `templates/` folder at the skill root. Full metadata is in
[`templates/index.json`](../../templates/index.json). Match the user's stated mood and audience
against each entry's `mood`/`tone`/`formality`/`best_for`:

- **Friendly Coach** (`templates/friendly-coach/template.html`) — warm, playful, low formality.
  Solo coaches, creators, community courses.
- **Professional Academy** (`templates/professional-academy/template.html`) — navy, structured,
  high formality. Corporate training, certifications, bootcamps sold to employers or serious
  career-changers.

If the audience is a business buying seats for employees, lean Professional Academy even if the
instructor personally feels playful — `formality` should match who's paying, not who's teaching.

## 4. Build

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

## 5. Verify and ship

Follow the root AGENTS.md exactly for these — don't skip them:
- §4 responsive checklist (also confirm the accordion and carousel work at ~375px width, not
  just desktop).
- §3.1 sample content: mark any copy you made up to fill a gap with `data-sample`, and list it
  in the handoff.
- §6 no fabricated proof points.
- §7 output contract — publish via `scripts/publish_site.py` and lead with the location it
  prints (the public URL, or the local path when TOS isn't configured), plus a one-line
  rationale for the template pick and any caveats (e.g. "kept the 2 placeholder testimonials
  since you didn't have real ones yet").

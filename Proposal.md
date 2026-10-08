# Proposal: Fill missing content so the customer always gets a page

**Status:** draft for review · **Date:** 2026-10-08 · **Affects:** `AGENTS.md` §3.1, §6, §7,
the three category docs, `_input/brief.template.md`, `check_page.py`, `publish_site.py`

## 1. Problem

Customers stall at intake. A half-filled brief turns into a long round of questions, and someone
who doesn't yet know their tagline or how to describe their work never reaches a page they can
react to. Most people find it much easier to fix a draft than to fill in a blank form.

The current rule (`AGENTS.md` §3.1) already helps. The agent writes copy itself and fills gaps
in descriptive copy with marked samples. It stops there, though. If too much is missing, the
agent still has to ask, and nothing tells the customer clearly what they should do next.

## 2. Goal

From a thin brief, the agent should:

1. Get the customer a **real, viewable page in one pass**, with no more than one short round of
   questions.
2. **Fill a few gaps, all marked.** Each filled item is either sample wording or one specific,
   labelled guess. Nothing made up can be mistaken for something the customer said.
3. **Turn the gaps into the next step.** The customer gets a short list to confirm or provide,
   ordered by impact.

**Scope for now: guess little, leave out the rest.** The only guess is the two-phase engagement
structure (§3). Any other content that isn't provided is left off the page for now and listed
as "add later". That keeps the page short and honest. Guessing more can be considered once this
has been tried with real customers.

There's one thing this proposal doesn't change: **facts that someone could rely on and be hurt by
are never guessed.** That covers proof points, prices, hours, contact details and credentials.

## 3. What the agent may fill in: four tiers

Every content field belongs to one of four tiers. The tier decides whether the agent can fill
it, how the filled item is marked, and whether it blocks the final publish.

| Tier | What it covers | Agent may… | Marked as | Blocks final publish? |
|---|---|---|---|---|
| **A. Decisions** | mood, template, section order, CTA type, which sections to include | decide, inferring from context | not marked on the page; named in the handoff | no |
| **B. Wording** | tagline, about paragraph, section intros, CTA lines, descriptions of items the customer *named* | write sample copy | `data-sample="<field>"` | no, just listed |
| **C. Engagement structure** | the project or service phases: **Discovery** and **Rollout only** | guess those two phases | `data-guess="<field>"` + a manifest entry | **yes**, until confirmed or removed |
| **D. Everything else not provided** | skills, platforms, service or product lists, menu items, course modules, metrics, testimonials, client/employer names, awards, credentials, experience, prices, hours, address, contact | **don't fill.** Leave the section off, or keep a required placeholder (contact) | listed under "add later" in the handoff | contact only (see below) |

### Tier C: the only guess

When the page has a project or service structure section ("How I work", "Engagement",
"Process"), and the customer didn't describe one, the agent adds two phases:

- **Discovery.** Understand the customer's workflow, data and success criteria before building.
- **Rollout.** Take the work into production, then monitor it and hand it over.

The agent uses neutral wording in the page's mood. It doesn't add any other phases, such as
Pilot, Build or Training, and it doesn't state durations, deliverables or results. The
customer adds those, or confirms the two phases as they are.

This fits a forward-deployed engineer, consultant or agency page. For categories with no
process section (e-commerce, restaurant), nothing is guessed.

### Tier D: left out for now

Content in Tier D that the customer didn't provide is **ignored for now**. The section isn't
built, and the page doesn't keep an empty block. The handoff lists what was left out so the
customer can add it later. There are two exceptions:

- **Contact.** Every page needs a way to get in touch. With no channel at all, the CTA points to
  a `[contact]` placeholder. The page can go out as a draft, but not as a final page.
- **Template image slots.** These keep their placeholder blocks, as today (`AGENTS.md` §3).

On an FDE page with only a name, role, mood and email, that means: hero, about (sample
wording), "How I work" (Discovery → Rollout, guessed), contact. Skills, platforms, projects,
outcomes, experience and education are all left out until the customer provides them.

## 4. How much to ask, by how complete the brief is

The agent scores the brief before it asks anything. It checks name, category, role or concept,
mood, and the category's core fields (the bulleted list in Step 3 or the category's intake).

| Brief coverage | Example | Ask | Then |
|---|---|---|---|
| **Full**: core fields all present | a filled `brief.md` | nothing new | build; Tier B only where wording is thin |
| **Partial**: about half | name, role, mood and contact, but no projects or about text | at most **3 questions**, only for facts that block publishing (usually contact) | fill Tier B/C, leave out the rest, build |
| **Sparse**: name + category, maybe a role | "Alex Rivera, forward deployed engineer" | **one** combined question: mood + contact, and an offer to "just build what you can" | build a short draft (§5) |
| **Bare**: category only | "make me a profile page" | the name, plus the same one combined question | short draft |

Rules for asking:
- **One round only.** Batch the questions, and give a sensible default in each one ("Mood: I'd
  go clean & professional unless you say otherwise"). If the customer doesn't answer a question,
  the default applies.
- **Never ask about Tier A or B.** Decide or draft them, and show the result.
- If the customer says "just do it", skip the question round completely. Only contact stays a
  placeholder. Everything else not provided is left out.

## 5. The short draft

When the brief is sparse or bare, the page is short on purpose. It has the hero, an about
paragraph, the Discovery → Rollout section where the page has one, and contact. Whatever the
customer did provide goes in as well.

The filled items come from these sources, most trustworthy first:

1. **The customer's own material.** That's the brief, any pasted text or résumé, image
   filenames, and a website or profile URL *they* gave. The agent doesn't search for them
   anywhere else.
2. **The stated role or concept.** It's used only to set the vocabulary of Tier B wording. It
   doesn't add sections or lists.
3. **The mood.** It sets the voice for all Tier B wording.

## 6. Marking, the manifest, and checks

**On the page**, the marks don't show on screen:
- `data-sample="about paragraph"` for Tier B. This already exists.
- `data-guess="engagement: discovery"` and `data-guess="engagement: rollout"` for Tier C. This
  is new.

**Next to the page**, a new file `_output/<slug>/content-status.md` (unpublished, like
`assets/` sources) lists what was filled and what was left out:

```markdown
| Field | Tier | Status | Question for you |
|---|---|---|---|
| Tagline | B | sample: "AI pilots into production, inside your team" | Keep, or your own line? |
| How I work | C | guessed: Discovery → Rollout | Is this how you engage? Any phase missing? |
| Contact | D | [contact] placeholder | What email should enquiries go to? |
| Projects, outcomes, skills, experience | D | left out | Send any you want shown |
```

**Checks:**
- `check_page.py`: `data-sample` → WARN (already does this). `data-guess` → WARN in draft mode
  and FAIL in final mode (new `--final` flag). `[placeholder]` → FAIL, as it does now.
- `publish_site.py`: a new `--draft` flag. It does three things:
  - publishes under `<slug>-draft`
  - adds `<meta name="robots" content="noindex">`
  - shows a small visible "Draft" ribbon

  A plain (final) publish refuses to run while any `data-guess` or `[placeholder]` remains.

## 7. Moving the customer forward: the handoff

The handoff is a short to-do list, not a report:

```text
Your draft is live: https://…/site/manual/alex-rivera-draft/index.html
(Technical Sidebar Profile, picked for the clean, technical tone you asked for.)

To finish it, I need 2 things:
1. Email for enquiries: the "Get in touch" button has nowhere to go yet.
2. How you work: I put Discovery → Rollout. Keep it, or tell me your actual phases?

Left out until you send them: projects, outcomes, skills, experience, education.
I also wrote your tagline and about paragraph. Change them whenever you like.
```

Behind that message:
- **Write what was filled back into `_input/brief.md`**, with a `(sample)` or `(guess)` tag on
  each item. Next time, the customer edits a pre-filled brief instead of a blank template.
- **Order the to-do list by what blocks the final publish.** Contact comes first, then the Tier
  C guess. "Left out" content is a single line, not a list of questions.
- **Anticipate the step after this one.** Once nothing blocks publishing, offer the next likely
  thing in one line. For an FDE page that's usually projects and outcomes; otherwise it's the
  final publish.

## 8. Guardrails

- **No guess goes out as a final page.** This is enforced by `--final` / publish refusal, not
  just by the docs.
- **No regulated or liability claims, even as guesses.** That means licences, certifications,
  medical, legal or financial outcomes, and guarantees or refunds.
- **Privacy is unchanged** (`AGENTS.md` §3). The agent never guesses or adds a home address or
  personal phone number.
- **Use only the customer's own material.** The agent never looks the customer up online to
  fill gaps unless they give the URL.
- **Every filled item is reversible in one edit.** It's marked in the HTML, listed in the
  manifest, and tagged in the brief.

## 9. Implementation plan

| # | Change | Files |
|---|---|---|
| 1 | Replace §3.1 with the tier table, the Discovery/Rollout rule, "left out for now", coverage levels, the one-round asking rule and the handoff format; update §6 and §7 to match | `AGENTS.md` |
| 2 | Point each category's intake to the coverage levels; say that e-commerce, restaurant and course pages have no Tier C guess | `categories/*/AGENTS.md` |
| 3 | `data-guess` WARN, plus a `--final` mode that FAILs on it | `scripts/check_page.py` |
| 4 | `--draft` (suffixed slug, noindex, ribbon); final publish refuses guesses or placeholders | `scripts/publish_site.py` |
| 5 | `content-status.md` format; excluded from publishing | `AGENTS.md` §7, `publish_site.py` |
| 6 | Brief template: explain the `(sample)`/`(guess)` tags and "just build what you can" | `_input/brief.template.md` |
| 7 | Try a bare, a sparse and a partial FDE brief, and one per category, and check that the questions, marks, left-out list and handoff come out as described | manual test run |

Items 1, 2 and 6 are doc-only and could ship first. Items 3–5 are what make the guardrails real.

## 10. Decisions needed

1. **Draft publishing:** should a page with a guess go public at all (as `-draft`, noindex), or
   stay local until confirmed? *Recommendation:* publish as a draft, since a link they can open
   on their phone is what gets customers to respond.
2. **Visible draft ribbon:** on or off by default? *Recommendation:* on. It's honest, and it
   goes away at the final publish.
3. **Later:** after trying this with real customers, should any "left out" content move into
   Tier C (e.g. a skills list inferred from the role)?

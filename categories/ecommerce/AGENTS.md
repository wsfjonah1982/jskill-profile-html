# E-commerce Subskill — Agent Instructions

You are building a **single-page online store** from the `profile-html` template library. This
folder is a subskill of the root `profile-html` library — for the rules that don't change between
subskills (responsive checklist, no-fabrication rule, output contract), see the root
[`../../AGENTS.md`](../../AGENTS.md). This document covers what's specific to a store.

## 1. Intake

Per root AGENTS.md Step 0.5, check `_input/brief.md`'s `## If E-commerce` block and
`_input/images/` first — only ask the user about what's missing or ambiguous:

- **Brand/store name** and a one-line tagline.
- **Product catalog**: for each item — name, price, category tag, and a short (1–2 sentence)
  description. Real product photos if they have them (check `_input/images/`); otherwise the
  template's placeholder image blocks stay in place (per root AGENTS.md §3 — never fabricate a
  stand-in photo as if it were real; if this environment has an image-generation tool available
  you may offer to use it, but never assume one exists).
- **Shipping / returns blurb** — one or two sentences for the footer/contact section.
- **Contact / social links.**
- **Vibe**: minimal & considered vs. bold & graphic (this maps directly to the two templates
  below — don't guess if it's ambiguous, ask).

## 2. Pick a template

Read this folder's `index.json` (2 entries). Match `mood`/`tone`/`occasion` against the intake
above:

| slug | when to pick it |
|---|---|
| `minimal-studio-shop` | Handmade/small-batch/design-led goods, a solo founder or small studio, anything that should read as considered and trustworthy. |
| `bold-streetwear-shop` | Streetwear, drop culture, sneakers/accessories, anything that wants to feel loud, confident, and hype-ready. |

Unlike the root library's 3-preview workflow, these two templates are structurally identical
(same sections, same cart/modal/filter behavior) and differ only in skin — a quick description of
each mood is usually enough for the user to pick without a full hero-preview round. Offer one if
the user seems unsure.

## 3. Build the page

1. Clone the chosen `templates/<slug>/template.html` into `_output/<slug-for-this-store>/` per
   root AGENTS.md §7 (or wherever the user directed instead).
2. Fill in nav brand, hero copy, about copy, contact/shipping blurb, footer — same
   bracket-placeholder convention as the root templates.
3. **Replace the `PRODUCTS` array** (near the top of the `<script>` block) with the real catalog:
   `{ id, name, price, category, description }` per item. The grid-render, filter-chip, quick-view,
   and cart logic all read from this array and already handle any number of items or categories —
   you do not need to touch the rendering/cart JS itself, only the data array. If the user gave you
   real product photos, replace the relevant `<div class="img-placeholder">…</div>` markup inside
   the `renderProductGrid()` template string with an `<img>` tag; otherwise leave the placeholder.
4. If the user wants more sections than the template ships with (e.g. a size guide, an FAQ), design
   them per root AGENTS.md §5 using this template's existing tokens (same `--ink`/`--accent`/
   `--line` variables, same card/border/shadow treatment).

## 4. Important limits — tell the user

- **The cart is an in-memory demo**: it resets on page reload (no `localStorage`, no backend). This
  is intentional so the shipped template stays stateless — flag this to the user rather than
  letting them assume it persists.
- **"Checkout" is a placeholder confirmation**, not a real payment flow. There's an HTML comment
  next to the checkout button marking where a real integration (Stripe, Shopify, etc.) would go.
  Building that integration is out of scope unless the user explicitly asks for it as a separate
  task — don't fake a transaction or collect real payment details in this template.

## 5. Finish

Defer to the root AGENTS.md: §4 for the responsive checklist (and additionally, click through the
filter chips, open a quick-view, add to cart, and open the cart drawer at both desktop and mobile
width before calling it done — this template's core value is the interaction, not just the
layout), §6 for the no-fabricated-proof-points rule, and §7 for the output contract (publish via
`scripts/upload_site.py` and lead with the public URL, plus a one-line rationale for the template
pick and any caveats — including the demo-cart/demo-checkout note above).

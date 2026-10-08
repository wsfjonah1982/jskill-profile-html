# E-commerce

Pages for a **single-page online store**: a product catalog with filter chips, quick-view and a
cart drawer.

This guide covers what's specific to a store. For everything shared (precheck, §3.1 sample
content, §4 responsive checklist, §6 no fabricated proof points, §7 output contract), follow the
root [`../../AGENTS.md`](../../AGENTS.md).

---

## 1. Design

A store page sells products, so the products carry the page and buying is never more than one
tap away.

- **Products up front.** A short hero, then the product grid. Don't make shoppers scroll through
  a long story before they see what's for sale.
- **Photos at one ratio.** Every product photo sits in a 4:3 slot, so the grid stays even. Run
  real photos through `scripts/fit_image.py --aspect 4:3`.
- **Price always visible.** Show name and price on every card, and the description in quick-view.
- **Filter by category.** Filter chips come from the products' category tags, so keep the tags
  short and consistent.
- **The cart is always reachable.** The cart button stays in the nav with a live count, and the
  cart drawer works the same at phone width.
- **Trust details near the end.** A short shipping and returns blurb and real contact links.
- **The vibe is the brand.** Minimal & considered, or bold & graphic. These are the two
  templates.

## 2. Content

Check `_input/brief.md`'s `## If E-commerce` block and `_input/images/` first (root Step 1).
Ask the user only about what's missing or ambiguous:

- **Brand/store name** and a one-line tagline.
- **Product catalog**: for each item — name, price, category tag, and a short (1–2 sentence)
  description. Real product photos if they have them (check `_input/images/`), run through
  `scripts/fit_image.py --aspect 4:3` (matching `.product-photo`'s ratio) before dropping into
  the grid; otherwise the template's placeholder image blocks stay in place (per root AGENTS.md
  §3 — never fabricate a stand-in photo, and this skill never generates one).
- **Shipping / returns blurb** — one or two sentences for the footer/contact section.
- **Contact / social links.**
- **Vibe**: minimal & considered vs. bold & graphic (this maps directly to the two templates
  below — don't guess if it's ambiguous, ask).

## 3. Relevant templates

Both are in the shared `templates/` folder at the skill root. Full metadata is in
[`templates/index.json`](../../templates/index.json). Match `mood`/`tone`/`occasion` against the
content above:

| slug | when to pick it |
|---|---|
| `minimal-studio-shop` | Handmade/small-batch/design-led goods, a solo founder or small studio, anything that should read as considered and trustworthy. |
| `bold-streetwear-shop` | Streetwear, drop culture, sneakers/accessories, anything that wants to feel loud, confident, and hype-ready. |

Unlike the OPC industry's 3-preview workflow, these two templates are structurally identical
(same sections, same cart/modal/filter behavior) and differ only in skin — a quick description of
each mood is usually enough for the user to pick without a full hero-preview round. Offer one if
the user seems unsure.

## 4. Build

1. Clone the chosen `templates/<slug>/template.html` into `_output/<slug-for-this-store>/` per
   root AGENTS.md §7 (or wherever the user directed instead).
2. Fill in nav brand, hero copy, about copy, contact/shipping blurb, footer — same
   bracket-placeholder convention as the OPC templates.
3. **Replace the `PRODUCTS` array** (near the top of the `<script>` block) with the real catalog:
   `{ id, name, price, category, description }` per item. The grid-render, filter-chip, quick-view,
   and cart logic all read from this array and already handle any number of items or categories —
   you do not need to touch the rendering/cart JS itself, only the data array. If the user gave you
   real product photos, replace the relevant `<div class="img-placeholder">…</div>` markup inside
   the `renderProductGrid()` template string with an `<img>` tag; otherwise leave the placeholder.
4. If the user wants more sections than the template ships with (e.g. a size guide, an FAQ), design
   them per root AGENTS.md §5 using this template's existing tokens (same `--ink`/`--accent`/
   `--line` variables, same card/border/shadow treatment).

## 5. Important limits — tell the user

- **The cart is an in-memory demo**: it resets on page reload (no `localStorage`, no backend). This
  is intentional so the shipped template stays stateless — flag this to the user rather than
  letting them assume it persists.
- **"Checkout" is a placeholder confirmation**, not a real payment flow. There's an HTML comment
  next to the checkout button marking where a real integration (Stripe, Shopify, etc.) would go.
  Building that integration is out of scope unless the user explicitly asks for it as a separate
  task — don't fake a transaction or collect real payment details in this template.

## 6. Finish

Defer to the root AGENTS.md: §4 for the responsive checklist (and additionally, click through the
filter chips, open a quick-view, add to cart, and open the cart drawer at both desktop and mobile
width before calling it done — this template's core value is the interaction, not just the
layout), §3.1 for marking any sample copy you wrote (e.g. product descriptions) with
`data-sample`, §6 for the no-fabricated-proof-points rule, and §7 for the output contract
(publish via `scripts/publish_site.py` and lead with the location it prints (the public URL, or
the local path when TOS isn't configured), plus a one-line rationale for the template pick and
any caveats — including the demo-cart/demo-checkout note above).

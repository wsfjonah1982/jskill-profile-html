# Restaurant / Cafe

Pages for a restaurant, cafe, bistro, or bar: one finished, responsive HTML page with the menu,
hours, location, and a reservation request form.

This guide covers what's specific to restaurants. For everything shared (precheck, §3.1 sample
content, §4 responsive checklist, §6 no fabricated proof points, §7 output contract), follow the
root [`../../AGENTS.md`](../../AGENTS.md).

---

## 1. Design

A restaurant page answers three questions fast: what's on the menu, when it's open, and how to
book.

- **Atmosphere in the hero.** Name, cuisine or concept, and one line of mood. The type and
  palette set the room: warm paper tones for a neighbourhood spot, near-black and gold for fine
  dining.
- **The menu is the main section.** Tabs split it into groups (Starters/Mains/Desserts/Drinks by
  default), so it stays short on a phone. Every item shows its price.
- **Hours and address are easy to find.** They get their own block with a maps link. On a
  phone, this is what most visitors came for.
- **Booking is one step.** The reservation form sits near hours and location, with a phone or
  email fallback if the user gives one.
- **Photos are optional.** The menu and hours sections have no image slots. A hero image can be
  added per root §5 if the user has a real one.

## 2. Content

Check `_input/brief.md`'s `## If Restaurant / Cafe` block and `_input/images/` first (root
Step 1). Ask only what's missing or ambiguous from the list below:

> "A few questions before I pick a template:
> 1. **Restaurant name and cuisine/concept** (e.g. modern Italian trattoria, neighborhood cafe,
>    tasting-menu fine dining)?
> 2. **What's the vibe?** Warm and personal, or moody and upscale?
> 3. **The full menu** — items with prices, grouped by category (the templates ship with
>    Starters/Mains/Desserts/Drinks; tell me if your categories are different, e.g. Brunch/Lunch,
>    or Small Plates/Large Plates/Sides).
> 4. **Hours and address** (and a maps link if you have one).
> 5. **How reservations should be requested** — this form is a client-side demo (see §5 below);
>    do you also want a phone number or email shown as a fallback?
> 6. **Any real food/interior photos?** If not, the templates don't currently have image slots in
>    the menu/hours sections — a portrait-style image could be added to the hero per root
>    AGENTS.md §5 if you want one, but it's not required."

## 3. Relevant templates

Both are in the shared `templates/` folder at the skill root. Full metadata is in
[`templates/index.json`](../../templates/index.json).

- **Warm Bistro** (`templates/warm-bistro/`) — light, warm, serif-led, paper tones. Best for
  neighborhood spots, cafes, family-run restaurants — anywhere the story/warmth is the pitch.
- **Modern Dark Dining** (`templates/modern-dark-dining/`) — near-black canvas, gold accents,
  italic serif. Best for fine dining, tasting menus, upscale bars — anywhere exclusivity is the
  pitch.

Match against the user's stated vibe (question 2) — don't guess.

## 4. Build

1. Clone the chosen `template.html` into `_output/<slug-for-this-restaurant>/` per root
   AGENTS.md §7 (or wherever the user directed instead).
2. Replace all bracketed placeholders (`[Restaurant Name]`, `[Cuisine — ...]`, hero copy, hours,
   address, maps link, footer year).
3. Replace the `MENU` JavaScript object near the bottom of the file with the user's real menu.
   The rendering code (`renderMenu()`) handles any number of items per category automatically —
   no other JS changes needed. **If the user's category names differ** from
   Starters/Mains/Desserts/Drinks, update in three places together: the four `.tab-btn` buttons'
   visible text and `data-target` values, the matching `id="panel-<key>"` elements, and the
   `MENU` object's keys — all three must use the same key strings.
4. If the user gave a real phone/email for reservations, add it as a line of text near the form
   (e.g. "Prefer to call? [phone]") rather than replacing the form.

## 5. The reservation form is a client-side demo

The form validates required fields and rejects past dates, then shows an on-page confirmation
message — it does **not** send an email, hit an API, or notify anyone. Say this explicitly when
you hand off the page (per root AGENTS.md §6, don't imply real functionality that doesn't exist).
If the user wants it to actually deliver reservations somewhere, that's a separate follow-up task
(e.g. wiring a form-backend service or a real API) — flag it, don't silently build it.

## 6. Before finishing

Run the root AGENTS.md §4 responsive checklist, then its §7 output contract (publish via
`scripts/publish_site.py` and lead with the location it prints (the public URL, or the local
path when TOS isn't configured), one line on which template you picked and why, plus the
reservation-form caveat from §5 above, and any sample menu descriptions you wrote, per §3.1).

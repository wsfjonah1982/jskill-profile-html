# Restaurant / Cafe Subskill

You are building a single, finished, responsive HTML page for a restaurant, cafe, bistro, or bar
— menu, hours, location, and a reservation request form. This subskill covers everything specific
to restaurants; for the rules that apply to every page in this library (responsive checklist, no
fabricated proof points, output contract), see the root `../../AGENTS.md` §4, §6, §7 — don't
duplicate them here, just follow them.

## 1. Intake — ask before building

Per root AGENTS.md Step 0.5, check `_input/brief.md`'s `## If Restaurant / Cafe` block and
`_input/images/` first — only ask what's missing or ambiguous from the list below:

> "A few questions before I pick a template:
> 1. **Restaurant name and cuisine/concept** (e.g. modern Italian trattoria, neighborhood cafe,
>    tasting-menu fine dining)?
> 2. **What's the vibe?** Warm and personal, or moody and upscale?
> 3. **The full menu** — items with prices, grouped by category (the templates ship with
>    Starters/Mains/Desserts/Drinks; tell me if your categories are different, e.g. Brunch/Lunch,
>    or Small Plates/Large Plates/Sides).
> 4. **Hours and address** (and a maps link if you have one).
> 5. **How reservations should be requested** — this form is a client-side demo (see §4 below);
>    do you also want a phone number or email shown as a fallback?
> 6. **Any real food/interior photos?** If not, the templates don't currently have image slots in
>    the menu/hours sections — a portrait-style image could be added to the hero per root
>    AGENTS.md §5 if you want one, but it's not required."

## 2. Pick a template

Read `index.json` in this folder. Two options:
- **Warm Bistro** (`templates/warm-bistro/`) — light, warm, serif-led, paper tones. Best for
  neighborhood spots, cafes, family-run restaurants — anywhere the story/warmth is the pitch.
- **Modern Dark Dining** (`templates/modern-dark-dining/`) — near-black canvas, gold accents,
  italic serif. Best for fine dining, tasting menus, upscale bars — anywhere exclusivity is the
  pitch.

Match against the user's stated vibe (question 2) — don't guess.

## 3. Build

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

## 4. The reservation form is a client-side demo

The form validates required fields and rejects past dates, then shows an on-page confirmation
message — it does **not** send an email, hit an API, or notify anyone. Say this explicitly when
you hand off the page (per root AGENTS.md §6, don't imply real functionality that doesn't exist).
If the user wants it to actually deliver reservations somewhere, that's a separate follow-up task
(e.g. wiring a form-backend service or a real API) — flag it, don't silently build it.

## 5. Before finishing

Run the root AGENTS.md §4 responsive checklist, then its §7 output contract (publish via
`scripts/upload_site.py` and lead with the public URL, one line on which template you picked and
why, plus the reservation-form caveat from §4 above).

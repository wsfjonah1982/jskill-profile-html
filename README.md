# profile-html-templates

A library of single-page, fully responsive HTML templates, designed so a coding agent can turn a
person's or company's information — bio, résumé, services, business idea, product catalog, menu,
or curriculum — into a finished, good-looking page automatically. Every template is one
self-contained HTML file that adapts from a phone screen to a desktop without a separate mobile
version. Beyond the 14 bio/portfolio templates below, the library also has three site-category
subskills under `categories/`: e-commerce stores, restaurants/cafes, and courses/coaching pages.

**Publishing is the default, not an optional extra.** A finished page isn't just written to
disk — the standard last step is uploading it to object storage and handing back a live public
URL, via `scripts/publish_site.py`. See "Scripts & credentials" below.

Agents using the library should read [`AGENTS.md`](./AGENTS.md). It's the operating manual: how
to read `index.json`, match the user's brief to a template, clone it, and adapt the content.

## Using this as a portable skill

This works as a **skill for any coding agent** — Claude Code, Cursor, Codex CLI, or anything else
that can read files and follow instructions. `AGENTS.md` (and each category's own `AGENTS.md`
under `categories/`) is plain markdown with no dependency on a specific tool ecosystem; a
`SKILL.md` is included only so Claude Code's Skill tool can also discover this folder directly —
every other agent should just be pointed at `AGENTS.md`.

By default the skill reads prepared content instead of only asking questions interactively:

- **`_input/brief.md`** — copy `_input/brief.template.md` to `_input/brief.md` and fill in the
  category you need (profile/bio, e-commerce, restaurant, or course) before running the agent.
  Anything left blank gets asked about interactively instead — nothing is invented.
- **`_input/images/`** and **`_input/videos/`** — drop in any photos, logos, or video you already
  have; reference their filenames from `brief.md` so the agent knows which slot each one fills.
- **`_output/<slug>/`** — the finished page (plus an `assets/` folder for any local media) lands
  here by default, one subfolder per site you build. See `_output/README.md`.

If you'd rather just talk through it, that still works — leave `_input/brief.md` absent (or
incomplete) and the agent falls back to asking everything interactively.

## Scripts & credentials

`scripts/` has self-contained helpers an agent calls while building and shipping a page. This
skill **never generates images** — every photo comes from the user's own `_input/images/`;
`fit_image.py` just crops/resizes what they gave you. Only `write_content.py` and the publishing
scripts talk to a network API; `fit_image.py` needs neither credentials nor `config.json` values
beyond its own defaults.

**Prerequisites:** Python 3.10+, and `pip install -r requirements.txt` (`requests` for
`write_content.py`'s Ark calls and `tos_client.py`'s hand-signed TOS calls, `Pillow` for
`fit_image.py`'s crop/resize — no vendor SDK for TOS; see `tos_client.py`). The HTML templates
themselves have no build step and no dependency on any of this — only the scripts do.

| Script | Does |
|---|---|
| `precheck.py` | **Run this first**, once per session (or after touching credentials/config). Confirms every credential loads and does a live publish→fetch→unpublish round-trip against TOS, so a broken setup surfaces before you've built anything |
| `fit_image.py` | Crops a user's photo to a slot's aspect ratio and resizes it down for the web — local only, no network call, no credentials |
| `write_content.py` | Drafts tagline/bio/section copy from `_input/brief.md` via a chat model, enforcing the no-fabricated-proof-points rule |
| `publish_site.py` | **The default way a finished page ships.** Publishes `_output/<slug>/` to BytePlus TOS object storage, public-read, and prints the live URL — this is the standard last step for every build, not something only done on request |
| `unpublish_site.py` | Removes a previously-published site from TOS by slug — use before re-publishing a redone build under the same slug, so nothing stale is left behind |
| `tos_client.py` | Shared TOS client both scripts above import — plain `requests` calls hand-signed with TOS's own TOS4-HMAC-SHA256 scheme, not the `tos` vendor SDK (see its docstring for why literal AWS S3 signing doesn't work against TOS despite its S3-like REST surface, discovered by hitting the real API) |
| `ark_service.py` / `credentials.py` | Shared HTTP client and credential-loading helpers `write_content.py` imports |

Copy `credential_tmp.json` to `credential.json` and fill in your own keys (`model_ark_key` for
content writing; `tos_access_key_id` / `tos_secret_access_key` / `tos_bucket` for publishing —
omit whichever you don't need). For each key, `credential.json` is checked first; if it's missing
or blank there, an environment variable of the **same name** is used instead (`model_ark_key`,
`tos_access_key_id`, `tos_secret_access_key`, `tos_bucket`) — handy for CI or a shared machine
where you'd rather not put a real key in a file at all. `config.json` ships with
`"tos_bucket": "your-bucket-name"` as a placeholder, so your real bucket name stays in your own
`credential.json` (or `$tos_bucket`).

## Get started

Fill in `_input/brief.md` (see above) and point your coding agent at this folder, or just say:

```
Read AGENTS.md in this repo and build me a single responsive HTML page from my information:
[paste your bio / résumé / company info / business idea / product catalog / menu / curriculum
here] — or: "read _input/brief.md".
```

## Gallery

All 14 templates, shown at desktop and mobile widths. Click any template name to open its folder.

### [Minimal Professional](./templates/minimal-professional/)

<p>
  <img src="./screenshots/minimal-professional-desktop.png" width="70%" alt="Minimal Professional — desktop" />
  <img src="./screenshots/minimal-professional-mobile.png" width="24%" alt="Minimal Professional — mobile" />
</p>

> Clean ink-on-cream one-pager with a sticky nav and a calm, trustworthy voice. Best for
> consultants, freelancers, advisors, B2B SaaS one-pagers, and professional personal brands.

### [Bold Creative](./templates/bold-creative/)

<p>
  <img src="./screenshots/bold-creative-desktop.png" width="70%" alt="Bold Creative — desktop" />
  <img src="./screenshots/bold-creative-mobile.png" width="24%" alt="Bold Creative — mobile" />
</p>

> Neo-brutalist one-pager: thick borders, offset shadows, one neon-lime accent on off-white. Best
> for indie founders, creative freelancers, and startups who want to land as confident and
> memorable.

### [Warm Editorial](./templates/warm-editorial/)

<p>
  <img src="./screenshots/warm-editorial-desktop.png" width="70%" alt="Warm Editorial — desktop" />
  <img src="./screenshots/warm-editorial-mobile.png" width="24%" alt="Warm Editorial — mobile" />
</p>

> Serif-led magazine feel on warm paper, sage and rust accents, story-first structure. Best for
> writers, coaches, consultants with a point of view, and boutique studios.

### [Dark Tech Modern](./templates/dark-tech-modern/)

<p>
  <img src="./screenshots/dark-tech-modern-desktop.png" width="70%" alt="Dark Tech Modern — desktop" />
  <img src="./screenshots/dark-tech-modern-mobile.png" width="24%" alt="Dark Tech Modern — mobile" />
</p>

> Dark canvas with a violet-to-cyan glow, built to pitch a product or business idea. Best for tech
> founders, developers, and SaaS/startup landing pages — includes a problem → solution → features
> → metrics structure for pitching an idea, not just a bio.

### [Corporate Pitch](./templates/corporate-pitch/)

<p>
  <img src="./screenshots/corporate-pitch-desktop.png" width="70%" alt="Corporate Pitch — desktop" />
  <img src="./screenshots/corporate-pitch-mobile.png" width="24%" alt="Corporate Pitch — mobile" />
</p>

> Navy-and-white corporate one-pager with a trusted-by strip and a leadership grid. Best for
> enterprise sales pages, investor one-pagers, agency capabilities pages, and executive bios.

### [Playful Personal](./templates/playful-personal/)

<p>
  <img src="./screenshots/playful-personal-desktop.png" width="70%" alt="Playful Personal — desktop" />
  <img src="./screenshots/playful-personal-mobile.png" width="24%" alt="Playful Personal — mobile" />
</p>

> Rounded pastel blobs, bouncy display type, and a friendly, human voice. Best for creators,
> coaches, small-business owners, and community brands who want to feel warm rather than corporate.

### [Luxury Portfolio](./templates/luxury-portfolio/)

<p>
  <img src="./screenshots/luxury-portfolio-desktop.png" width="70%" alt="Luxury Portfolio — desktop" />
  <img src="./screenshots/luxury-portfolio-mobile.png" width="24%" alt="Luxury Portfolio — mobile" />
</p>

> Near-black canvas, gold hairlines, italic serif display — a gallery-quality portfolio page. Best
> for photographers, architects, designers, and luxury brands whose visuals are the pitch.

### [Academic CV](./templates/academic-cv/)

<p>
  <img src="./screenshots/academic-cv-desktop.png" width="70%" alt="Academic CV — desktop" />
  <img src="./screenshots/academic-cv-mobile.png" width="24%" alt="Academic CV — mobile" />
</p>

> Structured, serif-set CV page: timeline, publications, and a résumé-download button. Best for
> academics, researchers, and job-seekers who need a dense, print-friendly page instead of a PDF.

### [AI FDE Engineer](./templates/ai-fde-engineer/)

<p>
  <img src="./screenshots/ai-fde-engineer-desktop.png" width="70%" alt="AI FDE Engineer — desktop" />
  <img src="./screenshots/ai-fde-engineer-mobile.png" width="24%" alt="AI FDE Engineer — mobile" />
</p>

> Carbon-and-lime engineer homepage: dark profile sidebar, glowing hero card, a numbered delivery
> lifecycle, and chip-dense skill cards. Best for AI forward deployed engineers, solutions/field
> engineers, and ML/infra ICs who want to show end-to-end delivery on one information-only page.

### Developer portfolio styles

The next five are fresh single-file rewrites of the visual style of popular templates from GitHub's
[`portfolio-template`](https://github.com/topics/portfolio-template) topic. No code was copied;
each `index.json` entry credits its source in `inspired_by`.

### [Playful Dev Folio](./templates/playful-dev-folio/)

<p>
  <img src="./screenshots/playful-dev-folio-desktop.png" width="70%" alt="Playful Dev Folio — desktop" />
  <img src="./screenshots/playful-dev-folio-mobile.png" width="24%" alt="Playful Dev Folio — mobile" />
</p>

> Montserrat-and-purple developer portfolio with a waving greeting, skill icons, proficiency bars,
> brand-colored experience cards, and a light/dark toggle. Style from
> [developerFolio](https://github.com/saadpasta/developerFolio).

### [Mono Minimal Dev](./templates/mono-minimal-dev/)

<p>
  <img src="./screenshots/mono-minimal-dev-desktop.png" width="70%" alt="Mono Minimal Dev — desktop" />
  <img src="./screenshots/mono-minimal-dev-mobile.png" width="24%" alt="Mono Minimal Dev — mobile" />
</p>

> All-monospace minimalist page with an oversized blue-name hero, titles-left section rows, numbered
> project cards, and a dot timeline. Style from [devportfolio](https://github.com/RyanFitzgerald/devportfolio).

### [Illustrated Sky Folio](./templates/illustrated-sky-folio/)

<p>
  <img src="./screenshots/illustrated-sky-folio-desktop.png" width="70%" alt="Illustrated Sky Folio — desktop" />
  <img src="./screenshots/illustrated-sky-folio-mobile.png" width="24%" alt="Illustrated Sky Folio — mobile" />
</p>

> Pale sky-blue, navy-ink portfolio built around big illustrations, with alternating "What I Do?"
> rows and light-blue project tiles. Style from [masterPortfolio](https://github.com/ashutosh1919/masterPortfolio).

### [Bold Blue Folio](./templates/bold-blue-folio/)

<p>
  <img src="./screenshots/bold-blue-folio-desktop.png" width="70%" alt="Bold Blue Folio — desktop" />
  <img src="./screenshots/bold-blue-folio-mobile.png" width="24%" alt="Bold Blue Folio — mobile" />
</p>

> Full-screen patterned blue hero, fixed social rail, laptop-mockup project rows, and a no-backend
> contact form. Style from [Dopefolio](https://github.com/rammcodes/Dopefolio).

### [GitHub Card Profile](./templates/github-card-profile/)

<p>
  <img src="./screenshots/github-card-profile-desktop.png" width="70%" alt="GitHub Card Profile — desktop" />
  <img src="./screenshots/github-card-profile-mobile.png" width="24%" alt="GitHub Card Profile — mobile" />
</p>

> Dashboard-style profile with a left column of info cards and right-hand panels of repo,
> publication, project, and article cards. Style from [gitprofile](https://github.com/arifszn/gitprofile).

## What makes these different from a slide-deck template

Each template is **one HTML page**, not a series of slides:

- Mobile-first responsive CSS — fluid type via `clamp()`, `grid`/`flex` layouts that collapse to
  a single column on small screens, and a hamburger nav that appears under ~840px.
- No external JS dependencies — only Google Fonts and a ~15-line inline script for the mobile
  menu toggle.
- Section-based structure (hero, about, services/experience, work, contact, etc.) so an agent can
  add, remove, or reorder sections without breaking the layout.

See `index.json` for each template's mood/tone/formality metadata, and `AGENTS.md` for the full
matching-and-build workflow.

## Skill Version
v 0.0.083011

## License

[MIT](./LICENSE) — free to use, modify, and distribute.

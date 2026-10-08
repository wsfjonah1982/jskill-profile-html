# profile-html-templates

A library of single-page, fully responsive HTML templates, designed so a coding agent can turn a
person's or company's information — bio, résumé, services, business idea, product catalog, menu,
or curriculum — into a finished, good-looking page automatically. Every template is one
self-contained HTML file that adapts from a phone screen to a desktop without a separate mobile
version. The library covers four industries under `industries/`: OPC (one-person company:
bio/portfolio/pitch, the 14 templates below), e-commerce stores, restaurants/cafes, and
education (courses/coaching) pages. All 20 templates share one `templates/` folder, with their metadata in
`templates/index.json`. Each industry has one `industries/<industry>/Industry.md` that describes
its design and content and names the templates that suit it.

**Publishing is the default, not an optional extra.** The standard last step is
`scripts/publish_site.py`. With BytePlus TOS configured, it uploads the page and hands back a
live public URL. TOS is optional, though. Without it, the page stays on the local file system,
in `_output/<slug>/` or a folder you choose (`local_publish_dir`). See "Scripts & credentials"
below.

Agents using the library should read [`AGENTS.md`](./AGENTS.md). It's the operating manual: how
to pick the industry, read its `Industry.md`, match the user's brief to a template, clone it, and adapt the content.

## Using this as a portable skill

This works as a **skill for any coding agent** — Claude Code, Cursor, Codex CLI, or anything else
that can read files and follow instructions. `AGENTS.md` (and each `Industry.md`
under `industries/`) is plain markdown with no dependency on a specific tool ecosystem; a
`SKILL.md` is included only so Claude Code's Skill tool can also discover this folder directly —
every other agent should just be pointed at `AGENTS.md`.

By default the skill reads prepared content instead of only asking questions interactively:

- **`_input/brief.md`** — copy `_input/brief.template.md` to `_input/brief.md` and fill in the
  industry you need (OPC/profile, e-commerce, restaurant, or education) before running the agent.
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
`fit_image.py` just crops/resizes what they gave you. The skill also **never calls a third-party
text model**. The building agent writes any copy itself, and marks sample copy it writes to fill
gaps (see `AGENTS.md` §3.1). Only the publishing scripts talk to a network API, and only when TOS
is configured. `fit_image.py` needs neither credentials nor `config.json` values beyond its own
defaults.

**Prerequisites:** Python 3.10+, and `pip install -r requirements.txt` (`requests` for
`tos_client.py`'s hand-signed TOS calls, needed only when TOS is configured; `Pillow` for
`fit_image.py`'s crop/resize — no vendor SDK for TOS; see `tos_client.py`). The HTML templates
themselves have no build step and no dependency on any of this — only the scripts do. The
skill doesn't need a headless browser (see [`PostTask.md`](./PostTask.md) for the optional
Playwright page checks).

### Installing on Ubuntu

```bash
# 1. Python + venv (skip if you already have them)
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 2. A virtual environment in the skill folder
cd profile-html
python3 -m venv .venv
source .venv/bin/activate

# 3. The skill's Python packages
pip install -r requirements.txt

# 4. Check that it works
python scripts/precheck.py
```

Ubuntu 23.04 and later reject `pip install` outside a virtual environment
("externally-managed-environment"); to skip the venv anyway, use
`pip install --user --break-system-packages -r requirements.txt`.
Run `source .venv/bin/activate` again in each new terminal before using the scripts.

| Script | Does |
|---|---|
| `precheck.py` | **Run this first**, once per session (or after touching credentials/config). With TOS configured, it confirms the credentials load and does a live publish→fetch→unpublish round-trip. Without TOS, it passes and checks that `local_publish_dir` is writable, if one is set. Partly-configured TOS fails. Either way, a broken setup surfaces before you've built anything |
| `fit_image.py` | Crops a user's photo to a slot's aspect ratio and resizes it down for the web — local only, no network call, no credentials |
| `publish_site.py` | **The default way a finished page ships.** Publishes `_output/<slug>/` to BytePlus TOS object storage, public-read, and prints the live URL. Without TOS, it copies the site to `<local_publish_dir>/<slug>/` (or leaves it in `_output/<slug>/`) and prints its `file://` location. `--local-dir DIR` delivers to any folder instead (a network drive, synced folder, web root). This is the standard last step for every build, not something only done on request |
| `unpublish_site.py` | Takes a published site down by slug: the TOS copy, or the `local_publish_dir` copy. Never touches the build in `_output/` (republishing doesn't need it — `publish_site.py` already removes stale files) |
| `list_sites.py` | Lists every site currently public in the bucket — files, size, last update, whether a local build still exists — so old test builds don't stay online unnoticed. Without TOS, it lists the sites in `local_publish_dir`. Read-only |
| `check_page.py` | **Disabled for now.** Automated §4 checks in a headless browser. It needs Playwright, which the skill no longer installs; see [`PostTask.md`](./PostTask.md) |
| `theme_fallbacks.py` | Adds plain-colour fallbacks for browsers without `color-mix()` / relative `oklch()` — re-run after changing `--accent` |
| `site_paths.py` | Shared slug validation, bucket-prefix building and local publish paths for publish/unpublish/list |
| `tos_client.py` | Shared TOS client both scripts above import — plain `requests` calls hand-signed with TOS's own TOS4-HMAC-SHA256 scheme, not the `tos` vendor SDK (see its docstring for why literal AWS S3 signing doesn't work against TOS despite its S3-like REST surface, discovered by hitting the real API) |
| `credentials.py` | Shared credential-loading helpers the publishing scripts import, including whether TOS is configured |

**TOS is optional.** Skip this whole step to keep sites local. To publish publicly, copy
`credential_tmp.json` to `credential.json` and fill in your own publishing keys
(`tos_access_key_id` / `tos_secret_access_key` / `tos_bucket`). Set all three or none. A partial
setup is reported as an error, not silently treated as local. For each key, `credential.json`
is checked first; if it's missing or blank there, an environment variable of the **same name**
is used instead (`tos_access_key_id`, `tos_secret_access_key`, `tos_bucket`) — handy for CI or a
shared machine where you'd rather not put a real key in a file at all. `config.json` ships with
`"tos_bucket": "your-bucket-name"` as a placeholder, so your real bucket name stays in your own
`credential.json` (or `$tos_bucket`).

Without TOS, set `"local_publish_dir"` in `config.json` to have finished sites copied to
`<that folder>/<slug>/` (absolute, or relative to this skill folder). That could be a mounted
network share, a synced cloud folder, or a web server's document root. Leave it empty (`""`)
and sites simply stay in `_output/<slug>/`.

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
  <img src="./templates/minimal-professional/screenshot-desktop.png" width="70%" alt="Minimal Professional — desktop" />
  <img src="./templates/minimal-professional/screenshot-mobile.png" width="24%" alt="Minimal Professional — mobile" />
</p>

> Clean ink-on-cream one-pager with a sticky nav and a calm, trustworthy voice. Best for
> consultants, freelancers, advisors, B2B SaaS one-pagers, and professional personal brands.

### [Bold Creative](./templates/bold-creative/)

<p>
  <img src="./templates/bold-creative/screenshot-desktop.png" width="70%" alt="Bold Creative — desktop" />
  <img src="./templates/bold-creative/screenshot-mobile.png" width="24%" alt="Bold Creative — mobile" />
</p>

> Neo-brutalist one-pager: thick borders, offset shadows, one neon-lime accent on off-white. Best
> for indie founders, creative freelancers, and startups who want to land as confident and
> memorable.

### [Warm Editorial](./templates/warm-editorial/)

<p>
  <img src="./templates/warm-editorial/screenshot-desktop.png" width="70%" alt="Warm Editorial — desktop" />
  <img src="./templates/warm-editorial/screenshot-mobile.png" width="24%" alt="Warm Editorial — mobile" />
</p>

> Serif-led magazine feel on warm paper, sage and rust accents, story-first structure. Best for
> writers, coaches, consultants with a point of view, and boutique studios.

### [Dark Tech Modern](./templates/dark-tech-modern/)

<p>
  <img src="./templates/dark-tech-modern/screenshot-desktop.png" width="70%" alt="Dark Tech Modern — desktop" />
  <img src="./templates/dark-tech-modern/screenshot-mobile.png" width="24%" alt="Dark Tech Modern — mobile" />
</p>

> Dark canvas with a violet-to-cyan glow, built to pitch a product or business idea. Best for tech
> founders, developers, and SaaS/startup landing pages — includes a problem → solution → features
> → metrics structure for pitching an idea, not just a bio.

### [Corporate Pitch](./templates/corporate-pitch/)

<p>
  <img src="./templates/corporate-pitch/screenshot-desktop.png" width="70%" alt="Corporate Pitch — desktop" />
  <img src="./templates/corporate-pitch/screenshot-mobile.png" width="24%" alt="Corporate Pitch — mobile" />
</p>

> Navy-and-white corporate one-pager with a trusted-by strip and a leadership grid. Best for
> enterprise sales pages, investor one-pagers, agency capabilities pages, and executive bios.

### [Playful Personal](./templates/playful-personal/)

<p>
  <img src="./templates/playful-personal/screenshot-desktop.png" width="70%" alt="Playful Personal — desktop" />
  <img src="./templates/playful-personal/screenshot-mobile.png" width="24%" alt="Playful Personal — mobile" />
</p>

> Rounded pastel blobs, bouncy display type, and a friendly, human voice. Best for creators,
> coaches, small-business owners, and community brands who want to feel warm rather than corporate.

### [Luxury Portfolio](./templates/luxury-portfolio/)

<p>
  <img src="./templates/luxury-portfolio/screenshot-desktop.png" width="70%" alt="Luxury Portfolio — desktop" />
  <img src="./templates/luxury-portfolio/screenshot-mobile.png" width="24%" alt="Luxury Portfolio — mobile" />
</p>

> Near-black canvas, gold hairlines, italic serif display — a gallery-quality portfolio page. Best
> for photographers, architects, designers, and luxury brands whose visuals are the pitch.

### [Academic CV](./templates/academic-cv/)

<p>
  <img src="./templates/academic-cv/screenshot-desktop.png" width="70%" alt="Academic CV — desktop" />
  <img src="./templates/academic-cv/screenshot-mobile.png" width="24%" alt="Academic CV — mobile" />
</p>

> Structured, serif-set CV page: timeline, publications, and a résumé-download button. Best for
> academics, researchers, and job-seekers who need a dense, print-friendly page instead of a PDF.

### [Technical Sidebar Profile](./templates/technical-sidebar-profile/)

<p>
  <img src="./templates/technical-sidebar-profile/screenshot-desktop.png" width="70%" alt="Technical Sidebar Profile — desktop" />
  <img src="./templates/technical-sidebar-profile/screenshot-mobile.png" width="24%" alt="Technical Sidebar Profile — mobile" />
</p>

> Monospace engineer homepage: dark profile sidebar, hero card with stats, a numbered timeline of
> recent projects, work history, chip-dense skill cards, and education. Recolour it with one `--accent`
> variable, switch mono/sans with `--font`, and print it as a PDF résumé. Best for AI forward deployed engineers, solution/pre-sales architects,
> field engineers, and ML/platform ICs.

### Developer portfolio styles

The next five are fresh single-file rewrites of the visual style of popular templates from GitHub's
[`portfolio-template`](https://github.com/topics/portfolio-template) topic. No code was copied;
each `templates/index.json` entry credits its source in `inspired_by`.

### [Playful Dev Folio](./templates/playful-dev-folio/)

<p>
  <img src="./templates/playful-dev-folio/screenshot-desktop.png" width="70%" alt="Playful Dev Folio — desktop" />
  <img src="./templates/playful-dev-folio/screenshot-mobile.png" width="24%" alt="Playful Dev Folio — mobile" />
</p>

> Montserrat-and-purple developer portfolio with a waving greeting, skill icons, proficiency bars,
> brand-colored experience cards, and a light/dark toggle. Style from
> [developerFolio](https://github.com/saadpasta/developerFolio).

### [Mono Minimal Dev](./templates/mono-minimal-dev/)

<p>
  <img src="./templates/mono-minimal-dev/screenshot-desktop.png" width="70%" alt="Mono Minimal Dev — desktop" />
  <img src="./templates/mono-minimal-dev/screenshot-mobile.png" width="24%" alt="Mono Minimal Dev — mobile" />
</p>

> All-monospace minimalist page with an oversized blue-name hero, titles-left section rows, numbered
> project cards, and a dot timeline. Style from [devportfolio](https://github.com/RyanFitzgerald/devportfolio).

### [Illustrated Sky Folio](./templates/illustrated-sky-folio/)

<p>
  <img src="./templates/illustrated-sky-folio/screenshot-desktop.png" width="70%" alt="Illustrated Sky Folio — desktop" />
  <img src="./templates/illustrated-sky-folio/screenshot-mobile.png" width="24%" alt="Illustrated Sky Folio — mobile" />
</p>

> Pale sky-blue, navy-ink portfolio built around big illustrations, with alternating "What I Do?"
> rows and light-blue project tiles. Style from [masterPortfolio](https://github.com/ashutosh1919/masterPortfolio).

### [Bold Blue Folio](./templates/bold-blue-folio/)

<p>
  <img src="./templates/bold-blue-folio/screenshot-desktop.png" width="70%" alt="Bold Blue Folio — desktop" />
  <img src="./templates/bold-blue-folio/screenshot-mobile.png" width="24%" alt="Bold Blue Folio — mobile" />
</p>

> Full-screen patterned blue hero, fixed social rail, laptop-mockup project rows, and a no-backend
> contact form. Style from [Dopefolio](https://github.com/rammcodes/Dopefolio).

### [GitHub Card Profile](./templates/github-card-profile/)

<p>
  <img src="./templates/github-card-profile/screenshot-desktop.png" width="70%" alt="GitHub Card Profile — desktop" />
  <img src="./templates/github-card-profile/screenshot-mobile.png" width="24%" alt="GitHub Card Profile — mobile" />
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
- Themeable from `:root`: change `--accent` to recolour the brand colour (derived shades follow),
  and swap fonts through the `--font-*` variables. The THEME comment at the top of each `:root`
  lists what's safe to change.
- Print-ready: every template has a print stylesheet (black on white, no nav or buttons, no
  cards split across pages) and a "Save as PDF" button in the footer.

See `templates/index.json` for each template's mood/tone/formality metadata,
`industries/<industry>/Industry.md` for each industry's design, content and templates, and
`AGENTS.md` for the full matching-and-build workflow.

## Skill Version
v 0.1.100601

## Changelog

### v 0.1.100601 — 2026-10-06
**Tooling**
- `check_page.py` (automated responsive/contrast/print checks), `list_sites.py` (what's public),
  `theme_fallbacks.py` (colour fallbacks for older browsers). All 14 profile templates pass
  `check_page.py`; it also caught and fixed undersized tap targets in 9 templates and a 1px
  overflow in Playful Dev Folio.
- Technical Sidebar Profile: name shown in white; footer contrast fixed.

**Templates**
- Added 6 profile templates: Technical Sidebar Profile, plus five developer-portfolio styles
  rewritten from scratch after popular GitHub `portfolio-template` projects (Playful Dev Folio,
  Mono Minimal Dev, Illustrated Sky Folio, Bold Blue Folio, GitHub Card Profile). Credited in
  `index.json` → `inspired_by`.
- All 14 profile templates: every colour moved into `:root`, one `--accent` knob with derived
  shades, font variables, a print stylesheet and a "Save as PDF" footer button. Refactor verified
  pixel-identical against the previous versions.
- Technical Sidebar Profile: Experience timeline, Education & Certifications (+ optional Awards),
  social/contact list (keep only real channels), stage strip built automatically from the cards,
  accessible solid-button contrast, `--font` mono/sans switch.
- Demo content that could be mistaken for real data is now bracketed (`[Skill]`, `[Method]`, …).

**Publishing**
- Slugs are validated (lowercase kebab-case) in publish and unpublish, so an empty or `/`-containing
  slug can no longer reach other sites' files.
- Republishing deletes objects no longer in the build, and refuses an empty build folder.
- HTML is served with `Cache-Control: no-cache`; other assets with `max-age=3600`.

**Privacy & config**
- `config.json` ships with a placeholder bucket; the real one comes from `credential.json` or
  `$tos_bucket`.
- Personal example names removed from docs and scripts.

**Docs**
- `AGENTS.md`: intake no longer contradicts itself (don't re-ask what the brief answers), dead
  image-generation reference removed, theming/font/print/contrast guidance, image-slot names,
  "never publish a home address or phone number" rule, `inspired_by` documented.

### v 0.0.083011
- Initial release: 8 profile templates and the e-commerce, restaurant and course subskills.

## License

[MIT](./LICENSE) — free to use, modify, and distribute.

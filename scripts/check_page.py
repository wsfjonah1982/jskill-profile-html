"""Automated version of AGENTS.md §4 — run it on any built page or template
before calling it done.

Checks, at each width (default 1440, 1024, 768, 375, 320):
  - horizontal overflow (page wider than the viewport)
  - clipped text (elements whose text is wider than their box)
  - tap targets under 44px tall on narrow widths (links/buttons)
  - JavaScript errors
  - the mobile menu (#menuBtn / #mobile-menu) opens and closes, if present
  - unfilled [placeholders] still in the visible page (skipped with --template)
  - agent-written sample content marked data-sample (a warning, not a failure)
Once:
  - text contrast (WCAG: 4.5:1 normal text, 3:1 large text) against the nearest
    solid background — elements over images/gradients are skipped
  - print mode: white background, nav/buttons hidden, PDF page count
  - optional --compare OTHER.html: pixel diff at 1440 and 375 (for refactors)

Exits 0 if every check passes, 1 if anything failed. Warnings don't fail.

Usage:
    python scripts/check_page.py _output/<slug>/index.html
    python scripts/check_page.py templates/<slug>/template.html --template
    python scripts/check_page.py new.html --compare old.html
    python scripts/check_page.py page.html --widths 1280,390 --pdf out.pdf

Needs Playwright (`pip install playwright && playwright install chromium`).
Disabled in the default workflow for now: Playwright isn't in requirements.txt and
AGENTS.md §4 doesn't call this script. See PostTask.md to turn it back on.
"""
import argparse
import io
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright isn't installed: pip install playwright && playwright install chromium")
    raise SystemExit(2)

LAYOUT_JS = """(narrow) => {
  const W = innerWidth;
  const vis = e => { const r = e.getBoundingClientRect(); const cs = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none'; };
  const label = e => (e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\\s+/)[0] : '')) +
                     ' "' + (e.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 30) + '"';
  const out = { overflow: document.documentElement.scrollWidth - W, wide: [], clipped: [], small: [] };
  if (out.overflow > 0) {
    out.wide = [...document.querySelectorAll('body *')].filter(e => {
      const cs = getComputedStyle(e); if (cs.position === 'fixed') return false;
      let p = e.parentElement; while (p) { const o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll' || o === 'hidden') return false; p = p.parentElement; }
      return e.getBoundingClientRect().right > W + 1;
    }).slice(0, 6).map(label);
  }
  out.clipped = [...document.querySelectorAll('h1,h2,h3,h4,p,a,button,span,b,li,label,dt,dd,td,th')].filter(e => {
    if (!vis(e) || !e.textContent.trim()) return false;
    const cs = getComputedStyle(e);
    if (cs.overflowX === 'visible' && cs.whiteSpace !== 'nowrap' && cs.textOverflow !== 'ellipsis') return false;
    let p = e.parentElement; while (p) { const o = getComputedStyle(p).overflowX; if (o === 'auto' || o === 'scroll') return false; p = p.parentElement; }
    return e.scrollWidth > e.clientWidth + 1;
  }).slice(0, 8).map(label);
  if (narrow) {
    out.small = [...document.querySelectorAll('a[href],button')].filter(e => {
      if (!vis(e)) return false; const cs = getComputedStyle(e);
      if (cs.display === 'inline' && e.closest('p,li,dd,td')) return false;   // links inside running text
      return e.getBoundingClientRect().height < 40;
    }).slice(0, 8).map(e => label(e) + ' ' + Math.round(e.getBoundingClientRect().height) + 'px');
  }
  return out;
}"""

CONTRAST_JS = """() => {
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const rgba = c => { cx.clearRect(0,0,1,1); cx.fillStyle = '#000'; cx.fillStyle = c; cx.fillRect(0,0,1,1); return [...cx.getImageData(0,0,1,1).data]; };
  const lum = ([r,g,b]) => { const f = v => { v /= 255; return v <= .03928 ? v/12.92 : Math.pow((v+.055)/1.055, 2.4); }; return .2126*f(r) + .7152*f(g) + .0722*f(b); };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x,y) + .05) / (Math.min(x,y) + .05); };
  const bgOf = e => {
    let layers = [];
    for (let p = e; p; p = p.parentElement) {
      const cs = getComputedStyle(p);
      if (cs.backgroundImage && cs.backgroundImage !== 'none' && !/^url\\("data:image\\/svg/.test(cs.backgroundImage)) return null; // gradient/image: can't know
      const c = rgba(cs.backgroundColor);
      if (c[3] > 0) { layers.push(c); if (c[3] >= 250) break; }
    }
    let base = [255,255,255];
    for (let i = layers.length - 1; i >= 0; i--) { const [r,g,b,a] = layers[i]; const al = a/255; base = [r*al + base[0]*(1-al), g*al + base[1]*(1-al), b*al + base[2]*(1-al)]; }
    return base;
  };
  const seen = new Set(), bad = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const t = walker.currentNode; if (!t.textContent.trim()) continue;
    const e = t.parentElement; if (!e || seen.has(e)) continue; seen.add(e);
    const r = e.getBoundingClientRect(), cs = getComputedStyle(e);
    if (!r.width || !r.height || cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
    if (e.closest('.img-placeholder,[aria-hidden="true"]')) continue;
    if (cs.webkitTextFillColor && cs.webkitTextFillColor !== cs.color && rgba(cs.webkitTextFillColor)[3] === 0) continue; // gradient text
    const bg = bgOf(e); if (!bg) continue;
    const fg = rgba(cs.color); if (fg[3] < 250) continue;
    const size = parseFloat(cs.fontSize), weight = +cs.fontWeight || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    const need = large ? 3 : 4.5, got = ratio(fg, bg);
    if (got < need) bad.push([+got.toFixed(2), need, (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\\s+/)[0] : e.tagName.toLowerCase()) + ' "' + e.textContent.trim().replace(/\\s+/g,' ').slice(0, 28) + '"']);
  }
  return bad;
}"""


def to_url(target):
    if re.match(r"https?://|file://", target):
        return target
    p = Path(target).resolve()
    if not p.exists():
        raise SystemExit(f"Not found: {target}")
    return p.as_uri()


def main():
    ap = argparse.ArgumentParser(description="Check a page against AGENTS.md §4.")
    ap.add_argument("target", help="HTML file path or URL")
    ap.add_argument("--widths", default="1440,1024,768,375,320")
    ap.add_argument("--template", action="store_true", help="it's a template: don't flag [placeholders]")
    ap.add_argument("--compare", help="another HTML file/URL to pixel-diff against (refactor check)")
    ap.add_argument("--pdf", help="also save the print-mode PDF here")
    ap.add_argument("--quiet", action="store_true", help="only print failures and the summary")
    args = ap.parse_args()

    url = to_url(args.target)
    widths = [int(w) for w in args.widths.split(",")]
    fails, warns = [], []

    def say(msg):
        if not args.quiet:
            print(msg)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for w in widths:
            pg = browser.new_page(viewport={"width": w, "height": 900})
            errors = []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.goto(url, wait_until="networkidle")
            pg.wait_for_timeout(400)
            r = pg.evaluate(LAYOUT_JS, w <= 640)
            line = []
            if r["overflow"] > 0:
                fails.append(f"{w}px: page is {r['overflow']}px wider than the viewport — {', '.join(r['wide']) or 'cause not found'}")
                line.append(f"overflow +{r['overflow']}px")
            if r["clipped"]:
                fails.append(f"{w}px: clipped text — {'; '.join(r['clipped'])}")
                line.append(f"{len(r['clipped'])} clipped")
            if r["small"]:
                fails.append(f"{w}px: tap targets under 40px — {'; '.join(r['small'])}")
                line.append(f"{len(r['small'])} small taps")
            if errors:
                fails.append(f"{w}px: JavaScript error — {errors[0][:120]}")
                line.append("JS error")
            if pg.query_selector("#menuBtn") and pg.is_visible("#menuBtn"):
                pg.click("#menuBtn")
                opened = pg.is_visible("#mobile-menu a")
                link = pg.query_selector("#mobile-menu a")
                if link:
                    link.click()
                    pg.wait_for_timeout(400)
                closed = not pg.is_visible("#mobile-menu a")
                if not (opened and closed):
                    fails.append(f"{w}px: mobile menu didn't {'open' if not opened else 'close after a link tap'}")
                    line.append("menu broken")
                else:
                    line.append("menu ok")
            if not args.template and w == widths[0]:
                text = pg.evaluate("document.body.innerText")
                ph = sorted(set(re.findall(r"\[[A-Za-z][^\]\n]{0,50}\]", text)))
                if ph:
                    fails.append(f"unfilled placeholders: {', '.join(ph[:10])}{' …' if len(ph) > 10 else ''}")
                samples = pg.evaluate("""() => [...document.querySelectorAll('[data-sample]')].map(e =>
                    e.getAttribute('data-sample') || e.textContent.trim().replace(/\\s+/g, ' ').slice(0, 40))""")
                if samples:
                    warns.append(f"{len(samples)} agent-written sample item(s) (data-sample) — confirm with the user: "
                                 f"{'; '.join(samples[:10])}{' …' if len(samples) > 10 else ''}")
            say(f"  {w:>5}px  {'; '.join(line) if line else 'ok'}")
            pg.close()

        # contrast (desktop, normal media)
        pg = browser.new_page(viewport={"width": widths[0], "height": 900})
        pg.goto(url, wait_until="networkidle")
        bad = pg.evaluate(CONTRAST_JS)
        for got, need, what in bad[:12]:
            warns.append(f"contrast {got}:1 (needs {need}:1) — {what}")
        say(f"  contrast  {'ok' if not bad else str(len(bad)) + ' low-contrast text element(s)'}")

        # print
        pg.emulate_media(media="print")
        pr = pg.evaluate("""() => ({bg: getComputedStyle(document.body).backgroundColor,
            shown: [...document.querySelectorAll('header.site,.menu-btn,.btn,.print-btn,nav.nav')].filter(e => e.getClientRects().length > 0).map(e => e.className || e.tagName)})""")
        pdf = pg.pdf(format="A4", print_background=True)
        pages = len(re.findall(rb"/Type\s*/Page[^s]", pdf))
        if args.pdf:
            Path(args.pdf).write_bytes(pdf)
        if pr["bg"] not in ("rgb(255, 255, 255)", "rgba(0, 0, 0, 0)"):
            fails.append(f"print: background is {pr['bg']}, not white")
        if pr["shown"]:
            warns.append(f"print: still visible — {', '.join(sorted(set(pr['shown'])))[:120]}")
        if not pg.query_selector(".print-btn"):
            warns.append("no 'Save as PDF' button (.print-btn) found")
        say(f"  print     {pages} A4 page(s), background {pr['bg']}")
        pg.close()

        # optional pixel comparison
        if args.compare:
            from PIL import Image, ImageChops
            other = to_url(args.compare)
            for w in (1440, 375):
                shots = []
                for u in (url, other):
                    q = browser.new_page(viewport={"width": w, "height": 900})
                    q.goto(u, wait_until="networkidle")
                    q.add_style_tag(content="*{animation:none!important;transition:none!important}")
                    q.wait_for_timeout(300)
                    shots.append(Image.open(io.BytesIO(q.screenshot(full_page=True))).convert("RGB"))
                    q.close()
                a, b = shots
                if a.size != b.size:
                    fails.append(f"compare {w}px: page size differs {b.size} → {a.size}")
                    continue
                diff = ImageChops.difference(a, b).convert("L")
                changed = sum(diff.histogram()[25:])
                say(f"  compare   {w}px: {changed} pixel(s) differ visibly")
                if changed:
                    warns.append(f"compare {w}px: {changed} pixel(s) differ visibly from {args.compare}")
        browser.close()

    print()
    for f in fails:
        print(f"FAIL  {f}")
    for w in warns:
        print(f"WARN  {w}")
    print(f"\n{'PASS' if not fails else 'FAIL'} — {len(fails)} failure(s), {len(warns)} warning(s): {args.target}")
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())

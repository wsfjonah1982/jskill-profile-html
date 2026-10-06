"""Add (or refresh) plain-colour fallbacks for browsers without modern CSS colour
functions — color-mix() and relative oklch(from ...) syntax.

Templates derive accent shades with those functions. Older browsers can't
compute them, and a property that depends on an uncomputable custom property
silently becomes unset. A "write the hex first" fallback doesn't work for
custom properties (the later declaration always wins), so this script appends a

    @supports not (color: oklch(from red l c h)) { ... }

block that redefines every derived variable — and every rule that uses those
functions inline — with the colour it resolves to for the page's *current*
theme. Modern browsers skip the block entirely.

Re-run it after changing --accent (or any colour it derives from); the block
is replaced in place, between /* theme-fallbacks:start */ and :end markers.

Usage:
    python scripts/theme_fallbacks.py templates/*/template.html
    python scripts/theme_fallbacks.py _output/<slug>/index.html
"""
import math
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

START, END = "/* theme-fallbacks:start */", "/* theme-fallbacks:end */"
MODERN_FN = re.compile(r"color-mix\(|oklch\(from")


# ---------------------------------------------------------------- colour maths
def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c):
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def rgb_to_oklab(r, g, b):
    r, g, b = (srgb_to_linear(x) for x in (r, g, b))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def oklab_to_rgb(L, a, b):
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (linear_to_srgb(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
            linear_to_srgb(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
            linear_to_srgb(-0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s))


class Color:
    def __init__(self, r, g, b, a=1.0):  # r,g,b in 0..1
        self.r, self.g, self.b, self.a = r, g, b, a

    def css(self):
        R, G, B = (round(max(0, min(1, x)) * 255) for x in (self.r, self.g, self.b))
        if self.a >= 0.999:
            return f"#{R:02x}{G:02x}{B:02x}"
        return f"rgba({R},{G},{B},{round(self.a, 3):g})"


def parse_literal(tok):
    tok = tok.strip().lower()
    if tok == "transparent":
        return Color(0, 0, 0, 0)
    if tok in ("white",):
        return Color(1, 1, 1)
    if tok in ("black",):
        return Color(0, 0, 0)
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", tok)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(c * 2 for c in h)
        return Color(*(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))
    m = re.fullmatch(r"rgba?\(([^)]*)\)", tok)
    if m:
        parts = [p.strip() for p in re.split(r"[,\s/]+", m.group(1)) if p.strip()]
        r, g, b = (float(x) / 255 for x in parts[:3])
        a = float(parts[3].rstrip("%")) / (100 if parts[3].endswith("%") else 1) if len(parts) > 3 else 1.0
        return Color(r, g, b, a)
    return None


def split_args(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip())
            cur = ""
        else:
            cur += ch
    out.append(cur.strip())
    return out


def find_call(s, start):
    """Return the index just past the ')' matching the '(' at/after start."""
    i = s.index("(", start)
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "(":
            depth += 1
        elif s[j] == ")":
            depth -= 1
            if depth == 0:
                return j + 1
    raise ValueError("unbalanced parens")


class Resolver:
    def __init__(self, env):
        self.env = env  # var name -> raw value

    def color(self, expr, seen=()):
        expr = expr.strip()
        m = re.fullmatch(r"var\(\s*--([\w-]+)\s*(?:,\s*(.+))?\)", expr)
        if m:
            name = m.group(1)
            if name in seen or name not in self.env:
                return self.color(m.group(2), seen) if m.group(2) else None
            return self.color(self.env[name], seen + (name,))
        if expr.startswith("color-mix("):
            return self._mix(expr[len("color-mix("):-1], seen)
        if expr.startswith("oklch(from"):
            return self._relative(expr[len("oklch(from"):-1], seen)
        return parse_literal(expr)

    def _mix(self, inner, seen):
        args = split_args(inner)
        space = args[0].replace("in", "", 1).strip()

        def comp(a):
            m = re.match(r"(.*?)\s+([\d.]+)%\s*$", a)
            return (m.group(1), float(m.group(2)) / 100) if m else (a, None)

        (ea, pa), (eb, pb) = comp(args[1]), comp(args[2])
        if pa is None and pb is None:
            pa = pb = 0.5
        elif pa is None:
            pa = 1 - pb
        elif pb is None:
            pb = 1 - pa
        A, B = self.color(ea, seen), self.color(eb, seen)
        if A is None or B is None:
            return None
        tot = pa + pb
        wa, wb = pa / tot, pb / tot
        alpha = A.a * wa + B.a * wb
        if alpha == 0:
            return Color(0, 0, 0, 0)
        if space == "oklab":
            la, lb = rgb_to_oklab(A.r, A.g, A.b), rgb_to_oklab(B.r, B.g, B.b)
            mixed = [(x * A.a * wa + y * B.a * wb) / alpha for x, y in zip(la, lb)]
            r, g, b = oklab_to_rgb(*mixed)
        else:  # srgb (premultiplied)
            r, g, b = ((x * A.a * wa + y * B.a * wb) / alpha for x, y in ((A.r, B.r), (A.g, B.g), (A.b, B.b)))
        return Color(r, g, b, alpha * min(1, tot))

    def _relative(self, inner, seen):
        # "<color> calc(l + D) calc(c * M) h"  (also accepts plain l / c)
        m = re.fullmatch(r"\s*(.+?)\s+(calc\(l\s*\+\s*([-\d.]+)\)|l)\s+(calc\(c\s*\*\s*([-\d.]+)\)|c)\s+h\s*", inner)
        if not m:
            return None
        base = self.color(m.group(1), seen)
        if base is None:
            return None
        dl = float(m.group(3) or 0)
        cm = float(m.group(5) or 1)
        L, a, b = rgb_to_oklab(base.r, base.g, base.b)
        C, H = math.hypot(a, b), math.atan2(b, a)
        L, C = min(1, max(0, L + dl)), max(0, C * cm)
        r, g, bb = oklab_to_rgb(L, C * math.cos(H), C * math.sin(H))
        return Color(r, g, bb, base.a)

    def substitute(self, value):
        """Replace every color-mix()/oklch(from) in a declaration value with its resolved colour."""
        out, i = "", 0
        while True:
            m = MODERN_FN.search(value, i)
            if not m:
                return out + value[i:]
            end = find_call(value, m.start())
            c = self.color(value[m.start():end])
            if c is None:
                raise ValueError(f"can't resolve {value[m.start():end]!r}")
            out += value[i:m.start()] + c.css()
            i = end


# ---------------------------------------------------------------- css handling
def iter_rules(css):
    """Yield (selector, body) for top-level and @media-nested rules (one level)."""
    i = 0
    while True:
        j = css.find("{", i)
        if j == -1:
            return
        sel = css[i:j].strip()
        # find matching brace
        depth, k = 0, j
        while k < len(css):
            if css[k] == "{":
                depth += 1
            elif css[k] == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        body = css[j + 1:k]
        sel_clean = re.sub(r"/\*.*?\*/", "", sel, flags=re.S).strip()
        if sel_clean.startswith("@media") or sel_clean.startswith("@supports"):
            yield from ((f"{sel_clean} ⟶ {s}", b) for s, b in iter_rules(body))
        elif not sel_clean.startswith("@"):
            yield sel_clean, body
        i = k + 1


def declarations(body):
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    for part in body.split(";"):
        if ":" in part:
            prop, val = part.split(":", 1)
            yield prop.strip(), val.strip()


def build_block(css):
    css_wo = re.sub(re.escape(START) + r".*?" + re.escape(END), "", css, flags=re.S)
    rules = list(iter_rules(css_wo))
    root_env = {}
    for sel, body in rules:
        if sel == ":root":
            for p, v in declarations(body):
                if p.startswith("--"):
                    root_env[p[2:]] = v
    lines = []
    for sel, body in rules:
        if "⟶" in sel:
            media, sel = sel.split(" ⟶ ", 1)
            if "print" in media:
                continue  # print overrides use plain colours already
        else:
            media = None
        env = dict(root_env)
        if sel.startswith(":root"):
            for p, v in declarations(body):
                if p.startswith("--"):
                    env[p[2:]] = v
        res = Resolver(env)
        fixed = []
        for p, v in declarations(body):
            if MODERN_FN.search(v):
                fixed.append(f"{p}:{res.substitute(v)};")
        if fixed:
            rule = f"{sel}{{{''.join(fixed)}}}"
            lines.append(f"    {media}{{{rule}}}" if media else f"    {rule}")
    if not lines:
        return None
    return (f"  {START}\n"
            f"  /* Plain colours for browsers without color-mix() / relative oklch(). Generated by\n"
            f"     scripts/theme_fallbacks.py for the current theme — re-run it after changing --accent. */\n"
            f"  @supports not (color: oklch(from red l c h)){{\n" + "\n".join(lines) + "\n  }\n"
            f"  {END}\n")


def process(path):
    html = path.read_text(encoding="utf-8")
    s0, s1 = html.index("<style>") + len("<style>"), html.index("</style>")
    css = html[s0:s1]
    css = re.sub(r"\n?  " + re.escape(START) + r".*?" + re.escape(END) + r"\n?", "\n", css, flags=re.S)
    block = build_block(css)
    if block is None:
        return 0
    css = css.rstrip() + "\n\n" + block
    path.write_text(html[:s0] + css + html[s1:], encoding="utf-8")
    return block.count("\n    ")


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    for a in argv:
        for p in sorted(Path().glob(a)) if any(ch in a for ch in "*?[") else [Path(a)]:
            n = process(p)
            print(f"{p}: {n} fallback rule(s)" if n else f"{p}: nothing to do")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

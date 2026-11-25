#!/usr/bin/env python3
"""Checks for the built site in ./public and a few source constraints."""

import base64
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
REQUIRED = [
    "index.html",
    "zh/index.html",
    "publications/index.html",
    "zh/publications/index.html",
    "projects/index.html",
    "zh/projects/index.html",
    "timeline/index.html",
    "zh/timeline/index.html",
    "grants/index.html",
    "zh/grants/index.html",
]
MAIN_PAGES = REQUIRED[:]
BADGE = {"en": "PLACEHOLDER", "zh": "占位"}
VOID = {"meta", "link", "img", "br", "hr", "input", "source", "wbr"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.cur = None
        self.items = []
        self.lang_href = None
        self.hreflang = {}

    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs, void=tag in VOID)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs, void=True)

    def _start(self, tag, attrs, void):
        ad = {k: (v or "") for k, v in attrs}
        classes = set(ad.get("class", "").split())
        if tag == "article" and "data-id" in ad:
            self._open_item(ad, tag)
        elif tag == "div" and ad.get("data-id") == "portrait":
            self._open_item(ad, tag)
        if tag == "span" and "badge" in classes and self.cur is not None:
            self.cur["capture"] = True
            self.cur["buf"] = []
        if tag == "a" and "lang-switch" in classes:
            self.lang_href = ad.get("href", "")
        if tag == "link" and "alternate" in ad.get("rel", "").split() and ad.get("hreflang"):
            self.hreflang[ad["hreflang"]] = ad.get("href", "")
        if tag == "strong" and self.cur is not None:
            self.cur["strong"] = True
            self.cur["strong_buf"] = []
        if not void:
            self.stack.append(tag)

    def _open_item(self, ad, tag):
        self.cur = {
            "id": ad.get("data-id", ""),
            "year": ad.get("data-year"),
            "month": ad.get("data-month"),
            "placeholder": ad.get("data-placeholder", ""),
            "badge": "",
            "capture": False,
            "buf": [],
            "strong": False,
            "strong_buf": [],
            "strong_text": "",
            "depth": len(self.stack) + 1,
            "tag": tag,
        }
        self.items.append(self.cur)

    def handle_endtag(self, tag):
        if self.cur and self.cur["capture"] and tag == "span":
            self.cur["badge"] += "".join(self.cur["buf"]).strip()
            self.cur["capture"] = False
        if self.cur and self.cur["strong"] and tag == "strong":
            self.cur["strong_text"] += "".join(self.cur["strong_buf"])
            self.cur["strong"] = False
        if self.cur and tag == self.cur["tag"] and len(self.stack) == self.cur["depth"]:
            self.cur = None
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_data(self, data):
        if self.cur and self.cur["capture"]:
            self.cur["buf"].append(data)
        if self.cur and self.cur["strong"]:
            self.cur["strong_buf"].append(data)


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def norm(href):
    if not href:
        return ""
    path = urlparse(href).path if "://" in href else href
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path += "/"
    return path


def load(rel):
    path = PUBLIC / rel
    text = path.read_text(encoding="utf-8")
    parser = Page()
    parser.feed(text)
    return text, parser


def parse_pubs(text):
    pubs = []
    parts = re.split(r"\n(?=- id:)", text)
    for part in parts:
        m = re.search(
            r'id:\s*"(?P<id>[^"]+)"\s+placeholder:\s*(?P<ph>true|false)\s+'
            r"type:\s*\w+\s+year:\s*(?P<year>\d+)\s+month:\s*(?P<month>\d+)\s+"
            r"selected:\s*(?P<sel>true|false)",
            part,
        )
        if not m:
            continue
        pubs.append(
            {
                "id": m.group("id"),
                "placeholder": m.group("ph") == "true",
                "year": int(m.group("year")),
                "month": int(m.group("month")),
                "selected": m.group("sel") == "true",
            }
        )
    return pubs


def publication_order(pubs):
    ranked = sorted(
        enumerate(pubs),
        key=lambda item: (item[1]["year"], item[1]["month"], -item[0]),
        reverse=True,
    )
    return [pub for _, pub in ranked]


def placeholder_ids(path):
    text = path.read_text(encoding="utf-8")
    found = []
    parts = re.split(r"\n(?=- id:)", "\n" + text)
    for part in parts:
        idm = re.search(r'id:\s*"?([^"\n]+)"?', part)
        phm = re.search(r"placeholder:\s*(true|false)", part)
        if idm and phm and phm.group(1) == "true":
            found.append(idm.group(1).strip().strip('"'))
    return found


def lang_of(rel):
    return "zh" if rel == "zh/index.html" or rel.startswith("zh/") else "en"


def pub_items(parser):
    return [item for item in parser.items if item["year"] is not None]


def check_order(label, items, expected):
    got = [item["id"] for item in items]
    want = [pub["id"] for pub in expected]
    if got != want:
        fail(f"{label} order {got} != {want}")
    stamps = [(int(item["year"]), int(item["month"])) for item in items]
    for prev, nxt in zip(stamps, stamps[1:]):
        if prev < nxt:
            fail(f"{label} not sorted descending: {stamps}")


def check_head(rel, text):
    head = text.split("</head>", 1)[0]
    low = head.lower()
    if 'name="color-scheme"' not in low and "name=color-scheme" not in low:
        fail(f"{rel} missing color-scheme meta")
    if "light dark" not in low:
        fail(f"{rel} color-scheme meta is incomplete")
    script_at = low.find("<script")
    style_at = low.find("stylesheet")
    if script_at < 0 or style_at < 0 or script_at > style_at:
        fail(f"{rel} theme script does not precede the stylesheet")
    for needle in ("localstorage", "prefers-color-scheme", "data-theme", "colorscheme"):
        if needle not in low:
            fail(f"{rel} theme script missing {needle}")


def check_hreflang(rel, parser):
    missing = {"en", "zh", "x-default"} - set(parser.hreflang)
    if missing:
        fail(f"{rel} missing hreflang {sorted(missing)}")
    if norm(parser.hreflang["x-default"]) != norm(parser.hreflang["en"]):
        fail(f"{rel} x-default is not the English URL")
    page_path = "/" + rel[: -len("index.html")]
    if lang_of(rel) == "zh":
        if norm(parser.hreflang["zh"]) != page_path:
            fail(f"{rel} zh hreflang {parser.hreflang['zh']} != {page_path}")
        en_path = page_path[len("/zh") :] or "/"
        if norm(parser.hreflang["en"]) != en_path:
            fail(f"{rel} en hreflang {parser.hreflang['en']} != {en_path}")
    else:
        if norm(parser.hreflang["en"]) != page_path:
            fail(f"{rel} en hreflang {parser.hreflang['en']} != {page_path}")


def check_placeholders(pages):
    portrait = (ROOT / "data/profile.yaml").read_text(encoding="utf-8")
    portrait_flag = re.search(r"^portrait_placeholder:\s*(true|false)\s*$", portrait, re.M)
    if not portrait_flag:
        fail("profile.yaml has no portrait_placeholder")
    if portrait_flag.group(1) == "true":
        for rel in ("index.html", "zh/index.html"):
            item = next(i for i in pages[rel].items if i["id"] == "portrait")
            if item["placeholder"] != "true" or BADGE[lang_of(rel)] not in item["badge"]:
                fail(f"{rel} portrait placeholder badge missing ({item['badge']!r})")
    data_files = {
        "publications": ROOT / "data/publications.yaml",
        "experience": ROOT / "data/experience.yaml",
        "education": ROOT / "data/education.yaml",
        "grants": ROOT / "data/grants.yaml",
    }
    for kind, path in data_files.items():
        for item_id in placeholder_ids(path):
            targets = []
            if kind == "publications":
                targets = ["publications/index.html", "zh/publications/index.html"]
            else:
                targets = ["index.html", "zh/index.html"]
            for rel in targets:
                match = [i for i in pages[rel].items if i["id"] == item_id]
                if not match:
                    fail(f"{rel} does not render placeholder item {item_id}")
                if BADGE[lang_of(rel)] not in match[0]["badge"]:
                    fail(f"{rel} item {item_id} has no {BADGE[lang_of(rel)]} badge")


def check_cv(html_paths):
    pdfs = list(PUBLIC.rglob("*.pdf"))
    if pdfs:
        fail(f"built site contains PDF files: {pdfs}")
    cv_dir = PUBLIC / "cv"
    if cv_dir.exists() and list(cv_dir.rglob("*.pdf")):
        fail("public/cv contains a PDF while cv param is empty")
    if (ROOT / "static/cv").exists():
        fail("static/cv exists; no CV files should be committed")
    for path in html_paths:
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        for needle in ("cv-en.pdf", "cv-zh.pdf", "download cv", "下载简历", "/cv/"):
            if needle in text:
                fail(f"{path.relative_to(PUBLIC)} contains CV marker {needle!r}")
        if re.search(r"""href\s*=\s*["'][^"']+\.pdf""", text):
            fail(f"{path.relative_to(PUBLIC)} links to a PDF")


SKIP_WALK = {".git", "public", "resources"}


def iter_repo_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_WALK for part in path.relative_to(ROOT).parts):
            continue
        yield path


def check_originality():
    pat = re.compile(
        base64.b64decode(
            "YWwtZm9saW98YWNhZGVtaWNwYWdlc3x3b3djaGVteXxodWdvLWJsb3h8bWluaW1hbC1taXN0YWtlcw=="
        ).decode(),
        re.IGNORECASE,
    )
    if (ROOT / "themes").exists():
        fail("themes/ directory exists")
    config = (ROOT / "hugo.toml").read_text(encoding="utf-8")
    for line in config.splitlines():
        code = line.split("#", 1)[0].strip()
        if re.match(r"(?i)^theme\s*=", code):
            fail("hugo.toml sets a theme")
    hits = []
    for path in iter_repo_files():
        if path.relative_to(ROOT).parts[0] == "docs":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if pat.search(text):
            hits.append(str(path.relative_to(ROOT)))
    if hits:
        fail("banned theme names found:\n" + "\n".join(hits))


def check_hit_targets():
    css = (ROOT / "assets/css/main.css").read_text(encoding="utf-8")
    match = re.search(
        r"\.nav a,\s*\.lang-switch,.*?\.download\s*\{([^}]+)\}",
        css,
        re.S,
    )
    if not match:
        fail("hit-target CSS rule is missing")
    body = match.group(1)
    for prop in ("min-width", "min-height"):
        found = re.search(rf"{prop}\s*:\s*(\d+)px", body)
        if not found or int(found.group(1)) < 44:
            fail(f"hit targets need {prop} of at least 44px")


def check_alias():
    path = PUBLIC / "en" / "index.html"
    if not path.is_file():
        fail("missing /en/ redirect page")
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    if "noindex" not in text:
        fail("/en/ redirect is missing robots noindex")
    if "refresh" not in text:
        fail("/en/ redirect is missing the meta refresh")


def check_private():
    pat = re.compile(
        base64.b64decode("Z2VudHJpZmljYXRpb24=").decode(),
        re.IGNORECASE,
    )
    for path in iter_repo_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        if pat.search(text):
            fail(f"{path.relative_to(ROOT)} contains excluded CV text")


def _attr(blob, name):
    match = re.search(
        rf"{name}=(?:\"([^\"]*)\"|'([^']*)'|([^\s>]+))",
        blob,
    )
    if not match:
        return None
    return next(group for group in match.groups() if group is not None)


def _timeline_items(html):
    items = []
    for match in re.finditer(r"<li\b([^>]*)>", html, re.I):
        blob = match.group(1)
        if _attr(blob, "data-tl-type") is None:
            continue
        items.append(
            {
                "type": _attr(blob, "data-tl-type"),
                "id": _attr(blob, "data-id") or "",
                "from": _attr(blob, "data-from") or "",
                "start": _attr(blob, "data-start") or "",
                "end": _attr(blob, "data-end") or "",
                "source": _attr(blob, "data-source") or "",
                "hidden": "hidden" in blob.lower().split(),
            }
        )
    return items


def _stamp(value, empty):
    if not value:
        return empty
    bits = value.split("-")
    year = int(bits[0])
    month = int(bits[1]) if len(bits) > 1 else 0
    return year * 100 + month


def _timeline_sort_key(item):
    return (
        _stamp(item["start"], 0),
        _stamp(item["end"], 999999),
        item["id"],
    )


def _parse_timeline_rows():
    rows = []
    current = None
    for line in (ROOT / "data/timeline.yaml").read_text(encoding="utf-8").splitlines():
        if line.startswith("- id:"):
            if current:
                rows.append(current)
            current = {"id": line.split(":", 1)[1].strip().strip('"'), "end": ""}
            continue
        if current is None or not line.startswith("  ") or line.startswith("    "):
            continue
        key, _, value = line.strip().partition(":")
        value = value.strip().strip('"')
        if value in ("null", "~"):
            value = ""
        current[key] = value
    if current:
        rows.append(current)
    return rows


def _ids_in_data(filename):
    text = (ROOT / "data" / filename).read_text(encoding="utf-8")
    return set(re.findall(r'(?m)^- id:\s*"?([^"\n]+)"?', text))


def _markdown_intro(path):
    raw = path.read_text(encoding="utf-8")
    body = raw.split("---", 2)[-1]
    paragraph = []
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("- "):
            if paragraph:
                break
            continue
        paragraph.append(stripped)
    return " ".join(paragraph)


def _nav_links(html):
    nav = re.search(r"<nav\b[^>]*>(.*?)</nav>", html, re.I | re.S)
    if not nav:
        return []
    links = []
    for match in re.finditer(r"<a\b([^>]*)>(.*?)</a>", nav.group(1), re.I | re.S):
        href = _attr(match.group(1), "href") or ""
        current = "aria-current" in match.group(1) and "page" in match.group(1)
        links.append((norm(href), re.sub(r"<[^>]+>", "", match.group(2)).strip(), current))
    return links


def _page_path(rel):
    if rel == "index.html":
        return "/"
    if rel == "zh/index.html":
        return "/zh/"
    return "/" + rel[: -len("index.html")]


def _sibling_path(rel):
    if rel.startswith("zh/"):
        rest = rel[len("zh/") :]
        if rest == "index.html":
            return "/"
        return "/" + rest[: -len("index.html")]
    if rel == "index.html":
        return "/zh/"
    return "/zh/" + rel[: -len("index.html")]


def ac1_home():
    """AC1: home is hero, a short intro, research directions, and four cards."""
    homes = {
        "index.html": ROOT / "content/_index.en.md",
        "zh/index.html": ROOT / "content/_index.zh.md",
    }
    en_intro = _markdown_intro(homes["index.html"])
    if len(en_intro.split()) > 60:
        fail(f"English home intro is {len(en_intro.split())} words")
    zh_intro = _markdown_intro(homes["zh/index.html"])
    if len(zh_intro) > 100:
        fail(f"Chinese home intro is {len(zh_intro)} characters")
    for rel, prefix in (("index.html", ""), ("zh/index.html", "/zh")):
        text, _ = load(rel)
        for marker in ("data-timeline", "tl-track", "grants-heading", "class=pub", 'class="pub"'):
            if marker in text:
                fail(f"{rel} still contains {marker}")
        for path in ("/publications/", "/timeline/", "/grants/", "/projects/"):
            href = prefix + path
            if href not in text:
                fail(f"{rel} is missing a card link to {href}")
        if text.count("<li") < 5:
            fail(f"{rel} is missing the research directions")


def ac2_nav():
    """AC2: five nav links, current page, and the sibling language toggle."""
    labels = {
        "en": ["About", "Publications", "Timeline / CV", "Grants", "Projects & Code"],
        "zh": ["关于", "论文", "时间线 / 简历", "资助", "项目与代码"],
    }
    for rel in MAIN_PAGES:
        text, parser = load(rel)
        lang = lang_of(rel)
        links = _nav_links(text)
        if [label for _, label, _ in links] != labels[lang]:
            fail(f"{rel} nav labels {[label for _, label, _ in links]}")
        here = _page_path(rel)
        paths = [href for href, _, _ in links]
        prefix = "/zh" if lang == "zh" else ""
        expected = [norm(prefix + path) for path in ("/", "/publications/", "/timeline/", "/grants/", "/projects/")]
        if lang == "zh":
            expected = [norm(path) for path in ("/zh/", "/zh/publications/", "/zh/timeline/", "/zh/grants/", "/zh/projects/")]
        if paths != expected:
            fail(f"{rel} nav paths {paths}")
        current = [href for href, _, on in links if on]
        if current != [here]:
            fail(f"{rel} aria-current is {current}, expected {here}")
        for href in paths:
            target = "index.html" if href == "/" else href.strip("/") + "/index.html"
            if not (PUBLIC / target).is_file():
                fail(f"{rel} nav target {href} is missing from public/")
        if norm(parser.lang_href) != _sibling_path(rel):
            fail(f"{rel} language toggle points to {parser.lang_href}")


def ac3_timeline():
    """AC3: one horizontal education and work track, details in the HTML."""
    for rel in ("timeline/index.html", "zh/timeline/index.html"):
        text, _ = load(rel)
        items = [item for item in _timeline_items(text) if item["type"] in ("education", "position")]
        if len(items) != 7:
            fail(f"{rel} has {len(items)} education/position entries")
        if sum(item["type"] == "education" for item in items) != 3:
            fail(f"{rel} does not have 3 education entries")
        if sum(item["type"] == "position" for item in items) != 4:
            fail(f"{rel} does not have 4 position entries")
        if any(item["type"] in ("publication", "milestone") for item in _timeline_items(text)):
            fail(f"{rel} still lists publications or grants")
        years = [int(year) for year in re.findall(r'data-year="?(\d{4})', text)]
        if years != list(range(2008, 2027)):
            fail(f"{rel} year ticks {years[:3]}...{years[-3:]}")
        if text.lower().count("<details") < 7:
            fail(f"{rel} details are not in the HTML")
        if 'alt=""' not in text and "alt=''" not in text:
            fail(f"{rel} flag images need an empty alt")
        for code in ("cn", "au", "de", "ca", "dk"):
            if f"/flags/{code}.svg" not in text:
                fail(f"{rel} is missing the {code} flag")
    script = re.search(r"<script\b[^>]*>(.*?)</script>", Path(PUBLIC / "timeline/index.html").read_text(encoding="utf-8"), re.I | re.S)
    if not script or "mouseenter" not in script.group(1) or "scrollLeft" not in script.group(1):
        fail("timeline hover script is missing")
    if len(script.group(1).strip().splitlines()) > 15:
        fail("timeline script is longer than 15 lines")


def ac4_timeline_mobile():
    """AC4: the year track scrolls inside the page, with snap points."""
    css = (ROOT / "assets/css/main.css").read_text(encoding="utf-8")
    for needle in ("overflow-x: auto", "scroll-snap-type", "scroll-snap-align", "overscroll-behavior-x", "--tl-year"):
        if needle not in css:
            fail(f"timeline CSS is missing {needle}")
    for rel in ("timeline/index.html", "zh/timeline/index.html"):
        text, _ = load(rel)
        if not re.search(r'tabindex="?0"?', text):
            fail(f"{rel} track is not keyboard-focusable")
        if not re.search(r'role="?region"?', text):
            fail(f"{rel} track is missing role=region")


def ac5_no_amounts():
    """AC5: no currency amounts and no amount field in the built site or data."""
    currency = re.compile(
        r"(?i)(\$|€|£|¥|\b(?:DKK|EUR|USD|CAD|GBP|kr)\b\.?)\s*\d|\d[\d.,]*\s*(?:DKK|EUR|USD|CAD|kr)\b|\$\s*(?:CAD|USD)"
    )
    suffixes = {".html", ".xml", ".txt", ".js", ".css"}
    for path in PUBLIC.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in suffixes:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if currency.search(text):
            fail(f"{path.relative_to(PUBLIC)} contains a currency amount")
        if path.suffix.lower() == ".html" and re.search(r"\bamount\b", text, re.I):
            fail(f"{path.relative_to(PUBLIC)} contains the word amount")
    for path in (ROOT / "data").rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if currency.search(text):
            fail(f"{path.relative_to(ROOT)} contains a currency amount")
        if re.search(r"(?m)^\s*amount\s*:", text):
            fail(f"{path.relative_to(ROOT)} still has an amount key")
    extra = [ROOT / "README.md", ROOT / "layouts", ROOT / "content", ROOT / "docs"]
    for base in extra:
        files = [base] if base.is_file() else list(base.rglob("*"))
        for path in files:
            if not path.is_file() or path == ROOT / "scripts/check_site.py":
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if currency.search(text):
                fail(f"{path.relative_to(ROOT)} contains a currency amount")
    grants, _ = load("grants/index.html")
    ids = re.findall(r'data-id="?([^"\s>]+)', grants)
    if len(ids) != 4:
        fail(f"grants page lists {len(ids)} records")


def ac6_theme_variables():
    """AC6: new blocks use the existing variables; dark theme still switches them."""
    css = (ROOT / "assets/css/main.css").read_text(encoding="utf-8")
    if '[data-theme="dark"]' not in css:
        fail("dark theme variables are missing")
    for match in re.finditer(r"([^{}]+)\{([^{}]+)\}", css):
        selector = match.group(1)
        if not re.search(r"\.tl-|\.home-card|\.tl-scroll|\.tl-track", selector):
            continue
        if re.search(r"#[0-9a-fA-F]{3,8}\b", match.group(2)):
            fail(f"new CSS uses a raw color in {selector.strip()}")


def ac7_i18n_parity():
    """AC7: both i18n tables match, and every new page exists in both languages."""
    en_keys = _flat_keys(ROOT / "i18n/en.yaml")
    zh_keys = _flat_keys(ROOT / "i18n/zh.yaml")
    if en_keys != zh_keys:
        fail(f"i18n key mismatch {set(en_keys) ^ set(zh_keys)}")
    required = {
        "nav_about",
        "nav_publications",
        "nav_timeline",
        "nav_grants",
        "nav_projects",
        "home_explore",
        "card_publications_desc",
        "card_timeline_desc",
        "card_grants_desc",
        "card_projects_desc",
        "summary",
        "timeline_region",
        "timeline_legend",
        "type_education",
        "type_position",
        "grants",
        "details",
    }
    missing = required - set(en_keys)
    if missing:
        fail(f"missing i18n keys {sorted(missing)}")
    removed = {
        "filter_all",
        "filter_education",
        "filter_position",
        "filter_publication",
        "filter_milestone",
        "timeline_filters",
        "type_publication",
        "type_milestone",
        "full_timeline",
        "experience",
        "education",
    }
    leftover = removed & set(en_keys)
    if leftover:
        fail(f"unused i18n keys still present {sorted(leftover)}")
    for rel in ("grants/index.html", "zh/grants/index.html", "timeline/index.html", "zh/timeline/index.html"):
        if not (PUBLIC / rel).is_file():
            fail(f"missing {rel}")


def ac8_flags():
    """AC8: the five vendored flags match the published checksums and the credit is present."""
    expected = {
        "cn.svg": "981da9bdf82d48e31691f20578cefcb26cf7d0bd95e4ebd5c0df00bdfe988c1a",
        "au.svg": "cbb2206c5e59a25d79228306af973666a191e163f0ae337681f447977e6edb18",
        "de.svg": "efd480af5a154a7651f29da23ee0d09dbc892410fb4041898ddf8face336c575",
        "ca.svg": "345ec9dac057e203f1331b2d3f9f473789864edaee1182a26bc261356bcf72f1",
        "dk.svg": "d2847c0bd7a1fb97977ee51f2f618c5ebc5898dd66ef9804f187613c27bdca1a",
    }
    folder = ROOT / "static/flags"
    found = sorted(path.name for path in folder.glob("*.svg")) if folder.is_dir() else []
    if found != sorted(expected):
        fail(f"static/flags SVGs are {found}")
    import hashlib
    for name, digest in expected.items():
        actual = hashlib.sha256((folder / name).read_bytes()).hexdigest()
        if actual != digest:
            fail(f"{name} sha256 {actual} != {digest}")
    licence = folder / "LICENSE-flag-icons.txt"
    if not licence.is_file() or "MIT" not in licence.read_text(encoding="utf-8"):
        fail("static/flags/LICENSE-flag-icons.txt is missing the MIT text")
    credit = "Flag SVGs from flag-icons v7.6.0 by Panayiotis Lipiridis, MIT licence, https://github.com/lipis/flag-icons"
    for path in (ROOT / "README.md", ROOT / "docs/references.md"):
        if credit not in path.read_text(encoding="utf-8"):
            fail(f"{path.relative_to(ROOT)} is missing the flag credit")
    for html in PUBLIC.rglob("*.html"):
        text = html.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"https?://[^\"'\s>]*flag", text, re.I):
            fail(f"{html.relative_to(PUBLIC)} loads a flag from an external host")


def ac9_exclusions():
    """AC9: phone, referee contacts, non-awarded grants, awards, blog, and CV PDF stay out."""
    needles = [
        base64.b64decode(value).decode()
        for value in (
            "KzQ1IDUyODAwNzE3",
            "NTI4MDA3MTc=",
            "bG91aXNlLnBpbG90ZUBtY2dpbGwuY2E=",
            "bWFyem9saW5p",
            "Y25vcnJpc0B1YWxiZXJ0YS5jYQ==",
            "Z2VudHJpZmljYXRpb24=",
            "YnJhaW4gYWdl",
            "cGF0aWVudC1yZXBvcnRlZCBvdXRjb21lcw==",
        )
    ]
    roots = [ROOT / "content", ROOT / "data", ROOT / "layouts", ROOT / "i18n", PUBLIC]
    for folder in roots:
        for path in folder.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            for needle in needles:
                if needle.lower() in text:
                    fail(f"{path} contains excluded private or non-awarded text")
            if path.suffix.lower() == ".html" and re.search(r"\bawards\b", text):
                fail(f"{path} contains an awards list")
    if (ROOT / "content/blog").exists() or (ROOT / "content/posts").exists() or (ROOT / "data/awards.yaml").exists():
        fail("blog or awards content is present")
    if list(PUBLIC.rglob("*.pdf")):
        fail("public/ contains a PDF")


def ac10_originality():
    """AC10: the implementation scan stays clean and the reference image is not committed."""
    check_originality()
    for banned in (ROOT / "_layouts", ROOT / "_sass", ROOT / "_includes", ROOT / "docs/timeline-reference.png"):
        if banned.exists():
            fail(f"{banned.relative_to(ROOT)} must not be in the repo")


def ac11_delivery():
    """AC11: the repository licence stays the MIT grant for Yusheng Zhou."""
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "MIT License" not in text or "Copyright (c) 2026 Yusheng Zhou" not in text:
        fail("LICENSE is not the MIT text for Yusheng Zhou")



def main():
    if not PUBLIC.is_dir():
        fail("public/ is missing; build the site first")
    for rel in REQUIRED:
        if not (PUBLIC / rel).is_file():
            fail(f"missing {rel}")
    pubs = parse_pubs((ROOT / "data/publications.yaml").read_text(encoding="utf-8"))
    if len(pubs) != 10:
        fail(f"expected 10 publications, found {len(pubs)}")
    ordered = publication_order(pubs)
    selected = [pub for pub in ordered if pub["selected"]]
    if len(selected) > 3:
        fail("more than 3 publications are selected")
    pages = {}
    html_paths = list(PUBLIC.rglob("*.html"))
    for rel in MAIN_PAGES:
        text, parser = load(rel)
        pages[rel] = parser
        check_head(rel, text)
        check_hreflang(rel, parser)
        if parser.lang_href is None:
            fail(f"{rel} has no language toggle")
    en_pubs, zh_pubs = pages["publications/index.html"], pages["zh/publications/index.html"]
    if norm(en_pubs.lang_href) != "/zh/publications/":
        fail(f"EN publications toggle points to {en_pubs.lang_href}")
    if norm(zh_pubs.lang_href) != "/publications/":
        fail(f"ZH publications toggle points to {zh_pubs.lang_href}")
    if norm(pages["index.html"].lang_href) != "/zh/":
        fail(f"EN home toggle points to {pages['index.html'].lang_href}")
    if norm(pages["zh/index.html"].lang_href) != "/":
        fail(f"ZH home toggle points to {pages['zh/index.html'].lang_href}")
    check_order("publications", pub_items(en_pubs), ordered)
    check_order("zh publications", pub_items(zh_pubs), ordered)
    for rel in ("publications/index.html", "zh/publications/index.html"):
        for item in pub_items(pages[rel]):
            if item["strong_text"] != "Yusheng Zhou":
                fail(f"{rel} does not bold Yusheng Zhou on {item['id']}")
    home_en, _ = load("index.html")
    if "mailto:yushengzhou29@hotmail.com" not in home_en:
        fail("home is missing the mailto link")
    projects_en, projects_parser = load("projects/index.html")
    if "No projects are listed yet." not in projects_en:
        fail("EN projects page has no empty state")
    projects_zh, _ = load("zh/projects/index.html")
    if "尚未列出项目。" not in projects_zh:
        fail("ZH projects page has no empty state")
    if pub_items(projects_parser):
        fail("projects page rendered publications")
    check_placeholders(pages)
    check_cv(html_paths)
    check_hit_targets()
    check_alias()
    check_originality()
    check_private()
    ac1_home()
    ac2_nav()
    ac3_timeline()
    ac4_timeline_mobile()
    ac5_no_amounts()
    ac6_theme_variables()
    ac7_i18n_parity()
    ac8_flags()
    ac9_exclusions()
    ac10_originality()
    ac11_delivery()
    print("ok")


if __name__ == "__main__":
    main()

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


def ac1_timeline_pages():
    """AC1: both timeline pages, reverse chronology, sibling language toggle."""
    rows = _parse_timeline_rows()
    if len(rows) < 21:
        fail(f"timeline.yaml has {len(rows)} rows, expected at least 21")
    expected = sorted(rows, key=_timeline_sort_key, reverse=True)
    for rel, other in (
        ("timeline/index.html", "/zh/timeline/"),
        ("zh/timeline/index.html", "/timeline/"),
    ):
        text, parser = load(rel)
        if norm(parser.lang_href) != other:
            fail(f"{rel} language toggle points to {parser.lang_href}")
        if 'data-timeline="full"' not in text and "data-timeline=full" not in text:
            fail(f"{rel} is not the full timeline")
        items = _timeline_items(text)
        got = [(item["id"], item["start"], item["end"]) for item in items]
        want = [(row["id"], row["start"], row.get("end", "")) for row in expected]
        if got != want:
            fail(f"{rel} timeline order {got} != {want}")
        if 'id="experience-heading"' in text or "id=experience-heading" in text:
            fail(f"{rel} still has a standalone experience block")
    home, _ = load("index.html")
    if "data-timeline=preview" not in home and 'data-timeline="preview"' not in home:
        fail("homepage is missing the timeline preview")
    if "id=experience-heading" in home or 'id="experience-heading"' in home:
        fail("homepage still has a standalone experience block")
    if "id=education-heading" in home or 'id="education-heading"' in home:
        fail("homepage still has a standalone education block")
    preview = _timeline_items(home)
    if not preview or any(item["type"] not in ("education", "position") for item in preview):
        fail("homepage timeline preview must be education and positions only")
    if "Full timeline" not in home:
        fail("homepage timeline preview has no full-timeline link")
    css = (ROOT / "assets/css/main.css").read_text(encoding="utf-8")
    if "[data-theme=\"dark\"]" not in css or "var(--text)" not in css or "var(--line)" not in css:
        fail("timeline styling must keep the existing light and dark variables")


def ac2_timeline_mobile():
    """AC2: single column, 44px controls, homepage identity stays first."""
    css = (ROOT / "assets/css/main.css").read_text(encoding="utf-8")
    if re.search(r"\.timeline\s*\{[^}]*grid-template-columns", css, re.S):
        fail("timeline must not use a side-column grid")
    for selector in (".tl-filters button", ".timeline summary"):
        match = re.search(rf"{re.escape(selector)}\s*\{{([^}}]+)\}}", css, re.S)
        if not match:
            fail(f"missing hit-target rule for {selector}")
        body = match.group(1)
        for prop in ("min-width", "min-height"):
            found = re.search(rf"{prop}\s*:\s*(\d+)px", body)
            if not found or int(found.group(1)) < 44:
                fail(f"{selector} needs {prop} of at least 44px")
    home, _ = load("index.html")
    if home.find("<h1") == -1 or home.find("mailto:") == -1:
        fail("homepage is missing the name or email")
    if home.find("<h1") > home.find("mailto:"):
        fail("homepage email appears before the name")
    if "data-timeline=preview" in home or 'data-timeline="preview"' in home:
        if home.find("mailto:") > home.find("data-timeline"):
            fail("homepage timeline is above the name and email")


def ac3_timeline_filters():
    """AC3: every item is in the HTML; filters are progressive enhancement."""
    text, _ = load("timeline/index.html")
    items = _timeline_items(text)
    if any(item["hidden"] for item in items):
        fail("timeline items are hidden without JS")
    if len(items) != len(_parse_timeline_rows()):
        fail("full timeline does not render every composed item")
    if "data-tl-filter=all" not in text and 'data-tl-filter="all"' not in text:
        fail("timeline filters are missing")
    if not re.search(r"<button\b[^>]*data-tl-filter", text):
        fail("timeline filters are not buttons")
    if not re.search(r"<script\b[^>]*>[\s\S]*data-tl-filter", text):
        fail("timeline filter script is missing")
    css = (ROOT / "assets/css/main.css").read_text(encoding="utf-8")
    if re.search(r"\.timeline\s+li\s*\{[^}]*display\s*:\s*none", css, re.S):
        fail("timeline CSS hides items before JS runs")


def ac4_timeline_semantics():
    """AC4: ordered list, machine dates, keyboard details, reduced motion."""
    for rel in ("timeline/index.html", "zh/timeline/index.html", "index.html"):
        text, _ = load(rel)
        if "<ol" not in text.lower() or "timeline" not in text.lower():
            fail(f"{rel} timeline is not an ordered list")
        for match in re.finditer(r"<li\b([^>]*)>([\s\S]*?)</li>", text, re.I):
            if _attr(match.group(1), "data-tl-type") is None:
                continue
            if not re.search(r"<time\b[^>]*datetime=", match.group(2), re.I):
                fail(f"{rel} item {_attr(match.group(1), 'data-id')} has no time datetime")
    text, _ = load("timeline/index.html")
    if "<details" not in text.lower():
        fail("timeline position or grant detail is not in details")
    css = (ROOT / "assets/css/main.css").read_text(encoding="utf-8")
    if "prefers-reduced-motion" not in css:
        fail("CSS does not disable motion for prefers-reduced-motion")


def ac5_timeline_exclusions():
    """AC5: no phone, referee contacts, or non-awarded grants; items trace to data."""
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
    by_file = {
        "experience": _ids_in_data("experience.yaml"),
        "education": _ids_in_data("education.yaml"),
        "publications": _ids_in_data("publications.yaml"),
        "grants": _ids_in_data("grants.yaml"),
    }
    text, _ = load("timeline/index.html")
    if re.search(r"\bVIP\b", text):
        fail("timeline shows the ORCID VIP title")
    if "2028-10" in text or "2028-10-31" in text:
        fail("timeline shows an Aarhus contract end date")
    if "Postdoctoral Researcher" not in text or "Present" not in text:
        fail("Aarhus role is not the CV wording")
    for item in _timeline_items(text):
        if item["source"] not in ("cv", "orcid", "cv+orcid"):
            fail(f"{item['id']} has no CV or ORCID source")
        if item["id"] not in by_file.get(item["from"], set()):
            fail(f"{item['id']} is not in data/{item['from']}")
        if item["type"] == "publication" and item["source"] != "orcid":
            fail(f"{item['id']} publication is not marked orcid")


def ac6_timeline_originality():
    """AC6: implementation does not reuse known theme or reference-site names."""
    pat = re.compile(
        base64.b64decode(
            "YWwtZm9saW98YWNhZGVtaWNwYWdlc3x3b3djaGVteXxodWdvLWJsb3h8bWluaW1hbC1taXN0YWtlc3xsaXpoZW5nfGx6LWNwYXRofGx6LWNhcmVlcnzotoXnur/mgKd8eXV6aGVuZyBzdW585a2Z54Wc5b6B"
        ).decode(),
        re.IGNORECASE,
    )
    hits = []
    for path in iter_repo_files():
        rel = path.relative_to(ROOT)
        if rel.parts[0] == "docs":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if pat.search(text) or re.search(r"\blz-[a-z]", text):
            hits.append(str(rel))
    if hits:
        fail("reference or theme names found:\n" + "\n".join(hits))


def _flat_keys(path):
    keys = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or line.startswith(" "):
            continue
        keys.append(stripped.split(":", 1)[0])
    return keys


def ac7_timeline_ci_surface():
    """AC7: new routes and both i18n tables are part of the existing build."""
    for rel in ("timeline/index.html", "zh/timeline/index.html"):
        if not (PUBLIC / rel).is_file():
            fail(f"missing {rel}")
    en_keys = _flat_keys(ROOT / "i18n/en.yaml")
    zh_keys = _flat_keys(ROOT / "i18n/zh.yaml")
    if en_keys != zh_keys:
        fail(f"i18n key mismatch {set(en_keys) ^ set(zh_keys)}")
    for key in ("nav_timeline", "full_timeline", "filter_all", "type_publication"):
        if key not in en_keys:
            fail(f"missing i18n key {key}")


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
    check_order("selected", pub_items(pages["index.html"]), selected)
    check_order("zh selected", pub_items(pages["zh/index.html"]), selected)
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
    ac1_timeline_pages()
    ac2_timeline_mobile()
    ac3_timeline_filters()
    ac4_timeline_semantics()
    ac5_timeline_exclusions()
    ac6_timeline_originality()
    ac7_timeline_ci_surface()
    print("ok")


if __name__ == "__main__":
    main()

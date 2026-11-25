#!/usr/bin/env python3
"""Checks for the built site in ./public and a few source constraints."""

import base64
import re
import subprocess
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


def check_originality():
    pat = base64.b64decode(
        "YWwtZm9saW98YWNhZGVtaWNwYWdlc3x3b3djaGVteXxodWdvLWJsb3h8bWluaW1hbC1taXN0YWtlcw=="
    ).decode()
    if (ROOT / "themes").exists():
        fail("themes/ directory exists")
    config = (ROOT / "hugo.toml").read_text(encoding="utf-8")
    for line in config.splitlines():
        code = line.split("#", 1)[0].strip()
        if re.match(r"(?i)^theme\s*=", code):
            fail("hugo.toml sets a theme")
    proc = subprocess.run(
        ["rg", "-i", "-e", pat, "."],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if proc.returncode == 0:
        fail("banned theme names found:\n" + proc.stdout)
    if proc.returncode not in (0, 1):
        fail(proc.stderr or "rg failed")


def check_private():
    banned = ("gentrification",)
    roots = [PUBLIC, ROOT / "content", ROOT / "data", ROOT / "layouts", ROOT / "i18n"]
    for folder in roots:
        for path in folder.rglob("*"):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            for needle in banned:
                if needle in text:
                    fail(f"{path} contains private or excluded CV text {needle!r}")


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
    check_originality()
    check_private()
    print("ok")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Construit le blog statique (dossier docs/) à partir de content/*.md.

Stdlib uniquement. Usage : python3 tools/build.py
Variables facultatives :
  SITE_URL       défaut : https://blog.tajweedtutorai.com
  CUSTOM_DOMAIN  écrit docs/CNAME (nécessaire pour GitHub Pages avec un domaine perso)
"""
import html
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUT = ROOT / "docs"
SITE_URL = os.environ.get("SITE_URL", "https://blog.tajweedtutorai.com").rstrip("/")
CUSTOM_DOMAIN = os.environ.get("CUSTOM_DOMAIN", "").strip()
APP_URL = "https://tajweedtutorai.com"
REQUIRED = ("title", "description", "lang", "slug", "date")
LANGS = {"fr": "Français", "en": "English"}
SLUG_RE = re.compile(r"^[a-z0-9-]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

CSS = (
    "body{font-family:system-ui,sans-serif;max-width:720px;margin:2rem auto;"
    "padding:0 1rem;line-height:1.6;color:#222}"
    "a{color:#0a6}header a{font-weight:bold;text-decoration:none;color:#222}"
    ".cta{border:1px solid #0a6;padding:1rem;border-radius:8px;margin:2rem 0}"
    ".desc{color:#555;font-style:italic}"
)


def parse(path):
    """Lit le front matter (entre deux lignes ---) et le corps Markdown."""
    text = path.read_text(encoding="utf-8")
    meta, body = {}, text
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if match:
        for line in match.group(1).splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip().strip('"')
        body = match.group(2)
    return meta, body


def inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" rel="noopener">\1</a>', text)
    return text


def markdown_to_html(body):
    """Conversion volontairement minimale : titres, paragraphes, listes."""
    out, in_list = [], False
    for raw in body.strip().splitlines():
        line = raw.rstrip()
        if not line:
            if in_list:
                out.append("</ul>")
                in_list = False
            continue
        if line.startswith("- "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(line[2:])}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        for level in (3, 2, 1):
            if line.startswith("#" * level + " "):
                out.append(f"<h{level}>{inline(line[level + 1:])}</h{level}>")
                break
        else:
            out.append(f"<p>{inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def cta(lang, slug):
    url = f"{APP_URL}/?utm_source=blog&utm_medium=seo&utm_campaign={slug}"
    if lang == "fr":
        text, button = "Vous voulez un retour sur votre récitation ?", "Essayer Tajweed Tutor AI"
    else:
        text, button = "Want feedback on your recitation?", "Try Tajweed Tutor AI"
    return f'<div class="cta"><p>{text}</p><p><a href="{url}">{button}</a></p></div>'


def page(meta, body_html, alternates, title, description):
    return (
        "<!doctype html>\n"
        f'<html lang="{meta["lang"]}"><head><meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f"<title>{html.escape(title)}</title>\n"
        f'<meta name="description" content="{html.escape(description)}">\n'
        f"{alternates}\n"
        f"<style>{CSS}</style></head><body>\n"
        f'<header><a href="/">Blog Tajweed</a></header>\n<main>{body_html}</main>\n'
        f'<footer><p><a href="{APP_URL}">tajweedtutorai.com</a></p></footer>\n'
        "</body></html>\n"
    )


def index_page(groups):
    sections = []
    for lang, items in groups.items():
        lis = "".join(
            f'<li><a href="/{lang}/{m["slug"]}/">{html.escape(m["title"])}</a></li>' for m in items
        )
        sections.append(f"<h2>{LANGS[lang]}</h2><ul>{lis}</ul>")
    return page(
        {"lang": "fr"}, "<h1>Blog Tajweed</h1>" + "".join(sections), "",
        "Blog Tajweed", "Articles sur le tajwid et la récitation du Coran.",
    )


def main():
    if not CONTENT.is_dir():
        sys.exit("Dossier content/ introuvable")

    articles = []
    for path in sorted(CONTENT.glob("*.md")):
        meta, body = parse(path)
        missing = [key for key in REQUIRED if not meta.get(key)]
        if missing:
            sys.exit(f"{path.name} : champs manquants {missing}")
        if not SLUG_RE.match(meta["slug"]):
            sys.exit(f"{path.name} : slug invalide (minuscules, chiffres, tirets)")
        if meta["lang"] not in LANGS:
            sys.exit(f"{path.name} : langue inconnue '{meta['lang']}'")
        if not DATE_RE.match(meta["date"]):
            sys.exit(f"{path.name} : date au format AAAA-MM-JJ attendue")
        articles.append((meta, body))

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    sitemap_urls = [(f"{SITE_URL}/", None)]
    groups = {lang: [] for lang in LANGS}

    for meta, body in articles:
        lang, slug = meta["lang"], meta["slug"]
        target = OUT / lang / slug
        if target.exists():
            sys.exit(f"Doublon : {lang}/{slug}")
        target.mkdir(parents=True)

        url = f"{SITE_URL}/{lang}/{slug}/"
        alternates = f'<link rel="canonical" href="{url}">\n<link rel="alternate" hreflang="{lang}" href="{url}">'
        if meta.get("alt"):
            other = meta["alt"].strip("/").split("/")[0]
            alternates += f'\n<link rel="alternate" hreflang="{other}" href="{SITE_URL}{meta["alt"]}">'

        body_html = (
            f"<article><h1>{html.escape(meta['title'])}</h1>"
            f'<p class="desc">{html.escape(meta["description"])}</p>'
            f"{markdown_to_html(body)}{cta(lang, slug)}</article>"
        )
        (target / "index.html").write_text(
            page(meta, body_html, alternates, meta["title"], meta["description"]), encoding="utf-8"
        )
        groups[lang].append(meta)
        sitemap_urls.append((url, meta["date"]))

    (OUT / "index.html").write_text(index_page(groups), encoding="utf-8")

    entries = []
    for loc, lastmod in sitemap_urls:
        lastmod_xml = f"<lastmod>{lastmod}</lastmod>" if lastmod else ""
        entries.append(f"  <url><loc>{loc}</loc>{lastmod_xml}</url>")
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    (OUT / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8"
    )
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    if CUSTOM_DOMAIN:
        (OUT / "CNAME").write_text(CUSTOM_DOMAIN + "\n", encoding="utf-8")

    print(f"OK : {len(articles)} article(s), {len(sitemap_urls)} URL dans le sitemap -> docs/")


if __name__ == "__main__":
    main()

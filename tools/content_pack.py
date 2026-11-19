#!/usr/bin/env python3
"""Génère le lot de publications de la semaine dans social/packs/AAAA-Www.md.

Lit social/ideas.json, prend PER_WEEK idées en tournant d'une semaine à l'autre,
et écrit un fichier prêt à copier : script, légende, hashtags, lien UTM.
Les publications restent manuelles (TikTok Studio, Meta Business Suite).

Stdlib uniquement. Usage : python3 tools/content_pack.py [AAAA-MM-JJ]
"""
import json
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parent.parent
IDEAS = ROOT / "social" / "ideas.json"
PACKS = ROOT / "social" / "packs"
APP_URL = "https://tajweedtutorai.com"
PER_WEEK = 5
PLATFORM_LABEL = {
    "tiktok": "TikTok (TikTok Studio, sur ordinateur)",
    "instagram": "Instagram Reels (Meta Business Suite)",
}


def utm_link(idea):
    query = urlencode({"utm_source": idea["platform"], "utm_medium": "social", "utm_campaign": idea["id"]})
    return f"{APP_URL}/?{query}"


def main():
    ref = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
    year, week, _ = ref.isocalendar()

    ideas = json.loads(IDEAS.read_text(encoding="utf-8"))
    if len(ideas) < PER_WEEK:
        sys.exit(f"Il faut au moins {PER_WEEK} idées dans social/ideas.json")

    start = (week * PER_WEEK) % len(ideas)
    chosen = [ideas[(start + i) % len(ideas)] for i in range(PER_WEEK)]

    lines = [
        f"# Lot de publications {year}-W{week:02d}",
        "",
        "Publier à la main. Cocher chaque case après publication.",
        "",
    ]
    for n, idea in enumerate(chosen, start=1):
        lines.append(f"- [ ] {n}. {idea['hook']} ({idea['lang']}, {PLATFORM_LABEL[idea['platform']]})")
    lines.append("")

    for n, idea in enumerate(chosen, start=1):
        lines += [
            f"## {n}. {idea['hook']}",
            "",
            f"- Id : `{idea['id']}`",
            f"- Langue : {idea['lang']}",
            f"- Plateforme : {PLATFORM_LABEL[idea['platform']]}",
            "- Script :",
        ]
        lines += [f"  - {line}" for line in idea["script"].splitlines()]
        lines += [
            f"- Légende : {idea['caption']}",
            f"- Hashtags : {' '.join('#' + tag for tag in idea['hashtags'])}",
            f"- Lien (bio ou description) : {utm_link(idea)}",
            "",
        ]

    PACKS.mkdir(parents=True, exist_ok=True)
    target = PACKS / f"{year}-W{week:02d}.md"
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK : {target.relative_to(ROOT)} ({PER_WEEK} publications)")


if __name__ == "__main__":
    main()

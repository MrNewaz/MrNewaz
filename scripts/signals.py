"""
Collects Saif's public GitHub numbers for the Signals card and saves them to
scripts/signals.json, which generate.py renders in the LoreCraftian style.

Uses GITHUB_TOKEN when present (the GitHub Action provides one) and the
public API otherwise. If GitHub can't be reached, the last saved
signals.json is kept, so the README always builds.

    python scripts/signals.py
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

USER = "MrNewaz"
OUT = Path(__file__).resolve().parent / "signals.json"


def _get(url: str, accept: str = "application/vnd.github+json") -> bytes:
    headers = {"User-Agent": "signals-card", "Accept": accept}
    token = os.environ.get("GITHUB_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=40).read()


def repos() -> list[dict]:
    out, page = [], 1
    while True:
        batch = json.loads(_get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&page={page}"))
        out += batch
        if len(batch) < 100:
            return out
        page += 1


def contributions(since_year: int) -> dict[str, int]:
    """Daily contribution counts from the public contributions calendar."""
    days: dict[str, int] = {}
    for year in range(since_year, date.today().year + 1):
        html = _get(
            f"https://github.com/users/{USER}/contributions?from={year}-01-01&to={year}-12-31", accept="text/html"
        ).decode()
        ids = dict(re.findall(r'data-date="(\d{4}-\d\d-\d\d)"[^>]*?id="([^"]+)"', html))
        ids.update({d: i for i, d in re.findall(r'id="([^"]+)"[^>]*?data-date="(\d{4}-\d\d-\d\d)"', html)})
        tips = dict(re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>\s*([^<]+)', html))
        for d, i in ids.items():
            text = tips.get(i, "")
            m = re.match(r"([\d,]+) contribution", text)
            days[d] = int(m.group(1).replace(",", "")) if m else 0
    today = date.today().isoformat()
    return {d: c for d, c in sorted(days.items()) if d <= today}


def streaks(days: dict[str, int]) -> dict:
    dates = sorted(days)
    longest = cur = 0
    best = (None, None)
    start = None
    for d in dates:
        if days[d] > 0:
            cur += 1
            start = start or d
            if cur > longest:
                longest, best = cur, (start, d)
        else:
            cur, start = 0, None
    # current streak counts back from today (or yesterday, if today is still empty)
    current, cs = 0, None
    day = date.today()
    if days.get(day.isoformat(), 0) == 0:
        day -= timedelta(days=1)
    while days.get(day.isoformat(), 0) > 0:
        current += 1
        cs = day.isoformat()
        day -= timedelta(days=1)
    return {"current": current, "current_since": cs, "longest": longest, "longest_from": best[0], "longest_to": best[1]}


def main():
    try:
        user = json.loads(_get(f"https://api.github.com/users/{USER}"))
        rs = [r for r in repos() if not r["fork"]]
        langs = Counter()
        for r in rs:
            if r["language"]:
                langs[r["language"]] += max(r["size"], 1)
        total = sum(langs.values()) or 1
        top = [{"name": n, "pct": round(v * 100 / total, 1)} for n, v in langs.most_common(6)]
        other = round(100 - sum(t["pct"] for t in top), 1)
        if other > 0.5:
            top.append({"name": "Other", "pct": other})

        since = datetime.fromisoformat(user["created_at"].replace("Z", "+00:00")).year
        days = contributions(since)
        last_year = {d: c for d, c in days.items() if d > (date.today() - timedelta(days=365)).isoformat()}

        data = {
            "updated": date.today().isoformat(),
            "stars": sum(r["stargazers_count"] for r in rs),
            "repos": user["public_repos"],
            "followers": user["followers"],
            "contributions_total": sum(days.values()),
            "contributions_year": sum(last_year.values()),
            "since": since,
            **streaks(days),
            "languages": top,
            "calendar": [last_year[d] for d in sorted(last_year)][-364:],
        }
        OUT.write_text(json.dumps(data, indent=1), encoding="utf-8")
        print(f"signals: {data['contributions_total']} contributions, streak {data['current']}/{data['longest']}, {data['stars']} stars")
    except Exception as e:  # keep the last good data
        print(f"signals: GitHub unreachable ({e}); keeping {OUT.name}")


if __name__ == "__main__":
    main()

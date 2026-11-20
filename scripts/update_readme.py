#!/usr/bin/env python3
"""Render the profile README for today's season, plus the four season pages.

Run from the repository root:

    python3 scripts/update_readme.py                     # today (UTC)
    python3 scripts/update_readme.py --date 2027-01-15   # preview another day

Writes:

    README.md          the live profile: current season, countdown, fact of the day
    seasons/<s>.md     one static page per season (winter, spring, summer, autumn)

Seasons are meteorological: spring is March to May, summer June to August,
autumn September to November, winter December to February (Northern
Hemisphere; set HEMISPHERE = "south" to flip them).  Standard library only.
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "profile.md"
PROFILE_URL = "https://github.com/TheK4rim"
HEMISPHERE = "north"

ORDER = ("winter", "spring", "summer", "autumn")       # each season is followed by the next

SEASONS = {
    "winter": dict(title="Winter", emoji="❄️", square="🟦", months="December to February",
                   mood="❄️ Winter mode: long nights, hot tea and whitepapers."),
    "spring": dict(title="Spring", emoji="🌸", square="🟩", months="March to May",
                   mood="🌸 Spring mode: fresh ideas, fresh code, fresh charts."),
    "summer": dict(title="Summer", emoji="☀️", square="🟨", months="June to August",
                   mood="☀️ Summer mode: hot markets, cool algorithms."),
    "autumn": dict(title="Autumn", emoji="🍂", square="🟧", months="September to November",
                   mood="🍂 Autumn mode: harvesting ideas and rebalancing."),
}

# One fact per day, cycling.  Topics alternate so consecutive days differ.
FACTS = (
    ("🪙", "Bitcoin’s whitepaper was published on 31 October 2008, and its genesis block was mined "
           "on 3 January 2009."),
    ("📈", "The New York Stock Exchange traces its origins to the Buttonwood Agreement, signed in 1792."),
    ("🔐", "Keccak won NIST’s SHA-3 competition in 2012, after five years of public analysis of "
           "64 submissions."),
    ("🤖", "Alan Turing proposed the “imitation game”, now known as the Turing test, in 1950."),
    ("🪙", "Bitcoin’s supply is capped at 21 million coins, and each coin divides into 100 million "
           "satoshis."),
    ("📈", "The rule of 72: divide 72 by the yearly return in percent to estimate how many years it "
           "takes money to double."),
    ("🔐", "RSA, one of the first practical public-key cryptosystems, was published in 1977 by Rivest, "
           "Shamir and Adleman."),
    ("🤖", "The term “artificial intelligence” comes from the 1955 proposal for the 1956 Dartmouth "
           "summer workshop."),
    ("🪙", "Ethereum switched from proof-of-work to proof-of-stake in September 2022, an upgrade known "
           "as “The Merge”."),
    ("📈", "The Dow Jones Industrial Average was first published in 1896 and started with 12 companies."),
    ("🔐", "Diffie and Hellman introduced public-key key exchange in their 1976 paper “New Directions "
           "in Cryptography”."),
    ("🤖", "The transformer architecture behind today’s language models was introduced in the 2017 "
           "paper “Attention Is All You Need”."),
    ("🪙", "Bitcoin miners hash block headers with SHA-256, applied twice, until the result falls "
           "below a target."),
    ("📈", "The S&P 500 index in its 500-company form was introduced in 1957."),
    ("🔐", "AES is the Rijndael cipher by Joan Daemen and Vincent Rijmen, standardised by NIST in 2001."),
    ("🤖", "IBM’s Deep Blue beat world chess champion Garry Kasparov in a six-game match in 1997."),
    ("📈", "The Amsterdam exchange, founded in the early 1600s to trade shares of the Dutch East India "
           "Company, is often called the first modern stock exchange."),
    ("🔐", "A 256-bit elliptic-curve key offers about the same security as a 3072-bit RSA key."),
    ("🤖", "DeepMind’s AlphaGo beat Go champion Lee Sedol 4–1 in 2016."),
    ("🔐", "Claude Shannon proved in 1949 that the one-time pad achieves perfect secrecy."),
    ("🔐", "Keccak, the permutation behind SHA-3, has a 1600-bit state made of 25 lanes of 64 bits."),
)


def season_of(day: dt.date) -> str:
    north = ORDER[(day.month % 12) // 3]                 # Dec-Feb -> 0, Mar-May -> 1, ...
    if HEMISPHERE == "south":
        return ORDER[(ORDER.index(north) + 2) % 4]
    return north


def season_bounds(day: dt.date):
    """First day of the current season and first day of the next one."""
    if day.month == 12:
        return dt.date(day.year, 12, 1), dt.date(day.year + 1, 3, 1)
    if day.month < 3:
        return dt.date(day.year - 1, 12, 1), dt.date(day.year, 3, 1)
    first = 3 * (day.month // 3)                          # 3, 6 or 9
    return dt.date(day.year, first, 1), dt.date(day.year, first + 3, 1)


def progress_bar(fraction: float, square: str, cells: int = 10) -> str:
    """Emoji progress bar; emoji squares render the same on every platform."""
    filled = max(0, min(cells, round(fraction * cells)))
    return square * filled + "⬜" * (cells - filled)


def live_status(season: str, day: dt.date) -> str:
    start, end = season_bounds(day)
    fraction = (day - start).days / (end - start).days
    days_left = (end - day).days
    upcoming = SEASONS[ORDER[(ORDER.index(season) + 1) % 4]]
    info = SEASONS[season]
    unit = "day" if days_left == 1 else "days"
    return (f'<b>{info["emoji"]} {info["title"]} edition</b> &nbsp;·&nbsp; '
            f'{progress_bar(fraction, info["square"])} {round(fraction * 100)}% &nbsp;·&nbsp; '
            f'{days_left} {unit} until {upcoming["emoji"]} {upcoming["title"]}')


def static_status(season: str) -> str:
    info = SEASONS[season]
    return (f'<b>{info["emoji"]} {info["title"]} edition</b> &nbsp;·&nbsp; {info["months"]} '
            f'&nbsp;·&nbsp; <a href="{PROFILE_URL}">see the live profile</a>')


def fact_section(day: dt.date) -> str:
    emoji, fact = FACTS[day.toordinal() % len(FACTS)]
    return f"\n## 💡 Fact of the day\n\n{emoji} {fact}\n"


def season_nav(current: str, root: str) -> str:
    links = []
    for season in ORDER:
        info = SEASONS[season]
        label = f'{info["emoji"]} {info["title"]}'
        if season == current:
            links.append(f"<b>{label}</b>")
        else:
            links.append(f'<a href="{root}seasons/{season}.md">{label}</a>')
    return " &nbsp;·&nbsp; ".join(links)


def render(season: str, day: dt.date, live: bool) -> str:
    root = "" if live else "../"
    info = SEASONS[season]
    if live:
        footer = ("Updated every day by a GitHub Action. The season switches on 1 March, 1 June, "
                  "1 September and 1 December (UTC).")
    else:
        footer = "This is the static page for one season; the live profile shows the current one."
    values = {
        "root": root,
        "season": season,
        "title": info["title"],
        "emoji": info["emoji"],
        "mood": info["mood"],
        "status": live_status(season, day) if live else static_status(season),
        "fact_section": fact_section(day) if live else "",
        "season_nav": season_nav(season, root),
        "footer": footer,
    }
    text = TEMPLATE.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    if "{{" in text:
        missing = text[text.index("{{"):text.index("{{") + 40]
        raise SystemExit(f"unreplaced placeholder in {TEMPLATE.name}: {missing!r}")
    return text


def write(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--date", type=dt.date.fromisoformat,
                        default=dt.datetime.now(dt.timezone.utc).date(),
                        help="render for this day (YYYY-MM-DD) instead of today (UTC)")
    day = parser.parse_args().date
    current = season_of(day)
    outputs = {ROOT / "README.md": render(current, day, live=True)}
    for season in ORDER:
        outputs[ROOT / "seasons" / f"{season}.md"] = render(season, day, live=False)
    changed = [path.relative_to(ROOT).as_posix() for path, content in outputs.items()
               if write(path, content)]
    print(f"{day}: {current}; updated: {', '.join(changed) if changed else 'nothing'}")


if __name__ == "__main__":
    main()

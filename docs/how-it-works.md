# How this profile works

The profile README changes with the seasons. Each season has its own animated
banner, icons and divider, and the README shows the one for today.

| Season | Months (UTC) | Banner |
|---|---|---|
| ❄️ Winter | December to February | Night sky, aurora, mountains, falling snow |
| 🌸 Spring | March to May | Cherry branch, drifting petals, meadow |
| ☀️ Summer | June to August | Sun, sea, waves, gliding birds |
| 🍂 Autumn | September to November | Sunset, hills, falling leaves |

## What updates automatically

The workflow `.github/workflows/seasons.yml` runs every day at 00:07 UTC. It
also runs when you change the scripts or the template, and on demand from the
**Actions** tab ("Run workflow"). Each run does two things:

1. `scripts/make_assets.py` regenerates the SVG artwork in `assets/<season>/`.
   The output is deterministic, so nothing changes unless the script did.
2. `scripts/update_readme.py` writes `README.md` for today's season, with a
   progress bar, a countdown to the next season and a fact of the day. It also
   writes the four static pages in `seasons/`.

If anything changed, the workflow commits it as `github-actions[bot]`. The
daily commit also keeps the repository active, so GitHub never pauses the
schedule. GitHub pauses scheduled workflows after 60 days without activity.

## Where to edit

| To change | Edit |
|---|---|
| The text (about me, interests, featured project) | `templates/profile.md` |
| Season moods, facts, season dates, hemisphere | `scripts/update_readme.py` |
| Banners, icons, dividers, colours, the typing line | `scripts/make_assets.py` |

Never edit `README.md` or `seasons/*.md` by hand, because the next run
overwrites them.

## Preview locally

Both scripts use only the Python standard library:

```bash
python3 scripts/make_assets.py
python3 scripts/update_readme.py --date 2027-01-15
```

The `--date` option renders the README for any day, for example to check the
winter version in November. Run the script again without `--date` before you
commit.

## Notes

* The SVGs contain no scripts and load nothing external. GitHub shows README
  images through `<img>`, which allows CSS and SMIL animation but nothing else.
* Visitors whose system asks for reduced motion get still images. The typing
  line is then replaced by a static sentence.
* The seasons follow the Northern Hemisphere. To flip them, set
  `HEMISPHERE = "south"` in `scripts/update_readme.py`.

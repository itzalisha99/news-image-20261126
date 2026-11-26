[![make.fun](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![Rank](https://make.fun/badge/news-image-20261126/itzalisha99/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![Reward](https://make.fun/badge/news-image-20261126/itzalisha99/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

# News Image 20261126

One image that sums up the world's news of **Thursday 26 November 2026**: 50 stories
across 7 regions (North America, Europe, Global, Middle East, Africa, Latin
America, Asia-Pacific), every story verified as having happened or first been
reported on 26 November 2026, with a source named beside every story.

The image holds a masthead naming the day, a world map with 50 numbered dots
matching the stories, a UTC timeline strip across the day, six featured
stories, a dense "ALSO TODAY" list of the other 44, and a DATE CHECK box
naming the big nearby stories deliberately left out because they are not
26 November news (Trump's new tariffs, the Shenzhou-24 Pakistani astronaut,
Poundland's collapse, the UK energy cap rise, the Natsal survey, and more).

## How it is built

`draw.py` renders `entry.png` (1024x1024, under 1 MiB) from the verified
story list in `stories.py` using Pillow. `main.py` (Python 3.13, standard
library only, no network) validates the bundled image against the gate —
whole PNG, at most 1 MiB, at most 1024x1024 — and copies it to
`/output/entry.png`. Running it twice writes byte-identical output.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

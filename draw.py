#!/usr/bin/env python3
"""Draw the 26 November 2026 world-news image (1024x1024 PNG, < 1 MiB).

Reads the verified story list from stories.py and renders:
masthead, world map with numbered dots, UTC timeline, 6 featured stories,
a dense ALSO TODAY list of the other 44, and a DATE CHECK box.
"""
import textwrap

from PIL import Image, ImageDraw, ImageFont

from stories import DATE_CHECK, FEATURED, REGION_COLOR, REGION_NAME, REGIONS, STORIES, TIMELINE

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (25, 25, 25)
MUTED = (90, 84, 72)
RED = (178, 58, 46)
NAVY = (31, 58, 95)
LAND = (216, 222, 230)
LAND_EDGE = (140, 150, 165)
PANEL = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


F_SERIF = lambda s: font("DejaVuSerif-Bold.ttf", s)  # noqa: E731
F_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)  # noqa: E731
F_REG = lambda s: font("DejaVuSans.ttf", s)  # noqa: E731

# Rough equirectangular continent outlines (lon, lat).
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60), (-55, 47),
     (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16), (-105, 20), (-115, 28),
     (-125, 40), (-125, 49), (-145, 60), (-165, 60)],
    # Greenland
    [(-58, 64), (-40, 70), (-30, 76), (-20, 70), (-35, 60)],
    # South America
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-40, -10), (-35, -20), (-48, -28),
     (-58, -35), (-65, -45), (-70, -54), (-73, -40), (-75, -20), (-80, -5)],
    # Europe
    [(-10, 36), (-5, 44), (0, 50), (5, 58), (10, 58), (18, 56), (21, 55), (28, 60),
     (30, 70), (40, 68), (45, 60), (40, 50), (30, 45), (28, 40), (23, 36), (15, 38),
     (8, 44), (3, 43), (-2, 37), (-9, 38)],
    # Africa
    [(-6, 35), (10, 37), (20, 32), (30, 31), (35, 28), (43, 12), (51, 11), (48, 0),
     (40, -10), (35, -18), (28, -28), (20, -35), (15, -28), (12, -18), (9, -5),
     (9, 4), (-8, 5), (-15, 10), (-17, 15)],
    # Asia
    [(30, 70), (45, 68), (60, 70), (75, 73), (90, 75), (110, 76), (130, 72),
     (150, 70), (170, 67), (178, 65), (170, 60), (160, 55), (150, 45), (140, 40),
     (130, 35), (127, 33), (120, 28), (110, 20), (105, 10), (100, 8), (95, 15),
     (90, 22), (80, 25), (75, 20), (70, 25), (60, 25), (55, 26), (50, 29),
     (45, 30), (40, 36), (35, 36), (30, 42), (28, 45), (30, 50), (35, 55), (30, 60)],
    # SE Asia islands (rough blobs)
    [(95, 5), (100, 0), (105, -5), (110, -8), (115, -8), (120, -10), (118, -5),
     (112, 0), (105, 5), (100, 8)],
    [(122, 18), (122, 12), (124, 8), (126, 6), (122, 10)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (142, 42), (144, 44),
     (141, 45), (140, 40), (137, 37), (133, 35), (130, 33)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (130, -32), (135, -35),
     (140, -38), (145, -38), (150, -37), (153, -32), (150, -25), (146, -20),
     (142, -15), (137, -12), (132, -11), (127, -14), (122, -17), (118, -20)],
    # UK
    [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (0, 57), (1, 53), (1, 51), (-3, 50)],
    # New Zealand
    [(167, -45), (170, -42), (174, -39), (177, -38), (175, -41), (171, -44)],
]

MAP_X0, MAP_Y0, MAP_X1, MAP_Y1 = 8, 96, 1016, 296


def map_xy(lon, lat):
    x = MAP_X0 + (lon + 180.0) / 360.0 * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (85.0 - lat) / 145.0 * (MAP_Y1 - MAP_Y0)
    return x, y


def fit_text(draw, text, fnt, max_w, suffix="..."):
    """Shorten text with an ellipsis until it fits max_w."""
    if draw.textlength(text, font=fnt) <= max_w:
        return text
    while text and draw.textlength(text + suffix, font=fnt) > max_w:
        text = text[:-1]
    return text + suffix


def wrap_text(draw, text, fnt, max_w, max_lines=2):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
            if len(lines) == max_lines:
                break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and words:
        # mark truncation if text remains
        joined = " ".join(lines)
        if len(joined) < len(text):
            lines[-1] = fit_text(draw, lines[-1], fnt, max_w)
    return lines


def draw_map(draw):
    draw.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=(233, 238, 244),
                   outline=LAND_EDGE, width=1)
    for poly in CONTINENTS:
        pts = [map_xy(lon, lat) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=LAND_EDGE)
    # graticule
    for lon in range(-150, 181, 30):
        x, _ = map_xy(lon, 0)
        draw.line([(x, MAP_Y0), (x, MAP_Y1)], fill=(225, 230, 238), width=1)
    for lat in (-30, 0, 30, 60):
        _, y = map_xy(0, lat)
        draw.line([(MAP_X0, y), (MAP_X1, y)], fill=(225, 230, 238), width=1)
    # region legend
    lx, ly = MAP_X0 + 8, MAP_Y1 - 20
    for key, name, color in REGIONS:
        draw.ellipse([lx, ly, lx + 10, ly + 10], fill=color)
        draw.text((lx + 13, ly - 1), name, font=F_REG(10), fill=INK)
        lx += 13 + draw.textlength(name, font=F_REG(10)) + 14
    # numbered dots
    for num, region, _headline, _src, lon, lat, dx, dy in STORIES:
        x, y = map_xy(lon, lat)
        x += dx
        y += dy
        r = 8
        draw.ellipse([x - r, y - r, x + r, y + r], fill=REGION_COLOR[region],
                     outline=(255, 255, 255), width=1)
        label = str(num)
        fnt = F_BOLD(8 if num < 10 else 7)
        tw = draw.textlength(label, font=fnt)
        draw.text((x - tw / 2, y - 5), label, font=fnt, fill=(255, 255, 255))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    d.rectangle([0, 0, W, 92], fill=NAVY)
    d.text((16, 10), "THE WORLD IN ONE DAY", font=F_SERIF(40), fill=(255, 255, 255))
    d.text((16, 58), "THURSDAY 26 NOVEMBER 2026  ·  50 STORIES  ·  7 REGIONS",
           font=F_BOLD(20), fill=(255, 214, 90))
    d.text((W - 16, 14), "ALL STORIES DATED", font=F_BOLD(13), fill=(255, 255, 255), anchor="ra")
    d.text((W - 16, 32), "26 NOV 2026", font=F_BOLD(16), fill=(255, 214, 90), anchor="ra")
    d.text((W - 16, 56), "Sources named with every story", font=F_REG(12),
           fill=(200, 210, 225), anchor="ra")
    d.line([(0, 92), (W, 92)], fill=RED, width=4)

    # ---- Map ----
    draw_map(d)
    d.text((MAP_X0, MAP_Y0 - 0), "", font=F_REG(10), fill=INK)

    # ---- UTC timeline ----
    ty0, ty1 = 300, 348
    d.rectangle([8, ty0, 1016, ty1], fill=PANEL, outline=LAND_EDGE, width=1)
    d.text((16, ty0 + 4), "26 NOVEMBER IN UTC", font=F_BOLD(11), fill=NAVY)
    x0, x1 = 190, 1000
    ymid = ty0 + 24
    d.line([(x0, ymid), (x1, ymid)], fill=NAVY, width=2)
    for hour in range(0, 25, 4):
        x = x0 + hour / 24.0 * (x1 - x0)
        d.line([(x, ymid - 4), (x, ymid + 4)], fill=NAVY, width=1)
    for hour, label, above in TIMELINE:
        x = x0 + hour / 24.0 * (x1 - x0)
        d.ellipse([x - 5, ymid - 5, x + 5, ymid + 5], fill=RED, outline=(255, 255, 255), width=1)
        ly = ymid - 19 if above else ymid + 9
        anchor = "ma"
        lx = x
        tw = d.textlength(label, font=F_BOLD(9))
        if lx - tw / 2 < 190:
            lx, anchor = 190, "la"
        if lx + tw / 2 > 1010:
            lx, anchor = 1010, "ra"
        d.text((lx, ly), label, font=F_BOLD(9), fill=INK, anchor=anchor)

    # ---- Featured stories ----
    fy = 356
    d.text((16, fy), "THE DAY'S BIG STORIES", font=F_BOLD(15), fill=RED)
    d.line([(16, fy + 22), (1008, fy + 22)], fill=RED, width=2)
    featured_nums = [21, 25, 1, 38, 9, 42]
    by_num = {s[0]: s for s in STORIES}
    col_w, row_h = 496, 66
    for i, num in enumerate(featured_nums):
        col, row = i % 2, i // 2
        x = 16 + col * (col_w + 16)
        y = fy + 28 + row * row_h
        _n, region, headline, src, _lo, _la, _dx, _dy = by_num[num]
        d.ellipse([x, y + 2, x + 26, y + 28], fill=REGION_COLOR[region])
        lbl = str(num)
        fnt = F_BOLD(13)
        tw = d.textlength(lbl, font=fnt)
        d.text((x + 13 - tw / 2, y + 7), lbl, font=fnt, fill=(255, 255, 255))
        lines = wrap_text(d, headline, F_BOLD(15), col_w - 36, max_lines=1)
        d.text((x + 34, y), lines[0], font=F_BOLD(15), fill=INK)
        detail = FEATURED[num] + "  (" + src + ")"
        dlines = wrap_text(d, detail, F_REG(12), col_w - 36, max_lines=2)
        for j, line in enumerate(dlines):
            d.text((x + 34, y + 20 + j * 15), line, font=F_REG(12), fill=MUTED)

    # ---- Also today ----
    ay = 584
    d.text((16, ay), "ALSO TODAY", font=F_BOLD(15), fill=RED)
    d.text((1010, ay), "number = dot on the map", font=F_REG(11), fill=MUTED, anchor="ra")
    d.line([(16, ay + 22), (1008, ay + 22)], fill=RED, width=2)
    rest = [s for s in STORIES if s[0] not in featured_nums]
    col_w2 = 492
    row_h2 = 14.6
    for i, (num, region, headline, src, _lo, _la, _dx, _dy) in enumerate(rest):
        col, row = i % 2, i // 2
        x = 16 + col * (col_w2 + 16)
        y = ay + 28 + row * row_h2
        d.ellipse([x, y + 1, x + 11, y + 12], fill=REGION_COLOR[region])
        lbl = str(num)
        fnt = F_BOLD(7)
        tw = d.textlength(lbl, font=fnt)
        d.text((x + 5.5 - tw / 2, y + 2), lbl, font=fnt, fill=(255, 255, 255))
        line = "%s  (%s)" % (headline, src)
        line = fit_text(d, line, F_REG(12), col_w2 - 16)
        d.text((x + 16, y), line, font=F_REG(12), fill=INK)

    # ---- Date check ----
    by = 938
    d.rectangle([8, by, 1016, 998], fill=(255, 244, 224), outline=(200, 140, 40), width=1)
    d.text((16, by + 5), "DATE CHECK", font=F_BOLD(12), fill=(150, 80, 0))
    wrapped = textwrap.wrap(DATE_CHECK, width=160)
    for j, line in enumerate(wrapped[:4]):
        d.text((16, by + 21 + j * 12), line, font=F_REG(11), fill=(80, 55, 20))

    # ---- Footer ----
    d.text((16, 1002),
           "Every story happened or was first reported on 26 November 2026.  Sources: BBC · Reuters · AP · Guardian · Al Jazeera · Focus Taiwan · The West · MEA · RBI",
           font=F_REG(10), fill=MUTED)
    d.text((16, 1014), "Drawn for make.fun — news-image-20261126",
           font=F_REG(10), fill=MUTED)

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()

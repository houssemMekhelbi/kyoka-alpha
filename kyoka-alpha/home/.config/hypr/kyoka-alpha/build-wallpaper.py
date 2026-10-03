#!/usr/bin/env python3
"""Generate the Kyoka alpha wallpaper: a void plane broken into five shards and
put back slightly wrong. The violet field is the same in every shard but
shifted a few pixels, so it misaligns across each crack; cracks are Pale
Violet hairlines with a void seam beside them. Two faint hairlines at 115°
and -30° cross the whole plane, across the whole wallpaper.

Writes wallpaper.svg next to this file and renders wallpaper.png with
rsvg-convert. Edit the constants and re-run.
"""

import math
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
W, H = 1920, 1080
VOID, DEEP, VIOLET, PALE = "#07060B", "#0F0B18", "#7B4FD6", "#A98BFF"

# Shards (polygons covering the screen) with the offset of their violet field
# and the strength of their deep-violet tint.
SHARDS = [
    ([(0, 0), (1150, 0), (980, 540), (0, 690)], (0, 0), 0.00),
    ([(1150, 0), (1920, 0), (1920, 380), (980, 540)], (9, -4), 0.18),
    ([(0, 690), (980, 540), (840, 1080), (0, 1080)], (-6, 5), 0.10),
    ([(980, 540), (1400, 468.5), (1560, 1080), (840, 1080)], (4, 8), 0.24),
    ([(1400, 468.5), (1920, 380), (1920, 1080), (1560, 1080)], (-10, -3), 0.06),
]
CRACKS = [
    [(1150, 0), (980, 540), (840, 1080)],
    [(0, 690), (980, 540), (1400, 468.5), (1920, 380)],
    [(1400, 468.5), (1560, 1080)],
]


def pts(ps):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in ps)


def hairline(angle_deg, through):
    """A line through `through` at `angle_deg`, long enough to cross the screen."""
    a = math.radians(angle_deg)
    dx, dy = math.cos(a) * 2400, -math.sin(a) * 2400
    x, y = through
    return f'<line x1="{x - dx:.1f}" y1="{y - dy:.1f}" x2="{x + dx:.1f}" y2="{y + dy:.1f}"/>'


defs, body = [], []
for i, (poly, (dx, dy), tint) in enumerate(SHARDS):
    defs.append(f'<clipPath id="s{i}"><polygon points="{pts(poly)}"/></clipPath>')
    body.append(
        f'<g clip-path="url(#s{i})">'
        f'<rect width="{W}" height="{H}" fill="{DEEP}" fill-opacity="{tint:.2f}"/>'
        f'<g transform="translate({dx} {dy})">'
        f'<rect x="-40" y="-40" width="{W + 80}" height="{H + 80}" fill="url(#field)"/>'
        f'<rect x="-40" y="-40" width="{W + 80}" height="{H + 80}" fill="url(#low)"/></g></g>')

seams = "".join(f'<polyline points="{pts([(x + 1.5, y + 1.5) for x, y in c])}"/>' for c in CRACKS)
cracks = "".join(f'<polyline points="{pts(c)}"/>' for c in CRACKS)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
 <radialGradient id="field" gradientUnits="userSpaceOnUse" cx="1260" cy="430" r="820" gradientTransform="translate(1260 430) scale(1.25 1) translate(-1260 -430)"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0.34"/><stop offset="0.5" stop-color="{VIOLET}" stop-opacity="0.12"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></radialGradient>
 <radialGradient id="low" gradientUnits="userSpaceOnUse" cx="260" cy="1000" r="620"><stop offset="0" stop-color="{PALE}" stop-opacity="0.10"/><stop offset="1" stop-color="{PALE}" stop-opacity="0"/></radialGradient>
 {"".join(defs)}
</defs>
<rect width="{W}" height="{H}" fill="{VOID}"/>
{"".join(body)}
<g fill="none" stroke="{PALE}" stroke-opacity="0.05" stroke-width="1">{hairline(115, (W * 0.48, H * 0.5))}{hairline(-30, (W * 0.62, H * 0.5))}</g>
<g fill="none" stroke="{VOID}" stroke-opacity="0.9" stroke-width="1.5" stroke-linejoin="miter">{seams}</g>
<g fill="none" stroke="{PALE}" stroke-opacity="0.2" stroke-width="1" stroke-linejoin="miter">{cracks}</g>
</svg>
'''

(HERE / "wallpaper.svg").write_text(svg)
subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), "-o", str(HERE / "wallpaper.png"),
                str(HERE / "wallpaper.svg")], check=True)
print("wrote", HERE / "wallpaper.svg", "and wallpaper.png")

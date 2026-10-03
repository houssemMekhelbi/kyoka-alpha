#!/usr/bin/env python3
"""Generate the KyokaShard cursor theme (Kyoka alpha) next to this file.

The pointer is the theme's shard: a void blade with a Pale Violet edge and a
Violet crack from the tip; links get the active shard (filled Pale Violet,
void crack); busy is the theme's radial glyph, a 270° arc broken at the
top-left, turning. Every shape has a thin void outline so it reads on light
pages too.

Writes two formats from the same SVGs:
  hyprcursors/ + manifest.hl*   hyprcursor (Hyprland draws it; SVG, any size)
  cursors/                      XCursor 24/32/48 (GTK3, XWayland, anything else)
Shapes not drawn here fall back to Adwaita (index.theme Inherits).
Needs rsvg-convert and hyprcursor-util. Run: python3 build.py
"""

import os
import shutil
import struct
import subprocess
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAME = "KyokaShard"
VOID, VIOLET, PALE, BLOOD = "#07060B", "#7B4FD6", "#A98BFF", "#E06A88"
XSIZES = (24, 32, 48)


def svg(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">'
            f'{body}</svg>\n')


def line(d, color=PALE, w=1.6):
    """A hairline stroke with a void outline under it."""
    return (f'<path d="{d}" fill="none" stroke="{VOID}" stroke-width="{w + 2}" stroke-linecap="square" stroke-linejoin="miter"/>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="square" stroke-linejoin="miter"/>')


BLADE = "M4 3 L4 26 L10.5 20 L22 19 Z"
CRACK = "M4.6 4.5 L11.5 17"


def blade(active=False):
    fill = PALE if active else VOID
    crack = VOID if active else VIOLET
    return (f'<path d="{BLADE}" fill="{fill}" stroke="{VOID}" stroke-width="3" stroke-linejoin="miter"/>'
            f'<path d="{BLADE}" fill="{fill}" stroke="{PALE}" stroke-width="1.3" stroke-linejoin="miter"/>'
            f'<path d="{CRACK}" stroke="{crack}" stroke-width="1.2"/>')


def arc(cx, cy, r, turn, w=2.4):
    """270° arc with its gap at the top-left, rotated by `turn` degrees."""
    import math
    a0, a1 = math.radians(-90), math.radians(180)  # from top, clockwise to left: gap top-left
    x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
    x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
    d = f"M{x0:.2f} {y0:.2f} A{r} {r} 0 1 1 {x1:.2f} {y1:.2f}"
    return (f'<g transform="rotate({turn} {cx} {cy})">'
            f'<path d="{d}" fill="none" stroke="{VOID}" stroke-width="{w + 2}"/>'
            f'<path d="{d}" fill="none" stroke="{PALE}" stroke-width="{w}"/></g>')


def heads(points):
    return "".join(f'<path d="{p}" fill="{PALE}" stroke="{VOID}" stroke-width="1" stroke-linejoin="miter"/>' for p in points)


FRAMES = 8
# name: (frames as svg bodies, hotspot (x, y) in 32-unit space, frame delay ms, aliases)
SHAPES = {
    "left_ptr": ([svg(blade())], (4, 3), 0,
                 ["default", "arrow", "top_left_arrow", "left_arrow", "context-menu", "copy", "alias",
                  "dnd-copy", "dnd-link", "dnd-none", "dnd-ask", "help", "question_arrow", "whats_this"]),
    "hand2": ([svg(blade(active=True))], (4, 3), 0,
              ["pointer", "hand1", "hand", "pointing_hand", "e29285e634086352946a0e7090d73106"]),
    "xterm": ([svg(line("M11 5 H21 M16 5 V27 M11 27 H21", w=1.4))], (16, 16), 0, ["text", "ibeam"]),
    "vertical-text": ([svg(line("M5 11 V21 M5 16 H27 M27 11 V21", w=1.4))], (16, 16), 0, []),
    "watch": ([svg(arc(16, 16, 9, k * 360 / FRAMES)) for k in range(FRAMES)], (16, 16), 90, ["wait"]),
    "left_ptr_watch": ([svg(blade() + arc(22, 23, 5, k * 360 / FRAMES, w=2)) for k in range(FRAMES)], (4, 3), 90,
                       ["progress", "half-busy", "00000000000000020006000e7e9ffc3f",
                        "08e8e1c95fe2fc01f976f1e063a24ccd", "3ecb610c1bf2410f44200f48c40d3599"]),
    "crosshair": ([svg(line("M16 4 V12 M16 20 V28 M4 16 H12 M20 16 H28", w=1.4)
                       + f'<rect x="15" y="15" width="2" height="2" fill="{PALE}"/>')], (16, 16), 0,
                  ["cross", "tcross", "cell", "plus", "color-picker"]),
    "not-allowed": ([svg(line("M16 7 A9 9 0 1 1 15.99 7 M9.6 22.4 L22.4 9.6", color=BLOOD, w=1.8))], (16, 16), 0,
                    ["no-drop", "forbidden", "circle", "crossed_circle", "dnd-no-drop"]),
    "grab": ([svg(f'<path d="M7 22 H20 L25 10 H12 Z" fill="none" stroke="{VOID}" stroke-width="3.4"/>'
                  f'<path d="M7 22 H20 L25 10 H12 Z" fill="none" stroke="{PALE}" stroke-width="1.5"/>')], (16, 16), 0,
             ["openhand", "hand-grab"]),
    "grabbing": ([svg(f'<path d="M7 22 H20 L25 10 H12 Z" fill="{PALE}" stroke="{VOID}" stroke-width="1.5"/>'
                      f'<path d="M11 19 L19 13" stroke="{VOID}" stroke-width="1.2"/>')], (16, 16), 0,
                 ["closedhand", "dnd-move", "hand-grabbing"]),
    "fleur": ([svg(line("M16 6 V26 M6 16 H26", w=1.3)
                   + heads(["M16 2 L19.5 7 H12.5 Z", "M16 30 L19.5 25 H12.5 Z", "M2 16 L7 12.5 V19.5 Z", "M30 16 L25 12.5 V19.5 Z"]))],
              (16, 16), 0, ["move", "all-scroll", "size_all", "4498f0e0c1937ffe01fd06f973665830", "9081237383d90e509aa00f00170e968f"]),
    "sb_h_double_arrow": ([svg(line("M7 16 H25", w=1.3) + heads(["M3 16 L8 12 V20 Z", "M29 16 L24 12 V20 Z"]))], (16, 16), 0,
                          ["ew-resize", "col-resize", "e-resize", "w-resize", "h_double_arrow", "left_side",
                           "right_side", "size_hor", "split_h", "14fef782d02440884392942c11205230",
                           "028006030e0e7ebffc7f7070c0600140"]),
    "sb_v_double_arrow": ([svg(line("M16 7 V25", w=1.3) + heads(["M16 3 L12 8 H20 Z", "M16 29 L12 24 H20 Z"]))], (16, 16), 0,
                          ["ns-resize", "row-resize", "n-resize", "s-resize", "v_double_arrow", "top_side",
                           "bottom_side", "size_ver", "split_v", "2870a09082c103050810ffdffffe0204",
                           "00008160000006810000408080010102"]),
    "bd_double_arrow": ([svg(line("M9 9 L23 23", w=1.3) + heads(["M5 5 L11.5 6.5 L6.5 11.5 Z", "M27 27 L20.5 25.5 L25.5 20.5 Z"]))],
                        (16, 16), 0, ["nwse-resize", "nw-resize", "se-resize", "top_left_corner",
                                      "bottom_right_corner", "size_fdiag", "c7088f0f3e6c8088236ef8e1e3e70000"]),
    "fd_double_arrow": ([svg(line("M23 9 L9 23", w=1.3) + heads(["M27 5 L25.5 11.5 L20.5 6.5 Z", "M5 27 L6.5 20.5 L11.5 25.5 Z"]))],
                        (16, 16), 0, ["nesw-resize", "ne-resize", "sw-resize", "top_right_corner",
                                      "bottom_left_corner", "size_bdiag", "fcf1c3c7cd4491d801f1e1c78f100000"]),
}


# ---- PNG decode (8-bit RGBA from rsvg-convert) --------------------------------

def load_png(path):
    d = Path(path).read_bytes()
    pos, idat = 8, b""
    while pos < len(d):
        n, t = struct.unpack(">I4s", d[pos:pos + 8])
        body = d[pos + 8:pos + 8 + n]
        pos += 12 + n
        if t == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", body[:10])
            assert bd == 8 and ct == 6, "expected 8-bit RGBA"
        elif t == b"IDAT":
            idat += body
    raw, bpp, stride = zlib.decompress(idat), 4, w * 4
    rows, prev, i = [], bytearray(stride), 0
    for _ in range(h):
        f, line_ = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line_[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if f == 1:
                line_[x] = (line_[x] + a) & 255
            elif f == 2:
                line_[x] = (line_[x] + b) & 255
            elif f == 3:
                line_[x] = (line_[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line_[x] = (line_[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        rows.append(bytes(line_))
        prev = line_
    return w, h, rows


def argb_premultiplied(rows):
    out = bytearray()
    for r in rows:
        for x in range(0, len(r), 4):
            R, G, B, A = r[x:x + 4]
            out += struct.pack("<I", (A << 24) | ((R * A // 255) << 16) | ((G * A // 255) << 8) | (B * A // 255))
    return bytes(out)


def xcursor(images):
    """images: list of (nominal, w, h, xhot, yhot, delay, argb). Returns XCursor bytes."""
    ntoc = len(images)
    header = struct.pack("<4sIII", b"Xcur", 16, 0x10000, ntoc)
    pos = 16 + ntoc * 12
    toc, chunks = b"", b""
    for nominal, w, h, xh, yh, delay, px in images:
        toc += struct.pack("<III", 0xFFFD0002, nominal, pos)
        chunk = struct.pack("<IIIIIIIII", 36, 0xFFFD0002, nominal, 1, w, h, xh, yh, delay) + px
        chunks += chunk
        pos += len(chunk)
    return header + toc + chunks


def main():
    for d in ("hyprcursors", "cursors"):
        shutil.rmtree(ROOT / d, ignore_errors=True)
    for f in ROOT.glob("manifest.*"):
        f.unlink()
    (ROOT / "cursors").mkdir()

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "work"
        (work / "hyprcursors").mkdir(parents=True)
        (work / "manifest.hl").write_text(
            f"name = {NAME}\ndescription = Kyoka alpha: void shard with a Pale Violet edge\n"
            "version = 0.1\ncursors_directory = hyprcursors\n")
        for shape, (frames, (hx, hy), delay, aliases) in SHAPES.items():
            sd = work / "hyprcursors" / shape
            sd.mkdir()
            meta = [f"resize_algorithm = bilinear", f"hotspot_x = {hx / 32:.4f}", f"hotspot_y = {hy / 32:.4f}"]
            meta += [f"define_override = {a}" for a in aliases]
            images = []
            for k, body in enumerate(frames):
                fname = f"{shape}-{k}.svg"
                (sd / fname).write_text(body)
                meta.append(f"define_size = 0, {fname}" + (f", {delay}" if delay else ""))
                for size in XSIZES:
                    png = Path(tmp) / f"{shape}-{k}-{size}.png"
                    subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), "-o", str(png), str(sd / fname)], check=True)
                    w, h, rows = load_png(png)
                    images.append((size, w, h, round(hx * size / 32), round(hy * size / 32), delay or 0, argb_premultiplied(rows)))
            (sd / "meta.hl").write_text("\n".join(meta) + "\n")
            images.sort(key=lambda i: i[0])
            (ROOT / "cursors" / shape).write_bytes(xcursor(images))
            for a in aliases:
                link = ROOT / "cursors" / a
                if not link.exists():
                    os.symlink(shape, link)

        out = Path(tmp) / "out"
        out.mkdir()
        subprocess.run(["hyprcursor-util", "--create", str(work), "--output", str(out)], check=True,
                       stdout=subprocess.DEVNULL)
        built = next(out.iterdir())
        for item in built.iterdir():
            dest = ROOT / item.name
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

    (ROOT / "index.theme").write_text(
        f"[Icon Theme]\nName={NAME}\nComment=Kyoka alpha cursors: shard, hairline, broken arc\nInherits=Adwaita\n")
    print(f"{NAME} written to {ROOT}")


if __name__ == "__main__":
    main()

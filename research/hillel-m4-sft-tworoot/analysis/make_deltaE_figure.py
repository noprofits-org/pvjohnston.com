#!/usr/bin/env python3
"""M4 same-geometry two-root SF-TDA figures: ACS plot (Fig 1) + optional stills.

Reads results/bayes-metrics.json at runtime for the two geometry-family
series (S0-relaxed and T1-relaxed) and each family's 90–105 linear
interpolant. Does not invent points, does not mark 110°, and does not
label an interpolant as an MECP or an evaluated degeneracy. Stills
composite existing frames only (shared edge-on camera); identity tags,
no energies. Lab frames are optional: a clean checkout writes the OG
plot and exits 0.

Usage:
  python3 research/hillel-m4-sft-tworoot/analysis/make_deltaE_figure.py
"""
from __future__ import annotations

import json
import math
import shutil
import struct
import zlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO_ROOT = ROOT.parents[1]
METRICS_PATH = ROOT / "results" / "bayes-metrics.json"
FRAMES = ROOT / "frames"
OUT_PREVIEW = HERE / "fig_deltaE_vs_phi.png"
OUT_PUBLISHED = (
    REPO_ROOT
    / "images"
    / "2026-08-28-does-the-m4-sf-profile-gap-survive-same-geometry-two-root-og.png"
)
OUT_S0_PREVIEW = HERE / "fig_s0_stills.png"
OUT_T1_PREVIEW = HERE / "fig_t1_stills.png"
OUT_S0_PUBLISHED = (
    REPO_ROOT
    / "images"
    / "2026-08-28-does-the-m4-sf-profile-gap-survive-same-geometry-two-root-s0-stills.png"
)
OUT_T1_PUBLISHED = (
    REPO_ROOT
    / "images"
    / "2026-08-28-does-the-m4-sf-profile-gap-survive-same-geometry-two-root-t1-stills.png"
)
# Faces: committed Hanken Grotesk (Latin ticks/numbers) plus DejaVu Sans
# for codepoints Hanken does not encode (Δ, φ). Both load with Pillow
# ImageFont.truetype at the same pixel size. No host font path.
HANKEN_TTF = HERE / "hanken-grotesk.ttf"
DEJAVU_TTF = HERE / "dejavu-sans.ttf"

# Standing rule (Peter / Heisenberg): plot type matches page body size.
# Desktop in-article image width DISPLAY_W=632 CSS px; body BODY_PX=17 (Hanken).
# When a PNG is shown at 632 px wide, every plot string must be 17 CSS pixels:
#   font_px_on_canvas = round(BODY_PX * canvas_w / DISPLAY_W)
# Plot 1200×630 → 17*1200/632 = 32.278… → 32 px (ticks, axis labels, ΔE)
# Stills 1600×520 → 17*1600/632 = 43.038… → 43 px (S0/T1 row tags, φ still tags)
# Keep 1200×630 and 1600×520 if possible. Widen gutters/margins so the larger
# type does not collide or clip. Grow canvas ONLY if labels otherwise clip;
# if width grows, recompute font_px = round(17 * new_w / 632) so on-page size
# stays 17 px.
DISPLAY_W = 632
BODY_PX = 17

def canvas_font_px(canvas_w: int) -> int:
    return int(round(BODY_PX * canvas_w / DISPLAY_W))

# Fig 1 — plot only (PR 99 OG path). No title, no molecule strip.
PLOT_W, PLOT_H = 1200, 630
# Fig 2/3 — four large stills, page-width, separate from the graph.
STILL_W, STILL_H = 1600, 520
PLOT_FONT_PX = canvas_font_px(PLOT_W)    # 32
STILL_FONT_PX = canvas_font_px(STILL_W)  # 43

INK = np.array([38, 38, 38], dtype=np.float64)       # ~0.15 near-black
ZERO_C = np.array([22, 22, 22], dtype=np.float64)
SERIES_S0 = np.array([36, 74, 128], dtype=np.float64)   # S0-relaxed
SERIES_T1 = np.array([166, 84, 48], dtype=np.float64)   # T1-relaxed
WHITE = np.array([255, 255, 255], dtype=np.uint8)
FAMILY_ORDER = ("s0_relaxed", "t1_relaxed")
FAMILY_COLOR = {"s0_relaxed": SERIES_S0, "t1_relaxed": SERIES_T1}
FAMILY_LABEL = {"s0_relaxed": "S0-relaxed", "t1_relaxed": "T1-relaxed"}

# Shared-camera crop of the 900×820 frames (union of molecule + pad 20).
# Edge-on CNNC camera: molecule bbox union x[171:690] y[48:581].
# Drops the in-frame identity caption band (y 778–798; previously y≥770).
CROP = (151, 28, 710, 601)  # x0, y0, x1, y1


# ---------------------------------------------------------------------------
# metrics — only source of plotted numbers
# ---------------------------------------------------------------------------

def load_metrics(path: Path) -> dict:
    m = json.loads(path.read_text())
    series = {family: [] for family in FAMILY_ORDER}
    for p in m["points"]:
        fam = p.get("geom_family")
        if fam not in series:
            raise SystemExit(f"unexpected geom_family {fam!r}")
        if not p.get("both_assigned"):
            raise SystemExit(
                f"refusing to plot: {fam} φ={p.get('phi_deg')} not both_assigned"
            )
        series[fam].append((float(p["phi_deg"]), float(p["deltaE_kJmol"])))
    for fam, pts in series.items():
        pts.sort(key=lambda t: t[0])
        if [phi for phi, _ in pts] != [90, 105, 120, 135]:
            raise SystemExit(f"{fam} points are not the required window: {pts!r}")

    interpolants = {}
    for pair in m["neighboring_pairs"]:
        ic = pair.get("interpolated_crossing_phi_deg")
        fam = pair.get("geom_family")
        if pair.get("sign_change") and ic is not None:
            if tuple(pair["pair"]) != (90, 105):
                raise SystemExit(f"interpolant is not on 90–105: {pair['pair']}")
            interpolants[fam] = float(ic)
        elif ic is not None:
            raise SystemExit("non-null interpolant on a non-sign-change pair")

    if set(interpolants) != set(FAMILY_ORDER):
        raise SystemExit(f"expected interpolants for both families, got {interpolants!r}")
    if abs(float(m["crossing_phi_deg_s0"]) - interpolants["s0_relaxed"]) > 1e-9:
        raise SystemExit("crossing_phi_deg_s0 != S0-relaxed 90–105 interpolant")
    if abs(float(m["crossing_phi_deg_t1"]) - interpolants["t1_relaxed"]) > 1e-9:
        raise SystemExit("crossing_phi_deg_t1 != T1-relaxed 90–105 interpolant")

    return {
        "series": series,
        "interpolants": interpolants,
        "method": m["method"],
        "slug": m.get("slug", ""),
    }


def fmt_delta(v: float) -> str:
    s = f"{v:+.2f}"
    return s.replace("-", "\u2212")


def fmt_tick(v: float) -> str:
    if abs(v) < 1e-12:
        return "0"
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v))).replace("-", "\u2212")
    return f"{v:g}".replace("-", "\u2212")


# ---------------------------------------------------------------------------
# PNG I/O (stdlib)
# ---------------------------------------------------------------------------

def read_png(path: Path):
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(path)
    pos = 8
    idat = b""
    w = h = None
    color_type = None
    while pos < len(data):
        ln = struct.unpack(">I", data[pos : pos + 4])[0]
        tag = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + ln]
        pos += 12 + ln
        if tag == b"IHDR":
            w, h, _bit, color_type, *_ = struct.unpack(">IIBBBBB", chunk)
        elif tag == b"IDAT":
            idat += chunk
        elif tag == b"IEND":
            break
    raw = zlib.decompress(idat)
    bpp = {2: 3, 6: 4}[color_type]
    stride = w * bpp
    rows = []
    i = 0
    prev = bytearray(stride)
    for _ in range(h):
        filt = raw[i]
        cur = bytearray(raw[i + 1 : i + 1 + stride])
        i += 1 + stride
        if filt == 1:
            for x in range(stride):
                left = cur[x - bpp] if x >= bpp else 0
                cur[x] = (cur[x] + left) & 255
        elif filt == 2:
            for x in range(stride):
                cur[x] = (cur[x] + prev[x]) & 255
        elif filt == 3:
            for x in range(stride):
                left = cur[x - bpp] if x >= bpp else 0
                cur[x] = (cur[x] + ((left + prev[x]) // 2)) & 255
        elif filt == 4:
            for x in range(stride):
                a = cur[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                cur[x] = (cur[x] + pr) & 255
        elif filt != 0:
            raise ValueError(filt)
        rows.append(bytes(cur))
        prev = cur
    rgb = np.zeros((h, w, 3), np.uint8)
    for y, row in enumerate(rows):
        if bpp == 3:
            rgb[y] = np.frombuffer(row, np.uint8).reshape(w, 3)
        else:
            a = np.frombuffer(row, np.uint8).reshape(w, 4)
            rgb[y] = a[:, :3]
    return rgb


def write_png(path: Path, rgb: np.ndarray) -> None:
    h, w = rgb.shape[:2]
    raw = b"".join(b"\x00" + rgb[i].tobytes() for i in range(h))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(
            ">I", zlib.crc32(tag + data) & 0xFFFFFFFF
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(raw, 9)))
        f.write(chunk(b"IEND", b""))


def resize_rgb(src: np.ndarray, nw: int, nh: int) -> np.ndarray:
    h, w = src.shape[:2]
    if nw == w and nh == h:
        return src
    ys = (np.arange(nh) + 0.5) * h / nh - 0.5
    xs = (np.arange(nw) + 0.5) * w / nw - 0.5
    y0 = np.clip(np.floor(ys).astype(int), 0, h - 1)
    x0 = np.clip(np.floor(xs).astype(int), 0, w - 1)
    y1 = np.clip(y0 + 1, 0, h - 1)
    x1 = np.clip(x0 + 1, 0, w - 1)
    wy = (ys - np.floor(ys)).reshape(nh, 1, 1)
    wx = (xs - np.floor(xs)).reshape(1, nw, 1)
    c00 = src[y0][:, x0].astype(np.float64)
    c01 = src[y0][:, x1].astype(np.float64)
    c10 = src[y1][:, x0].astype(np.float64)
    c11 = src[y1][:, x1].astype(np.float64)
    top = c00 * (1.0 - wx) + c01 * wx
    bot = c10 * (1.0 - wx) + c11 * wx
    out = top * (1.0 - wy) + bot * wy
    return np.clip(out, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# Portable font rendering — Pillow ImageFont.truetype on committed faces
# ---------------------------------------------------------------------------

def ttf_cmap(path: Path) -> frozenset[int]:
    """Unicode codepoints with a non-zero glyph id in the TTF cmap."""
    data = path.read_bytes()
    ntables = struct.unpack(">H", data[4:6])[0]
    tables: dict[bytes, tuple[int, int]] = {}
    off = 12
    for _ in range(ntables):
        tag = data[off : off + 4]
        _csum, toff, tlen = struct.unpack(">III", data[off + 4 : off + 16])
        tables[tag] = (toff, tlen)
        off += 16
    if b"cmap" not in tables:
        raise SystemExit(f"{path} has no cmap")
    toff, tlen = tables[b"cmap"]
    cmap = data[toff : toff + tlen]
    _ver, nsub = struct.unpack(">HH", cmap[0:4])
    cps: set[int] = set()
    for i in range(nsub):
        _plat, _enc, suboff = struct.unpack(">HHI", cmap[4 + i * 8 : 12 + i * 8])
        fmt = struct.unpack(">H", cmap[suboff : suboff + 2])[0]
        if fmt == 4:
            _length, _lang, seg_x2 = struct.unpack(">HHH", cmap[suboff + 2 : suboff + 8])
            nseg = seg_x2 // 2
            end_off = suboff + 14
            ends = struct.unpack(">" + "H" * nseg, cmap[end_off : end_off + 2 * nseg])
            start_off = end_off + 2 * nseg + 2
            starts = struct.unpack(">" + "H" * nseg, cmap[start_off : start_off + 2 * nseg])
            delta_off = start_off + 2 * nseg
            deltas = struct.unpack(">" + "h" * nseg, cmap[delta_off : delta_off + 2 * nseg])
            range_off = delta_off + 2 * nseg
            ranges = struct.unpack(">" + "H" * nseg, cmap[range_off : range_off + 2 * nseg])
            for si in range(nseg):
                for cp in range(starts[si], ends[si] + 1):
                    if ranges[si] == 0:
                        gid = (cp + deltas[si]) & 0xFFFF
                    else:
                        glyph_off = range_off + 2 * si + ranges[si] + 2 * (cp - starts[si])
                        gid = struct.unpack(">H", cmap[glyph_off : glyph_off + 2])[0]
                        if gid:
                            gid = (gid + deltas[si]) & 0xFFFF
                    if gid:
                        cps.add(cp)
        elif fmt == 12:
            ng = struct.unpack(">I", cmap[suboff + 12 : suboff + 16])[0]
            p = suboff + 16
            for _g in range(ng):
                start, end, start_gid = struct.unpack(">III", cmap[p : p + 12])
                for cp in range(start, end + 1):
                    gid = start_gid + (cp - start)
                    if gid:
                        cps.add(cp)
                p += 12
    return frozenset(cps)


class Font:
    """Hanken for Latin; DejaVu for Hanken-missing glyphs. No host soname."""

    def __init__(self, latin_path: Path, greek_path: Path):
        if not latin_path.is_file():
            raise SystemExit(f"committed Hanken TTF missing: {latin_path}")
        if not greek_path.is_file():
            raise SystemExit(f"committed DejaVu TTF missing: {greek_path}")
        self.latin_path = latin_path
        self.greek_path = greek_path
        self.latin_cmap = ttf_cmap(latin_path)
        self.greek_cmap = ttf_cmap(greek_path)
        for required in ("\u0394", "\u03c6"):
            if ord(required) not in self.greek_cmap:
                raise SystemExit(f"{greek_path.name} missing {required!r}")
        self._latin: dict[int, ImageFont.FreeTypeFont] = {}
        self._greek: dict[int, ImageFont.FreeTypeFont] = {}

    def face_for(self, ch: str) -> str:
        cp = ord(ch)
        if cp in self.latin_cmap:
            return "Hanken Grotesk"
        if cp in self.greek_cmap:
            return "DejaVu Sans"
        raise SystemExit(f"no committed face covers U+{cp:04X} {ch!r}")

    def _face(self, px: int, ch: str):
        name = self.face_for(ch)
        if name == "Hanken Grotesk":
            cache, path = self._latin, self.latin_path
        else:
            cache, path = self._greek, self.greek_path
        if px not in cache:
            cache[px] = ImageFont.truetype(str(path), size=px)
        return cache[px]

    def measure(self, text: str, px: int) -> tuple[int, int]:
        gray, _ = self.render_gray(text, px)
        return gray.shape[1], gray.shape[0]

    def render_gray(self, text: str, px: int) -> tuple[np.ndarray, int]:
        """Return (H×W uint8 coverage, baseline y)."""
        glyphs = []
        width = 0.0
        max_top = 0
        max_bot = 0
        for ch in text:
            face = self._face(px, ch)
            left, top, right, bottom = face.getbbox(ch, anchor="ls")
            w = max(int(math.ceil(right - left)), 1)
            h = max(int(math.ceil(bottom - top)), 1)
            im = Image.new("L", (w, h), 0)
            ImageDraw.Draw(im).text(
                (-left, -top), ch, font=face, fill=255, anchor="ls"
            )
            arr = np.asarray(im, dtype=np.uint8)
            adv = float(face.getlength(ch))
            bitmap_top = int(round(-top))
            glyphs.append((arr, left, bitmap_top, adv))
            max_top = max(max_top, bitmap_top)
            max_bot = max(max_bot, arr.shape[0] - bitmap_top)
            width += adv
        height = max(max_top + max_bot, 1)
        canvas = np.zeros((height, max(int(math.ceil(width)) + 4, 1)), np.uint8)
        pen = 0.0
        for arr, left, bitmap_top, adv in glyphs:
            y0 = max_top - bitmap_top
            x0 = int(round(pen + left))
            gh, gw = arr.shape
            x1 = x0 + gw
            y1 = y0 + gh
            if x0 < 0 or y0 < 0:
                sx = max(0, -x0)
                sy = max(0, -y0)
                arr = arr[sy:, sx:]
                x0 = max(x0, 0)
                y0 = max(y0, 0)
                gh, gw = arr.shape
                x1 = x0 + gw
                y1 = y0 + gh
            if y1 > canvas.shape[0] or x1 > canvas.shape[1]:
                new = np.zeros(
                    (max(canvas.shape[0], y1), max(canvas.shape[1], x1)), np.uint8
                )
                new[: canvas.shape[0], : canvas.shape[1]] = canvas
                canvas = new
            dst = canvas[y0:y1, x0:x1]
            np.maximum(dst, arr[: dst.shape[0], : dst.shape[1]], out=dst)
            pen += adv
        return canvas, max_top


# ---------------------------------------------------------------------------
# drawing
# ---------------------------------------------------------------------------

def blit_gray(rgb: np.ndarray, gray: np.ndarray, x: int, y: int, color) -> None:
    gh, gw = gray.shape
    H, W = rgb.shape[:2]
    x0, y0 = int(round(x)), int(round(y))
    xs0, ys0 = max(0, x0), max(0, y0)
    xs1, ys1 = min(W, x0 + gw), min(H, y0 + gh)
    if xs0 >= xs1 or ys0 >= ys1:
        return
    g = gray[ys0 - y0 : ys1 - y0, xs0 - x0 : xs1 - x0].astype(np.float64) / 255.0
    sl = rgb[ys0:ys1, xs0:xs1].astype(np.float64)
    col = np.asarray(color, dtype=np.float64).reshape(1, 1, 3)
    rgb[ys0:ys1, xs0:xs1] = np.clip(sl * (1.0 - g[..., None]) + col * g[..., None], 0, 255).astype(
        np.uint8
    )


def text(
    rgb,
    font: Font,
    s: str,
    x,
    y,
    px: int,
    color=INK,
    align="left",
    valign="baseline",
):
    gray, base = font.render_gray(s, px)
    gh, gw = gray.shape
    x = float(x)
    y = float(y)
    if align == "center":
        x -= gw / 2
    elif align == "right":
        x -= gw
    if valign == "top":
        y0 = y
    elif valign == "bottom":
        y0 = y - gh
    elif valign == "middle":
        y0 = y - gh / 2
    else:  # baseline
        y0 = y - base
    blit_gray(rgb, gray, int(round(x)), int(round(y0)), color)


def vtext(rgb, font: Font, s: str, x, y, px: int, color=INK):
    """Rotate 90° CCW, center at (x, y)."""
    gray, _ = font.render_gray(s, px)
    rot = np.rot90(gray, 1)
    rh, rw = rot.shape
    blit_gray(rgb, rot, int(round(x - rw / 2)), int(round(y - rh / 2)), color)


def line(rgb, x0, y0, x1, y1, color, width=1.2):
    h, w = rgb.shape[:2]
    x0, y0, x1, y1 = float(x0), float(y0), float(x1), float(y1)
    dx, dy = x1 - x0, y1 - y0
    L = (dx * dx + dy * dy) ** 0.5
    if L < 1e-6:
        return
    pad = width * 1.5 + 1.0
    xmin = max(int(np.floor(min(x0, x1) - pad)), 0)
    xmax = min(int(np.ceil(max(x0, x1) + pad)) + 1, w)
    ymin = max(int(np.floor(min(y0, y1) - pad)), 0)
    ymax = min(int(np.ceil(max(y0, y1) + pad)) + 1, h)
    if xmin >= xmax or ymin >= ymax:
        return
    ys, xs = np.mgrid[ymin:ymax, xmin:xmax]
    px = xs + 0.5
    py = ys + 0.5
    t = ((px - x0) * dx + (py - y0) * dy) / (L * L)
    t = np.clip(t, 0.0, 1.0)
    dist = np.sqrt((px - (x0 + t * dx)) ** 2 + (py - (y0 + t * dy)) ** 2)
    a = np.clip((width * 0.5 + 0.55) - dist, 0.0, 1.0)
    if not np.any(a):
        return
    sl = rgb[ymin:ymax, xmin:xmax].astype(np.float64)
    col = np.asarray(color, dtype=np.float64).reshape(1, 1, 3)
    rgb[ymin:ymax, xmin:xmax] = np.clip(sl * (1.0 - a[..., None]) + col * a[..., None], 0, 255).astype(
        np.uint8
    )


def circle(rgb, cx, cy, r, color, fill=True, stroke=1.2):
    h, w = rgb.shape[:2]
    cx, cy, r = float(cx), float(cy), float(r)
    pad = r + stroke + 1.5
    xmin = max(int(np.floor(cx - pad)), 0)
    xmax = min(int(np.ceil(cx + pad)) + 1, w)
    ymin = max(int(np.floor(cy - pad)), 0)
    ymax = min(int(np.ceil(cy + pad)) + 1, h)
    if xmin >= xmax or ymin >= ymax:
        return
    ys, xs = np.mgrid[ymin:ymax, xmin:xmax]
    dist = np.sqrt((xs + 0.5 - cx) ** 2 + (ys + 0.5 - cy) ** 2)
    if fill:
        a = np.clip((r + 0.45) - dist, 0.0, 1.0)
    else:
        a = np.clip((stroke * 0.5 + 0.45) - np.abs(dist - r), 0.0, 1.0)
    sl = rgb[ymin:ymax, xmin:xmax].astype(np.float64)
    col = np.asarray(color, dtype=np.float64).reshape(1, 1, 3)
    rgb[ymin:ymax, xmin:xmax] = np.clip(sl * (1.0 - a[..., None]) + col * a[..., None], 0, 255).astype(
        np.uint8
    )


def blit_img(rgb, img, x, y):
    h, w = img.shape[:2]
    x, y = int(round(x)), int(round(y))
    H, W = rgb.shape[:2]
    xs0, ys0 = max(0, x), max(0, y)
    xs1, ys1 = min(W, x + w), min(H, y + h)
    if xs0 >= xs1 or ys0 >= ys1:
        return
    rgb[ys0:ys1, xs0:xs1] = img[ys0 - y : ys1 - y, xs0 - x : xs1 - x]


# ---------------------------------------------------------------------------
# frames — crop only; never re-render. Lab stills are optional.
# ---------------------------------------------------------------------------

STILL_PHIS = (90, 105, 120, 135)
STILL_SURFS = ("s0", "t1")


def frame_path(surf: str, phi: int) -> Path:
    return FRAMES / f"m4_{surf}_phi_{phi:03d}.png"


def missing_frames() -> list[Path]:
    return [
        frame_path(surf, phi)
        for surf in STILL_SURFS
        for phi in STILL_PHIS
        if not frame_path(surf, phi).is_file()
    ]


def load_cropped_frame(surf: str, phi: int) -> np.ndarray:
    x0, y0, x1, y1 = CROP
    path = frame_path(surf, phi)
    im = read_png(path)
    crop = im[y0:y1, x0:x1]
    # refuse to ship a still that still has the old in-frame caption
    # (caption lives at source y 778–798; crop y1=601)
    if y1 > 770:
        raise SystemExit(f"crop y1={y1} would keep the caption band")
    return crop


# ---------------------------------------------------------------------------
# Fig 1 — ACS plot only
# ---------------------------------------------------------------------------

def render_plot(metrics: dict, font: Font) -> np.ndarray:
    rgb = np.full((PLOT_H, PLOT_W, 3), 255, np.uint8)

    series = metrics["series"]
    interpolants = metrics["interpolants"]
    font_px = PLOT_FONT_PX  # 17 * 1200 / 632 → 32

    # Full-canvas plot: no title, no subtitle, no molecule strip.
    # Gutters sized for 32 px type so y-label, ticks, point labels, and
    # both interpolant numerals do not collide or clip. Canvas stays 1200×630.
    y_label = "\u0394E = E(T1) \u2212 E(S0) (kJ/mol)"
    x_label = "\u03c6 / CNNC (deg)"
    xticks = [90, 105, 120, 135]
    yticks = [-20, 0, 20, 40, 60, 80, 100, 120]

    ytick_w = max(font.measure(fmt_tick(v), font_px)[0] for v in yticks)
    _, ylab_box_w = font.measure(y_label, font_px)  # height before rot = width after
    _, xlab_h = font.measure(x_label, font_px)
    _, tick_h = font.measure("120", font_px)

    left_pad = 16
    ylab_to_ticks = 16
    ticks_to_spine = 14
    tick_len = 8
    right_pad = 28
    top_pad = 36
    tick_label_gap = 10
    xlab_gap = 12
    bottom_pad = 14

    plot_l = left_pad + ylab_box_w + ylab_to_ticks + ytick_w + ticks_to_spine
    plot_r = PLOT_W - right_pad
    plot_t = top_pad
    plot_b = PLOT_H - (bottom_pad + xlab_h + xlab_gap + tick_h + tick_label_gap + tick_len)
    xlim = (86.5, 138.5)  # pad only; ticks stay 90/105/120/135
    ylim = (-36.0, 148.0)

    def X(phi):
        return plot_l + (phi - xlim[0]) / (xlim[1] - xlim[0]) * (plot_r - plot_l)

    def Y(de):
        return plot_b - (de - ylim[0]) / (ylim[1] - ylim[0]) * (plot_b - plot_t)

    # spines
    line(rgb, plot_l, plot_t, plot_r, plot_t, INK, 0.9)
    line(rgb, plot_l, plot_b, plot_r, plot_b, INK, 0.9)
    line(rgb, plot_l, plot_t, plot_l, plot_b, INK, 0.9)
    line(rgb, plot_r, plot_t, plot_r, plot_b, INK, 0.9)

    # ΔE = 0 hairline (near-black, thin) — behind the series
    y0 = Y(0.0)
    line(rgb, plot_l, y0, plot_r, y0, ZERO_C, 0.85)

    for xv in xticks:
        px = X(xv)
        line(rgb, px, plot_b, px, plot_b + tick_len, INK, 0.8)
        text(
            rgb, font, fmt_tick(xv), px, plot_b + tick_len + tick_label_gap,
            font_px, INK, align="center", valign="top",
        )
    for yv in yticks:
        py = Y(yv)
        line(rgb, plot_l - tick_len, py, plot_l, py, INK, 0.8)
        text(
            rgb, font, fmt_tick(yv), plot_l - ticks_to_spine, py,
            font_px, INK, align="right", valign="middle",
        )

    vtext(
        rgb, font, y_label,
        left_pad + ylab_box_w / 2,
        (plot_t + plot_b) / 2,
        font_px,
        INK,
    )
    text(
        rgb, font, x_label,
        (plot_l + plot_r) / 2,
        plot_b + tick_len + tick_label_gap + tick_h + xlab_gap,
        font_px, INK, align="center", valign="top",
    )

    # Two series: adjacent both-assigned neighbors only; straight segments.
    for fam in FAMILY_ORDER:
        pts = series[fam]
        color = FAMILY_COLOR[fam]
        for (a, da), (b, db) in zip(pts, pts[1:]):
            line(rgb, X(a), Y(da), X(b), Y(db), color, 2.15)
        for phi, de in pts:
            if fam == "s0_relaxed":
                circle(rgb, X(phi), Y(de), 5.1, color, fill=True)
            else:
                circle(rgb, X(phi), Y(de), 5.1, color, fill=False, stroke=1.8)
                circle(rgb, X(phi), Y(de), 2.2, color, fill=True)

    # Point labels from file values, 2 decimals. Offsets keep strings off
    # markers, both series, the 0-line, and the two interpolant labels.
    label_off = {
        "s0_relaxed": {
            90: (-8, 18, "right"),
            105: (14, -28, "left"),
            120: (12, -26, "left"),
            135: (-8, -18, "right"),
        },
        "t1_relaxed": {
            90: (10, 20, "left"),
            105: (-10, 22, "right"),
            120: (-10, 20, "right"),
            135: (10, 16, "left"),
        },
    }
    for fam in FAMILY_ORDER:
        for phi, de in series[fam]:
            dx, dy, al = label_off[fam][int(phi)]
            text(
                rgb, font, fmt_delta(de),
                X(phi) + dx, Y(de) + dy,
                font_px, INK, align=al, valign="middle",
            )

    # Linear interpolants of the 90–105 pairs at ΔE = 0. Not 110°.
    # Not drawn as an MECP or an evaluated degeneracy: tick + stored angle.
    s0_xc = interpolants["s0_relaxed"]
    t1_xc = interpolants["t1_relaxed"]
    line(rgb, X(s0_xc), y0, X(s0_xc), y0 + 10, SERIES_S0, 0.95)
    line(rgb, X(t1_xc), y0, X(t1_xc), y0 + 10, SERIES_T1, 0.95)
    text(
        rgb, font, f"{s0_xc:.2f}\u00b0",
        X(s0_xc) - 8, y0 + 12,
        font_px, INK, align="right", valign="top",
    )
    text(
        rgb, font, f"{t1_xc:.2f}\u00b0",
        X(t1_xc) + 8, y0 + 12,
        font_px, INK, align="left", valign="top",
    )

    # Legend in the empty upper-left of the data box.
    legend_x = plot_l + 18
    legend_y = plot_t + 22
    line(rgb, legend_x, legend_y, legend_x + 28, legend_y, SERIES_S0, 2.15)
    circle(rgb, legend_x + 14, legend_y, 5.1, SERIES_S0, fill=True)
    text(
        rgb, font, FAMILY_LABEL["s0_relaxed"],
        legend_x + 38, legend_y,
        font_px, INK, align="left", valign="middle",
    )
    legend_y2 = legend_y + 36
    line(rgb, legend_x, legend_y2, legend_x + 28, legend_y2, SERIES_T1, 2.15)
    circle(rgb, legend_x + 14, legend_y2, 5.1, SERIES_T1, fill=False, stroke=1.8)
    circle(rgb, legend_x + 14, legend_y2, 2.2, SERIES_T1, fill=True)
    text(
        rgb, font, FAMILY_LABEL["t1_relaxed"],
        legend_x + 38, legend_y2,
        font_px, INK, align="left", valign="middle",
    )

    return rgb


# ---------------------------------------------------------------------------
# Fig 2 / Fig 3 — large stills, four to a page width
# ---------------------------------------------------------------------------

def render_stills(font: Font, surf: str) -> np.ndarray:
    """One row of four large identity-only stills. Angle tags; no energies."""
    rgb = np.full((STILL_H, STILL_W, 3), 255, np.uint8)
    phis = (90, 105, 120, 135)
    font_px = STILL_FONT_PX  # 17 * 1600 / 632 → 43

    # Larger left gutter for vertical S0/T1; more space under φ tags.
    # Canvas stays 1600×520; molecules shrink only as much as the gutters require.
    _, tag_box_w = font.measure("T1", font_px)  # height before rot = width after
    _, angle_h = font.measure("135\u00b0", font_px)

    margin_l = 20
    margin_r = 20
    margin_t = 16
    margin_b = 18
    label_col = tag_box_w + 20
    angle_band = angle_h + 16
    gap = 14

    inner_l = margin_l + label_col
    inner_r = STILL_W - margin_r
    inner_t = margin_t
    inner_b = STILL_H - margin_b - angle_band
    usable_w = inner_r - inner_l
    panel_w = (usable_w - gap * (len(phis) - 1)) / len(phis)
    panel_h = inner_b - inner_t

    vtext(
        rgb, font, surf.upper(),
        margin_l + tag_box_w / 2,
        (inner_t + inner_b) / 2,
        font_px,
        INK,
    )

    for i, phi in enumerate(phis):
        src = load_cropped_frame(surf, phi)
        scale = min(panel_w / src.shape[1], panel_h / src.shape[0])
        nw = max(1, int(round(src.shape[1] * scale)))
        nh = max(1, int(round(src.shape[0] * scale)))
        im = resize_rgb(src, nw, nh)
        px0 = inner_l + i * (panel_w + gap)
        cx = px0 + panel_w / 2
        x = cx - nw / 2
        y = inner_t + (panel_h - nh) / 2
        blit_img(rgb, im, x, y)
        text(
            rgb, font, f"{phi}\u00b0",
            cx, STILL_H - margin_b,
            font_px, INK, align="center", valign="bottom",
        )

    return rgb


def load_plot_font() -> Font:
    """Committed Hanken + DejaVu via Pillow ImageFont.truetype."""
    font = Font(HANKEN_TTF, DEJAVU_TTF)
    gray, _ = font.render_gray("Hanken", PLOT_FONT_PX)
    if gray.max() == 0:
        raise SystemExit("Hanken rasterized empty")
    for ch in ("\u0394", "\u03c6", "\u2212"):
        face = font.face_for(ch)
        g, _ = font.render_gray(ch, PLOT_FONT_PX)
        # Letter-sized glyphs must be taller than Hanken's 16 px .notdef box.
        # U+2212 is a hairline; empty coverage is the only reject.
        too_small = ch in "\u0394\u03c6" and g.shape[0] < 18
        if g.max() == 0 or too_small:
            raise SystemExit(
                f"refusing tofu/empty for {ch!r} U+{ord(ch):04X} via {face} "
                f"size={g.shape}"
            )
        print(f"glyph {ch} U+{ord(ch):04X} → {face} ({g.shape[1]}x{g.shape[0]})")
    return font


def main():
    metrics = load_metrics(METRICS_PATH)
    print("points (from results/bayes-metrics.json):")
    for fam in FAMILY_ORDER:
        print(f"  {fam}:")
        for phi, de in metrics["series"][fam]:
            print(f"    phi={phi:g}  deltaE_kJmol={de}  label={fmt_delta(de)}")
    for fam in FAMILY_ORDER:
        xc = metrics["interpolants"][fam]
        print(f"interpolant {fam} phi={xc}  label={xc:.2f}°")
    print("pairs with a drawn interpolant: 90–105 on each family; 110° not marked")
    print("ACS: no title, no subtitle, no stills on the plot")
    print(
        f"standing rule: font_px = round({BODY_PX} * W / {DISPLAY_W}) "
        f"→ plot {PLOT_W}×{PLOT_H} = {PLOT_FONT_PX}px, "
        f"stills {STILL_W}×{STILL_H} = {STILL_FONT_PX}px"
    )

    font = load_plot_font()
    print(f"Pillow faces: {HANKEN_TTF.name} + {DEJAVU_TTF.name}")
    print(f"ImageFont.truetype plot={PLOT_FONT_PX} stills={STILL_FONT_PX}")

    plot = render_plot(metrics, font)
    if plot.shape[1] != PLOT_W or plot.shape[0] != PLOT_H:
        raise SystemExit(f"bad plot size {plot.shape}")
    write_png(OUT_PREVIEW, plot)
    shutil.copy2(OUT_PREVIEW, OUT_PUBLISHED)
    print(f"wrote {OUT_PREVIEW} {PLOT_W}x{PLOT_H}")
    print(f"copied {OUT_PUBLISHED}")

    missing = missing_frames()
    if missing:
        print(f"stills skipped: {len(missing)} lab frame(s) not in checkout")
        print("published still PNGs left unchanged")
        return

    s0 = render_stills(font, "s0")
    t1 = render_stills(font, "t1")
    if s0.shape[1] != STILL_W or s0.shape[0] != STILL_H:
        raise SystemExit(f"bad S0 stills size {s0.shape}")
    if t1.shape[1] != STILL_W or t1.shape[0] != STILL_H:
        raise SystemExit(f"bad T1 stills size {t1.shape}")
    write_png(OUT_S0_PREVIEW, s0)
    write_png(OUT_T1_PREVIEW, t1)
    shutil.copy2(OUT_S0_PREVIEW, OUT_S0_PUBLISHED)
    shutil.copy2(OUT_T1_PREVIEW, OUT_T1_PUBLISHED)
    print(f"wrote {OUT_S0_PUBLISHED} {STILL_W}x{STILL_H}")
    print(f"wrote {OUT_T1_PUBLISHED} {STILL_W}x{STILL_H}")


if __name__ == "__main__":
    main()

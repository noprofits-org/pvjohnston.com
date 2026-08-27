#!/usr/bin/env python3
"""M4 SF-TDDFT figures: ACS plot (Fig 1) + large S0/T1 stills (Fig 2/3).

Reads metrics.json at runtime for the four (φ, ΔE) points and the
single 90–105 interpolant. Does not invent points, does not mark 110°,
does not draw a second zero. Stills composite existing frames only
(shared edge-on camera); identity tags, no energies.

Usage:
  python3 /workspace/hillel-m4-sft/analysis/make_deltaE_figure.py
"""
from __future__ import annotations

import json
import shutil
import struct
import zlib
from pathlib import Path

import ctypes
from ctypes import (
    POINTER,
    Structure,
    c_char_p,
    c_int,
    c_int16,
    c_int32,
    c_long,
    c_short,
    c_ubyte,
    c_uint,
    c_uint16,
    c_uint32,
    c_void_p,
)
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
METRICS_PATH = ROOT / "metrics.json"
FRAMES = ROOT / "frames"
OUT_PLOT = HERE / "fig_deltaE_vs_phi.png"
OUT_PLOT_EASY = ROOT / "fig_deltaE_vs_phi.png"
OUT_S0 = HERE / "fig_s0_stills.png"
OUT_T1 = HERE / "fig_t1_stills.png"
# Face: Hanken Grotesk (converted woff2 → static Regular TTF).
# DejaVu only if Hanken will not rasterize, or for a missing glyph (Δ, φ).
HANKEN_TTF = HERE / "hanken-grotesk.ttf"
DEJAVU_TTF = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")

# Standing rule (Peter / Heisenberg): plot type matches page body size.
# Desktop in-article image width DISPLAY_W=632 CSS px; body BODY_PX=17 (Hanken).
# When a PNG is shown at 632 px wide, every plot string must be 17 CSS pixels:
#   font_px_on_canvas = round(BODY_PX * canvas_w / DISPLAY_W)
# Plot 1200×630 → 17*1200/632 = 32.278… → 32 px (ticks, axis labels, ΔE, 98.89°)
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
SERIES = np.array([36, 74, 128], dtype=np.float64)    # one series
WHITE = np.array([255, 255, 255], dtype=np.uint8)

# Shared-camera crop of the 900×820 frames (union of molecule + pad 20).
# Edge-on CNNC camera: molecule bbox union x[171:690] y[48:581].
# Drops the in-frame identity caption band (y 778–798; previously y≥770).
CROP = (151, 28, 710, 601)  # x0, y0, x1, y1


# ---------------------------------------------------------------------------
# metrics — only source of plotted numbers
# ---------------------------------------------------------------------------

def load_metrics(path: Path) -> dict:
    m = json.loads(path.read_text())
    pts = []
    for p in m["points"]:
        if not (p.get("both_converged") and p.get("both_assigned")):
            raise SystemExit(f"refusing to plot: φ={p.get('phi_deg')} not both_converged+assigned")
        pts.append((float(p["phi_deg"]), float(p["deltaE_kJmol"])))
    pts.sort(key=lambda t: t[0])

    crossings = []
    for pair in m["neighboring_pairs"]:
        ic = pair.get("interpolated_crossing_phi_deg")
        if pair.get("sign_change") and ic is not None:
            crossings.append((tuple(pair["pair"]), float(ic)))
        else:
            # honesty: null interpolant stays undrawn
            if ic is not None:
                raise SystemExit("non-null interpolant on a non-sign-change pair")

    if len(crossings) != 1:
        raise SystemExit(f"expected exactly one interpolant, got {crossings!r}")
    pair_ab, xc = crossings[0]
    if pair_ab != (90, 105):
        raise SystemExit(f"interpolant is not on 90–105: {pair_ab}")
    file_xc = float(m["crossing_phi_deg"])
    if abs(file_xc - xc) > 1e-9:
        raise SystemExit("crossing_phi_deg != neighboring_pairs[0] interpolant")

    return {
        "points": pts,
        "crossing_phi": xc,
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
# FreeType (Hanken Grotesk; DejaVu only as last-resort / missing-glyph)
# ---------------------------------------------------------------------------

class FT_Bitmap(Structure):
    _fields_ = [
        ("rows", c_uint32),
        ("width", c_uint32),
        ("pitch", c_int32),
        ("buffer", POINTER(c_ubyte)),
        ("num_grays", c_uint16),
        ("pixel_mode", c_ubyte),
        ("palette_mode", c_ubyte),
        ("palette", c_void_p),
    ]


class FT_Vector(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


class FT_Glyph_Metrics(Structure):
    _fields_ = [
        ("width", c_long),
        ("height", c_long),
        ("horiBearingX", c_long),
        ("horiBearingY", c_long),
        ("horiAdvance", c_long),
        ("vertBearingX", c_long),
        ("vertBearingY", c_long),
        ("vertAdvance", c_long),
    ]


class FT_Outline(Structure):
    _fields_ = [
        ("n_contours", c_short),
        ("n_points", c_short),
        ("points", c_void_p),
        ("tags", c_void_p),
        ("contours", c_void_p),
        ("flags", c_int),
    ]


class FT_Generic(Structure):
    _fields_ = [("data", c_void_p), ("finalizer", c_void_p)]


class FT_GlyphSlotRec(Structure):
    _fields_ = [
        ("library", c_void_p),
        ("face", c_void_p),
        ("next", c_void_p),
        ("glyph_index", c_uint),
        ("generic", FT_Generic),
        ("metrics", FT_Glyph_Metrics),
        ("linearHoriAdvance", c_long),
        ("linearVertAdvance", c_long),
        ("advance", FT_Vector),
        ("format", c_uint32),
        ("bitmap", FT_Bitmap),
        ("bitmap_left", c_int),
        ("bitmap_top", c_int),
        ("outline", FT_Outline),
    ]


class FT_BBox(Structure):
    _fields_ = [("xMin", c_long), ("yMin", c_long), ("xMax", c_long), ("yMax", c_long)]


class FT_FaceRec(Structure):
    _fields_ = [
        ("num_faces", c_long),
        ("face_index", c_long),
        ("face_flags", c_long),
        ("style_flags", c_long),
        ("num_glyphs", c_long),
        ("family_name", c_char_p),
        ("style_name", c_char_p),
        ("num_fixed_sizes", c_int),
        ("available_sizes", c_void_p),
        ("num_charmaps", c_int),
        ("charmaps", c_void_p),
        ("generic", FT_Generic),
        ("bbox", FT_BBox),
        ("units_per_EM", c_uint16),
        ("ascender", c_int16),
        ("descender", c_int16),
        ("height", c_int16),
        ("max_advance_width", c_int16),
        ("max_advance_height", c_int16),
        ("underline_position", c_int16),
        ("underline_thickness", c_int16),
        ("glyph", POINTER(FT_GlyphSlotRec)),
        ("size", c_void_p),
        ("charmap", c_void_p),
    ]


FT_LOAD_RENDER = 4


class Font:
    def __init__(self, path: bytes, fallback_path: bytes | None = None):
        self.ft = ctypes.cdll.LoadLibrary("libfreetype.so.6")
        self.lib = c_void_p()
        if self.ft.FT_Init_FreeType(ctypes.byref(self.lib)) != 0:
            raise RuntimeError("FT_Init_FreeType")
        self.ft.FT_Get_Char_Index.restype = c_uint
        self.face_ptr = c_void_p()
        if self.ft.FT_New_Face(self.lib, path, 0, ctypes.byref(self.face_ptr)) != 0:
            raise RuntimeError("FT_New_Face")
        self.face = ctypes.cast(self.face_ptr, POINTER(FT_FaceRec)).contents
        self._px = None
        self.fallback_ptr = None
        self.fallback_face = None
        self._fb_px = None
        if fallback_path:
            fb = c_void_p()
            if self.ft.FT_New_Face(self.lib, fallback_path, 0, ctypes.byref(fb)) == 0:
                self.fallback_ptr = fb
                self.fallback_face = ctypes.cast(fb, POINTER(FT_FaceRec)).contents

    def _set_px(self, px: int) -> None:
        if self._px != px:
            if self.ft.FT_Set_Pixel_Sizes(self.face_ptr, 0, px) != 0:
                raise RuntimeError("FT_Set_Pixel_Sizes")
            self._px = px
        if self.fallback_ptr is not None and self._fb_px != px:
            if self.ft.FT_Set_Pixel_Sizes(self.fallback_ptr, 0, px) != 0:
                raise RuntimeError("FT_Set_Pixel_Sizes fallback")
            self._fb_px = px

    def _face_for_char(self, ch: str):
        idx = self.ft.FT_Get_Char_Index(self.face_ptr, ord(ch))
        if idx != 0 or self.fallback_ptr is None:
            return self.face_ptr, self.face
        fb_idx = self.ft.FT_Get_Char_Index(self.fallback_ptr, ord(ch))
        if fb_idx != 0:
            return self.fallback_ptr, self.fallback_face
        return self.face_ptr, self.face

    def measure(self, text: str, px: int) -> tuple[int, int]:
        self._set_px(px)
        w = 0
        for ch in text:
            face_ptr, face = self._face_for_char(ch)
            self.ft.FT_Load_Char(face_ptr, ord(ch), FT_LOAD_RENDER)
            w += face.glyph.contents.advance.x >> 6
        asc = int(round(self.face.ascender * px / max(self.face.units_per_EM, 1)))
        desc = int(round(-self.face.descender * px / max(self.face.units_per_EM, 1)))
        return w, asc + desc

    def render_gray(self, text: str, px: int) -> tuple[np.ndarray, int]:
        """Return (H×W uint8 coverage, baseline y)."""
        self._set_px(px)
        glyphs = []
        width = 0
        max_top = 0
        max_bot = 0
        for ch in text:
            face_ptr, face = self._face_for_char(ch)
            self.ft.FT_Load_Char(face_ptr, ord(ch), FT_LOAD_RENDER)
            slot = face.glyph.contents
            bm = slot.bitmap
            rows, cols, pitch = bm.rows, bm.width, bm.pitch
            if rows and cols and bm.buffer:
                buf = ctypes.string_at(bm.buffer, pitch * rows)
                arr = np.frombuffer(buf, np.uint8).reshape(rows, pitch)[:, :cols].copy()
            else:
                arr = np.zeros((1, 1), np.uint8)
            glyphs.append((arr, slot.bitmap_left, slot.bitmap_top, slot.advance.x >> 6))
            max_top = max(max_top, slot.bitmap_top)
            max_bot = max(max_bot, rows - slot.bitmap_top)
            width += slot.advance.x >> 6
        height = max(max_top + max_bot, 1)
        canvas = np.zeros((height, max(width + 4, 1)), np.uint8)
        pen = 0
        for arr, left, top, adv in glyphs:
            y0 = max_top - top
            x0 = pen + left
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
# frames — crop only; never re-render
# ---------------------------------------------------------------------------

def load_cropped_frame(surf: str, phi: int) -> np.ndarray:
    x0, y0, x1, y1 = CROP
    name = f"m4_{surf}_phi_{phi:03d}.png"
    im = read_png(FRAMES / name)
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

    pts = metrics["points"]
    xc = metrics["crossing_phi"]
    font_px = PLOT_FONT_PX  # 17 * 1200 / 632 → 32

    # Full-canvas plot: no title, no subtitle, no molecule strip.
    # Gutters sized for 32 px type so y-label, ticks, point labels, and 98.89°
    # do not collide or clip. Canvas stays 1200×630.
    y_label = "\u0394E = E(T1) \u2212 E(S0) (kJ/mol)"
    x_label = "\u03c6 / CNNC (deg)"
    xticks = [90, 105, 120, 135]
    yticks = [-20, 0, 20, 40, 60, 80, 100]

    ytick_w = max(font.measure(fmt_tick(v), font_px)[0] for v in yticks)
    _, ylab_box_w = font.measure(y_label, font_px)  # height before rot = width after
    _, xlab_h = font.measure(x_label, font_px)
    _, tick_h = font.measure("100", font_px)

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
    ylim = (-30.0, 118.0)

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

    # series — adjacent both-converged neighbors only; straight segments; no wrap
    for (a, da), (b, db) in zip(pts, pts[1:]):
        line(rgb, X(a), Y(da), X(b), Y(db), SERIES, 2.15)
    for phi, de in pts:
        circle(rgb, X(phi), Y(de), 5.1, SERIES, fill=True)

    # point labels (from file values, 2 decimals). Offsets grown with 32 px type
    # so labels miss markers, the series, the 0-line, and 98.89°.
    # 90: right and below the rising 90–105 segment (not on the line).
    # 105: left of the marker, above the 0-line (empty pocket; not on the
    # incoming 90–105 segment). Right-aligned so the string sits left of 105.
    # 135: left of the marker, slightly above, so it misses the incoming segment.
    # 98.89° sits right of the crossing tick, just under the 0-line, so it
    # stays clear of −19.10.
    label_off = {
        90: (36, 14, "left"),
        105: (-56, -36, "right"),
        120: (-18, -28, "right"),
        135: (-50, -6, "right"),
    }
    for phi, de in pts:
        dx, dy, al = label_off[int(phi)]
        text(
            rgb, font, fmt_delta(de),
            X(phi) + dx, Y(de) + dy,
            font_px, INK, align=al, valign="middle",
        )

    # ONE interpolant: 90–105 pair, y = 0 on that segment. Not 110°.
    xcp, ycp = X(xc), Y(0.0)
    line(rgb, xcp, ycp, xcp, ycp + 10, ZERO_C, 0.85)
    text(
        rgb, font, f"{xc:.2f}\u00b0",
        xcp + 12, ycp + 8,
        font_px, INK, align="left", valign="top",
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


def load_plot_font() -> tuple[Font, str]:
    """Hanken Grotesk TTF; DejaVu only if Hanken will not rasterize."""
    fallback = str(DEJAVU_TTF).encode()
    if HANKEN_TTF.is_file():
        try:
            font = Font(str(HANKEN_TTF).encode(), fallback_path=fallback)
            gray, _ = font.render_gray("Hanken", PLOT_FONT_PX)
            if gray.max() == 0:
                raise RuntimeError("Hanken rasterized empty")
            fam = (font.face.family_name or b"").decode("ascii", "replace")
            return font, fam
        except Exception as exc:
            print(f"Hanken failed ({exc}); falling back to DejaVu")
    return Font(fallback), "DejaVu Sans"


def main():
    metrics = load_metrics(METRICS_PATH)
    print("points (from metrics.json):")
    for phi, de in metrics["points"]:
        print(f"  phi={phi:g}  deltaE_kJmol={de}  label={fmt_delta(de)}")
    print(f"interpolant phi={metrics['crossing_phi']}  label={metrics['crossing_phi']:.2f}°")
    print("pairs with a drawn crossing: 90–105 only; 110° not marked")
    print("ACS: no title, no subtitle, no stills on the plot")
    print(
        f"standing rule: font_px = round({BODY_PX} * W / {DISPLAY_W}) "
        f"→ plot {PLOT_W}×{PLOT_H} = {PLOT_FONT_PX}px, "
        f"stills {STILL_W}×{STILL_H} = {STILL_FONT_PX}px"
    )

    font, face_name = load_plot_font()
    print(f"FreeType face: {face_name}")
    print(f"FT_Set_Pixel_Sizes plot={PLOT_FONT_PX} stills={STILL_FONT_PX}")

    plot = render_plot(metrics, font)
    if plot.shape[1] != PLOT_W or plot.shape[0] != PLOT_H:
        raise SystemExit(f"bad plot size {plot.shape}")
    write_png(OUT_PLOT, plot)
    shutil.copy2(OUT_PLOT, OUT_PLOT_EASY)
    print(f"wrote {OUT_PLOT} {PLOT_W}x{PLOT_H}")
    print(f"copied {OUT_PLOT_EASY}")

    s0 = render_stills(font, "s0")
    t1 = render_stills(font, "t1")
    if s0.shape[1] != STILL_W or s0.shape[0] != STILL_H:
        raise SystemExit(f"bad S0 stills size {s0.shape}")
    if t1.shape[1] != STILL_W or t1.shape[0] != STILL_H:
        raise SystemExit(f"bad T1 stills size {t1.shape}")
    write_png(OUT_S0, s0)
    write_png(OUT_T1, t1)
    print(f"wrote {OUT_S0} {STILL_W}x{STILL_H}")
    print(f"wrote {OUT_T1} {STILL_W}x{STILL_H}")


if __name__ == "__main__":
    main()

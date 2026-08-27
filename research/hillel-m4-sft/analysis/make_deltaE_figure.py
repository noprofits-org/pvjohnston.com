#!/usr/bin/env python3
"""M4 SF-TDDFT ΔE vs φ hero figure (1200×630).

Reads results/bayes-metrics.json at runtime for the four (φ, ΔE)
points and the single interpolant. Does not invent points, does not
mark 110°, does not draw a second zero. Frames are identity-only
stills.

Usage:
  python3 research/hillel-m4-sft/analysis/make_deltaE_figure.py
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
METRICS_PATH = ROOT / "results" / "bayes-metrics.json"
FRAMES = ROOT / "frames"
OUT_HERO = HERE / "fig_deltaE_vs_phi.png"
OUT_EASY = ROOT / "fig_deltaE_vs_phi.png"
FONT_PATH = b"/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

W, H = 1200, 630
INK = np.array([38, 38, 38], dtype=np.float64)       # ~0.15
ZERO_C = np.array([22, 22, 22], dtype=np.float64)
SERIES = np.array([36, 74, 128], dtype=np.float64)    # one series
WHITE = np.array([255, 255, 255], dtype=np.uint8)

# Shared-camera crop of the 900×820 frames (union of content + pad).
# Drops the unreadable-at-thumb identity caption band (y≥770).
CROP = (26, 48, 646, 752)  # x0, y0, x1, y1


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


def short_method(method: str) -> str:
    """ORCA 6.1.1 SF-TDA  LibXC(BHANDHLYP) D3BJ/def2-QZVPP"""
    return "ORCA 6.1.1 SF-TDA  LibXC(BHANDHLYP) D3BJ/def2-QZVPP"


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
# FreeType (DejaVu Sans)
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
    def __init__(self, path: bytes):
        self.ft = ctypes.cdll.LoadLibrary("libfreetype.so.6")
        self.lib = c_void_p()
        if self.ft.FT_Init_FreeType(ctypes.byref(self.lib)) != 0:
            raise RuntimeError("FT_Init_FreeType")
        self.face_ptr = c_void_p()
        if self.ft.FT_New_Face(self.lib, path, 0, ctypes.byref(self.face_ptr)) != 0:
            raise RuntimeError("FT_New_Face")
        self.face = ctypes.cast(self.face_ptr, POINTER(FT_FaceRec)).contents
        self._px = None

    def _set_px(self, px: int) -> None:
        if self._px != px:
            if self.ft.FT_Set_Pixel_Sizes(self.face_ptr, 0, px) != 0:
                raise RuntimeError("FT_Set_Pixel_Sizes")
            self._px = px

    def measure(self, text: str, px: int) -> tuple[int, int]:
        self._set_px(px)
        w = 0
        for ch in text:
            self.ft.FT_Load_Char(self.face_ptr, ord(ch), FT_LOAD_RENDER)
            w += self.face.glyph.contents.advance.x >> 6
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
            self.ft.FT_Load_Char(self.face_ptr, ord(ch), FT_LOAD_RENDER)
            slot = self.face.glyph.contents
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
                # clip negative bearings
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


def text_width(font: Font, s: str, px: int) -> int:
    return font.measure(s, px)[0]


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
# figure
# ---------------------------------------------------------------------------

def load_thumbs():
    x0, y0, x1, y1 = CROP
    out = {}
    for surf in ("s0", "t1"):
        for phi in (90, 105, 120, 135):
            name = f"m4_{surf}_phi_{phi:03d}.png"
            im = read_png(FRAMES / name)
            out[(surf, phi)] = im[y0:y1, x0:x1]
    return out


def render(metrics: dict) -> np.ndarray:
    font = Font(FONT_PATH)
    rgb = np.full((H, W, 3), 255, np.uint8)

    pts = metrics["points"]
    phis = [p[0] for p in pts]
    des = [p[1] for p in pts]
    xc = metrics["crossing_phi"]

    # layout — 2-row strip, plot in the middle band
    plot_l, plot_r = 100, 1168
    plot_t, plot_b = 172, 476
    xlim = (86.5, 138.5)  # pad only; ticks stay 90/105/120/135
    ylim = (-30.0, 118.0)

    def X(phi):
        return plot_l + (phi - xlim[0]) / (xlim[1] - xlim[0]) * (plot_r - plot_l)

    def Y(de):
        return plot_b - (de - ylim[0]) / (ylim[1] - ylim[0]) * (plot_b - plot_t)

    # title + method subtitle (11–12 pt near-black)
    text(rgb, font, "M4 S0/T1 gap", W / 2, 20, 16, INK, align="center", valign="middle")
    text(
        rgb,
        font,
        short_method(metrics["method"]),
        W / 2,
        40,
        13,
        INK,
        align="center",
        valign="middle",
    )

    # frames — S0 top / T1 bottom, aligned to φ
    thumbs = load_thumbs()
    thumb_w, thumb_h = 188, 104
    s0_top, t1_top = 52, 512
    for surf, top, tag in (("s0", s0_top, "S0"), ("t1", t1_top, "T1")):
        text(rgb, font, tag, 14, top + thumb_h / 2, 12, INK, align="left", valign="middle")
        for phi in (90, 105, 120, 135):
            src = thumbs[(surf, phi)]
            scale = min(thumb_w / src.shape[1], thumb_h / src.shape[0])
            nw = max(1, int(round(src.shape[1] * scale)))
            nh = max(1, int(round(src.shape[0] * scale)))
            im = resize_rgb(src, nw, nh)
            cx = X(phi)
            x = cx - nw / 2
            y = top + (thumb_h - nh) / 2
            blit_img(rgb, im, x, y)

    # spines
    line(rgb, plot_l, plot_t, plot_r, plot_t, INK, 0.9)
    line(rgb, plot_l, plot_b, plot_r, plot_b, INK, 0.9)
    line(rgb, plot_l, plot_t, plot_l, plot_b, INK, 0.9)
    line(rgb, plot_r, plot_t, plot_r, plot_b, INK, 0.9)

    # ΔE = 0 hairline (near-black, thin) — behind the series
    y0 = Y(0.0)
    line(rgb, plot_l, y0, plot_r, y0, ZERO_C, 0.85)

    # ticks
    xticks = [90, 105, 120, 135]
    yticks = [-20, 0, 20, 40, 60, 80, 100]
    for xv in xticks:
        px = X(xv)
        line(rgb, px, plot_b, px, plot_b + 5, INK, 0.8)
        text(rgb, font, fmt_tick(xv), px, plot_b + 8, 12, INK, align="center", valign="top")
    for yv in yticks:
        py = Y(yv)
        line(rgb, plot_l - 5, py, plot_l, py, INK, 0.8)
        text(rgb, font, fmt_tick(yv), plot_l - 8, py, 12, INK, align="right", valign="middle")

    # axis labels (y labelpad 8, x pad 6)
    vtext(
        rgb,
        font,
        "\u0394E = E(T1) \u2212 E(S0) (kJ/mol)",
        18,
        (plot_t + plot_b) / 2,
        14,
        INK,
    )
    text(
        rgb,
        font,
        "\u03c6 / CNNC (deg)",
        (plot_l + plot_r) / 2,
        plot_b + 28,
        14,
        INK,
        align="center",
        valign="top",
    )

    # series — adjacent both-converged neighbors only; straight segments; no wrap
    for (a, da), (b, db) in zip(pts, pts[1:]):
        line(rgb, X(a), Y(da), X(b), Y(db), SERIES, 2.15)
    for phi, de in pts:
        circle(rgb, X(phi), Y(de), 5.1, SERIES, fill=True)

    # point labels (from file values, 2 decimals)
    # offsets chosen so they miss the crossing hairline and each other
    label_off = {
        90: (10, 12, "left"),      # right of marker, above (still negative)
        105: (9, -11, "left"),     # right of marker, above
        120: (-9, -11, "right"),   # left of marker
        135: (-9, 12, "right"),    # left of marker, below so it stays in-pad
    }
    for phi, de in pts:
        dx, dy, al = label_off[int(phi)]
        text(
            rgb,
            font,
            fmt_delta(de),
            X(phi) + dx,
            Y(de) + dy,
            12,
            INK,
            align=al,
            valign="middle",
        )

    # ONE interpolant: 90–105 pair, y = 0 on that segment. Not 110°.
    # Hairline from the interpolant down to a short label, off the markers.
    xcp, ycp = X(xc), Y(0.0)
    line(rgb, xcp, ycp, xcp, ycp + 16, ZERO_C, 0.85)
    text(
        rgb,
        font,
        f"{xc:.2f}\u00b0",
        xcp + 4,
        ycp + 28,
        12,
        INK,
        align="center",
        valign="top",
    )

    return rgb


def main():
    metrics = load_metrics(METRICS_PATH)
    print("points (from results/bayes-metrics.json):")
    for phi, de in metrics["points"]:
        print(f"  phi={phi:g}  deltaE_kJmol={de}")
    print(f"interpolant phi={metrics['crossing_phi']}  label={metrics['crossing_phi']:.2f}°")
    print("pairs with a drawn crossing: 90–105 only; 110° not marked")
    rgb = render(metrics)
    if rgb.shape[1] != W or rgb.shape[0] != H:
        raise SystemExit(f"bad size {rgb.shape}")
    write_png(OUT_HERO, rgb)
    shutil.copy2(OUT_HERO, OUT_EASY)
    print(f"wrote {OUT_HERO} {W}x{H}")
    print(f"copied {OUT_EASY}")


if __name__ == "__main__":
    main()

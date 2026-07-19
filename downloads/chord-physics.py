#!/usr/bin/env python3
"""Generate the figures and synthetic audio for "What a Chord Looks Like".

The script uses only NumPy, Pillow, and the Python standard library. It has no
external data inputs and no random component.
"""

from __future__ import annotations

import math
import platform
import struct
import sys
import wave
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "images"
DOWNLOADS = ROOT / "downloads"

SR = 44_100
C4 = 440.0 * 2.0 ** (-9.0 / 12.0)
EB4 = 440.0 * 2.0 ** (-6.0 / 12.0)
E4 = 440.0 * 2.0 ** (-5.0 / 12.0)
G4 = 440.0 * 2.0 ** (-2.0 / 12.0)
NONLINEAR_ALPHA = 0.15
NONLINEAR_BETA = 0.10
AUDITION_RMS = 0.17
AUDITION_PEAK = 0.88

INK = "#1a1d2b"
DEEP = "#2f417a"
INDIGO = "#465c9b"
LIFTED = "#8fa5e3"
TEAL = "#6f9e9c"
GOLD = "#c89b55"
CREAM = "#fbfaf6"
GRID = "#d9d5cc"
WHITE = "#ffffff"

FONT_REGULAR_PATHS = (
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
)
FONT_BOLD_PATHS = (
    Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
)


def _font(paths: tuple[Path, ...], size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in paths:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


FONT_SMALL = _font(FONT_REGULAR_PATHS, 18)
FONT_LABEL = _font(FONT_REGULAR_PATHS, 22)
FONT_LEGEND = _font(FONT_REGULAR_PATHS, 18)
FONT_BOLD = _font(FONT_BOLD_PATHS, 20)


def note_frequency(semitones_from_a4: int) -> float:
    return 440.0 * 2.0 ** (semitones_from_a4 / 12.0)


def sine(frequency: float, duration: float, phase: float = 0.0) -> np.ndarray:
    t = np.arange(round(SR * duration), dtype=np.float64) / SR
    return np.sin(2.0 * np.pi * frequency * t + phase)


def harmonic_tone(
    frequency: float,
    duration: float,
    partials: int = 8,
    rolloff: float = 1.2,
) -> np.ndarray:
    t = np.arange(round(SR * duration), dtype=np.float64) / SR
    signal = np.zeros_like(t)
    for harmonic in range(1, partials + 1):
        signal += harmonic ** (-rolloff) * np.sin(
            2.0 * np.pi * harmonic * frequency * t
        )
    peak = np.max(np.abs(signal))
    return signal / peak if peak else signal


def listening_envelope(length: int) -> np.ndarray:
    t = np.arange(length, dtype=np.float64) / SR
    attack = 1.0 - np.exp(-t / 0.012)
    decay = np.exp(-t / 2.8)
    envelope = attack * decay
    fade = min(round(0.08 * SR), length)
    envelope[-fade:] *= np.linspace(1.0, 0.0, fade)
    return envelope


def normalize(signal: np.ndarray, peak: float = 0.88) -> np.ndarray:
    maximum = float(np.max(np.abs(signal)))
    return signal if maximum == 0.0 else signal * (peak / maximum)


def normalize_rms(
    signal: np.ndarray,
    target_rms: float = AUDITION_RMS,
    peak_ceiling: float = AUDITION_PEAK,
) -> np.ndarray:
    """Set audition level without changing ratios within a product layer."""
    rms = float(np.sqrt(np.mean(np.square(signal))))
    if rms == 0.0:
        return signal
    scaled = signal * (target_rms / rms)
    maximum = float(np.max(np.abs(scaled)))
    return scaled if maximum <= peak_ceiling else scaled * (peak_ceiling / maximum)


def chord(
    frequencies: tuple[float, ...],
    duration: float,
    harmonic: bool,
) -> np.ndarray:
    voices = [
        harmonic_tone(frequency, duration) if harmonic else sine(frequency, duration)
        for frequency in frequencies
    ]
    return normalize(np.sum(voices, axis=0))


def spectrum(signal: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    window = np.hanning(signal.size)
    magnitude = np.abs(np.fft.rfft(signal * window))
    maximum = float(np.max(magnitude))
    if maximum:
        magnitude /= maximum
    frequency = np.fft.rfftfreq(signal.size, d=1.0 / SR)
    return frequency, magnitude


def db(magnitude: np.ndarray, floor: float = -60.0) -> np.ndarray:
    values = 20.0 * np.log10(np.maximum(magnitude, 10.0 ** (floor / 20.0)))
    return np.maximum(values, floor)


def write_wav(path: Path, signal: np.ndarray, peak_normalize: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = normalize(signal) if peak_normalize else signal
    pcm = np.asarray(np.round(rendered * 32767.0), dtype="<i2")
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SR)
        handle.writeframes(pcm.tobytes())


@dataclass
class Plot:
    draw: ImageDraw.ImageDraw
    box: tuple[int, int, int, int]
    xlim: tuple[float, float]
    ylim: tuple[float, float]

    def point(self, x: float, y: float) -> tuple[float, float]:
        left, top, right, bottom = self.box
        px = left + (x - self.xlim[0]) / (self.xlim[1] - self.xlim[0]) * (right - left)
        py = bottom - (y - self.ylim[0]) / (self.ylim[1] - self.ylim[0]) * (bottom - top)
        return px, py

    def axes(
        self,
        xticks: list[float],
        yticks: list[float],
        xlabel: str,
        ylabel: str,
        xformat=lambda value: f"{value:g}",
        yformat=lambda value: f"{value:g}",
        yticklabels: list[str] | None = None,
    ) -> None:
        left, top, right, bottom = self.box
        for value in xticks:
            x, _ = self.point(value, self.ylim[0])
            self.draw.line((x, top, x, bottom), fill=GRID, width=1)
            self.draw.line((x, bottom, x, bottom + 7), fill=INK, width=2)
            self.draw.text((x, bottom + 11), xformat(value), fill=INK, font=FONT_SMALL, anchor="ma")
        for index, value in enumerate(yticks):
            _, y = self.point(self.xlim[0], value)
            self.draw.line((left, y, right, y), fill=GRID, width=1)
            self.draw.line((left - 7, y, left, y), fill=INK, width=2)
            label = yticklabels[index] if yticklabels else yformat(value)
            self.draw.text((left - 11, y), label, fill=INK, font=FONT_SMALL, anchor="rm")
        self.draw.rectangle(self.box, outline=INK, width=2)
        self.draw.text(((left + right) / 2, bottom + 47), xlabel, fill=INK, font=FONT_LABEL, anchor="ma")
        label_layer = Image.new("RGBA", (bottom - top + 100, 42), (0, 0, 0, 0))
        label_draw = ImageDraw.Draw(label_layer)
        label_draw.text((label_layer.width / 2, 21), ylabel, fill=INK, font=FONT_LABEL, anchor="mm")
        rotated = label_layer.rotate(90, expand=True, resample=Image.Resampling.BICUBIC)
        x = left - 82
        y = (top + bottom - rotated.height) / 2
        self.draw._image.paste(rotated, (round(x), round(y)), rotated)

    def line(
        self,
        x: np.ndarray,
        y: np.ndarray,
        color: str,
        width: int = 3,
        max_points: int = 2400,
    ) -> None:
        if x.size > max_points:
            indices = np.linspace(0, x.size - 1, max_points).astype(int)
            x = x[indices]
            y = y[indices]
        points = [self.point(float(xv), float(yv)) for xv, yv in zip(x, y)]
        self.draw.line(points, fill=color, width=width, joint="curve")

    def segment(self, x1: float, y1: float, x2: float, y2: float, color: str, width: int = 3) -> None:
        self.draw.line((*self.point(x1, y1), *self.point(x2, y2)), fill=color, width=width)

    def callout(self, label: str, x: float, y: float) -> None:
        px, py = self.point(x, y)
        radius = 16
        self.draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=INK, outline=WHITE, width=2)
        self.draw.text((px, py + 1), label, fill=WHITE, font=FONT_BOLD, anchor="mm")

    def legend(self, entries: list[tuple[str, str]], x: int | None = None, y: int | None = None) -> None:
        left, top, right, _ = self.box
        start_x = x if x is not None else right - 170
        start_y = y if y is not None else top + 14
        for index, (label, color) in enumerate(entries):
            yy = start_y + 27 * index
            self.draw.line((start_x, yy, start_x + 27, yy), fill=color, width=4)
            self.draw.text((start_x + 36, yy), label, fill=INK, font=FONT_LEGEND, anchor="lm")


def canvas(width: int, height: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (width, height), CREAM)
    return image, ImageDraw.Draw(image)


def save(image: Image.Image, filename: str, expected: tuple[int, int]) -> None:
    if image.size != expected:
        raise RuntimeError(f"unexpected image size for {filename}: {image.size}")
    path = IMAGES / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True)
    print(f"wrote {path}")


def figure_one() -> None:
    image, draw = canvas(1200, 630)
    duration = 1.0
    signal = sine(440.0, duration)
    time = np.arange(signal.size) / SR
    frequency, magnitude = spectrum(signal)

    left = Plot(draw, (100, 55, 565, 535), (0.0, 10.0), (-1.15, 1.15))
    left.axes([0, 2, 4, 6, 8, 10], [-1, 0, 1], "Time (ms)", "Pressure (relative)")
    keep = time <= 0.010
    left.line(time[keep] * 1000.0, signal[keep], DEEP, width=4)
    left.callout("A", 0.65, 0.92)

    right = Plot(draw, (690, 55, 1155, 535), (0.0, 900.0), (0.0, 1.05))
    right.axes([0, 220, 440, 660, 880], [0, 0.5, 1.0], "Frequency (Hz)", "Magnitude (relative)")
    keep = frequency <= 900.0
    right.line(frequency[keep], magnitude[keep], INDIGO, width=4)
    right.callout("B", 440.0, 0.91)

    save(image, "2026-07-19-what-a-chord-looks-like-hero.png", (1200, 630))


def figure_two() -> None:
    image, draw = canvas(1200, 820)
    duration = 1.0
    pure = sine(220.0, duration)
    rich = harmonic_tone(220.0, duration)
    time = np.arange(pure.size) / SR
    f_pure, m_pure = spectrum(pure)
    f_rich, m_rich = spectrum(rich)

    plots = [
        Plot(draw, (95, 50, 565, 345), (0.0, 18.0), (-1.15, 1.15)),
        Plot(draw, (690, 50, 1160, 345), (0.0, 18.0), (-1.15, 1.15)),
        Plot(draw, (95, 455, 565, 750), (0.0, 1900.0), (0.0, 1.05)),
        Plot(draw, (690, 455, 1160, 750), (0.0, 1900.0), (0.0, 1.05)),
    ]
    for plot in plots[:2]:
        plot.axes([0, 6, 12, 18], [-1, 0, 1], "Time (ms)", "Pressure (relative)")
    for plot in plots[2:]:
        plot.axes([0, 440, 880, 1320, 1760], [0, 0.5, 1.0], "Frequency (Hz)", "Magnitude (relative)")

    keep_t = time <= 0.018
    plots[0].line(time[keep_t] * 1000.0, pure[keep_t], DEEP, width=4)
    plots[1].line(time[keep_t] * 1000.0, rich[keep_t], INDIGO, width=4)
    keep_f = f_pure <= 1900.0
    plots[2].line(f_pure[keep_f], m_pure[keep_f], DEEP, width=4)
    plots[3].line(f_rich[keep_f], m_rich[keep_f], INDIGO, width=4)
    for label, plot, xy in zip("ABCD", plots, [(1.2, 0.9), (1.2, 0.9), (220, 0.9), (220, 0.9)]):
        plot.callout(label, *xy)

    save(image, "2026-07-19-what-a-chord-looks-like-harmonics.png", (1200, 820))


def figure_three() -> None:
    image, draw = canvas(1200, 700)
    duration = 1.0
    frequencies = (C4, E4, G4)
    voices = [sine(value, duration) for value in frequencies]
    mixed = normalize(np.sum(voices, axis=0))
    rich = chord(frequencies, duration, harmonic=True)
    time = np.arange(mixed.size) / SR
    frequency, magnitude = spectrum(rich)

    left = Plot(draw, (120, 55, 610, 610), (0.0, 20.0), (-3.8, 3.8))
    left.axes(
        [0, 5, 10, 15, 20],
        [-3, -1, 1, 3],
        "Time (ms)",
        "Component and sum",
        yticklabels=["Sum", "G4", "E4", "C4"],
    )
    keep = time <= 0.020
    colors = (DEEP, INDIGO, TEAL)
    offsets = (3.0, 1.0, -1.0)
    for voice, color, offset in zip(voices, colors, offsets):
        left.line(time[keep] * 1000.0, 0.64 * voice[keep] + offset, color, width=3)
    left.line(time[keep] * 1000.0, 0.95 * mixed[keep] - 3.0, INK, width=4)
    left.callout("A", 0.9, 3.5)

    right = Plot(draw, (735, 55, 1160, 610), (0.0, 2500.0), (-60.0, 2.0))
    right.axes([0, 500, 1000, 1500, 2000, 2500], [-60, -40, -20, 0], "Frequency (Hz)", "Magnitude (dB)")
    keep = frequency <= 2500.0
    right.line(frequency[keep], db(magnitude[keep]), INDIGO, width=3)
    right.callout("B", C4, -5.5)

    save(image, "2026-07-19-what-a-chord-looks-like-chord.png", (1200, 700))


def figure_four() -> None:
    image, draw = canvas(1200, 780)
    duration = 1.0
    major = chord((C4, E4, G4), duration, harmonic=True)
    minor = chord((C4, EB4, G4), duration, harmonic=True)
    f_major, m_major = spectrum(major)
    f_minor, m_minor = spectrum(minor)

    upper = Plot(draw, (105, 50, 1160, 330), (0.0, 2500.0), (-60.0, 2.0))
    lower = Plot(draw, (105, 420, 1160, 690), (0.0, 2500.0), (-60.0, 2.0))
    for plot in (upper, lower):
        plot.axes([0, 500, 1000, 1500, 2000, 2500], [-60, -40, -20, 0], "Frequency (Hz)", "Magnitude (dB)")
    keep = f_major <= 2500.0
    upper.line(f_major[keep], db(m_major[keep]), DEEP, width=3)
    lower.line(f_minor[keep], db(m_minor[keep]), INDIGO, width=3)
    upper.legend([("C major", DEEP)], x=950, y=75)
    lower.legend([("C minor", INDIGO)], x=950, y=445)
    upper.callout("A", E4, -6.0)
    lower.callout("B", EB4, -6.0)

    save(image, "2026-07-19-what-a-chord-looks-like-major-minor.png", (1200, 780))


def figure_five() -> None:
    image, draw = canvas(1200, 630)
    duration = 2.0
    first = sine(440.0, duration)
    second = sine(442.0, duration)
    mixed = 0.5 * (first + second)
    time = np.arange(mixed.size) / SR
    frequency, magnitude = spectrum(mixed)
    envelope = np.abs(np.cos(np.pi * 2.0 * time))

    left = Plot(draw, (95, 55, 585, 535), (0.0, 1.0), (-1.15, 1.15))
    left.axes([0, 0.25, 0.5, 0.75, 1.0], [-1, 0, 1], "Time (s)", "Pressure (relative)")
    keep = time <= 1.0
    left.line(time[keep], mixed[keep], DEEP, width=2, max_points=5000)
    left.line(time[keep], envelope[keep], TEAL, width=4)
    left.line(time[keep], -envelope[keep], TEAL, width=4)
    left.callout("A", 0.5, 0.08)

    right = Plot(draw, (710, 55, 1160, 535), (436.0, 446.0), (0.0, 1.05))
    right.axes([436, 438, 440, 442, 444, 446], [0, 0.5, 1.0], "Frequency (Hz)", "Magnitude (relative)")
    keep = (frequency >= 436.0) & (frequency <= 446.0)
    right.line(frequency[keep], magnitude[keep], INDIGO, width=4)
    right.callout("B", 441.0, 0.88)

    save(image, "2026-07-19-what-a-chord-looks-like-beats.png", (1200, 630))


def figure_nonlinearity() -> None:
    """Plot the exact line spectra added by quadratic and cubic mixing."""
    image, draw = canvas(1200, 920)
    alpha = NONLINEAR_ALPHA
    beta = NONLINEAR_BETA
    floor = -36.0

    linear = Plot(draw, (110, 55, 1160, 250), (0.0, 1050.0), (floor, 2.0))
    quadratic = Plot(draw, (110, 345, 1160, 540), (0.0, 1050.0), (floor, 2.0))
    cubic = Plot(draw, (110, 635, 1160, 830), (0.0, 1050.0), (floor, 2.0))

    ticks = [0, 200, 400, 600, 800, 1000]
    yticks = [-30, -20, -10, 0]
    linear.axes(ticks, yticks, "", "Magnitude (dB)", xformat=lambda _: "")
    quadratic.axes(ticks, yticks, "", "Magnitude (dB)", xformat=lambda _: "")
    cubic.axes(ticks, yticks, "Frequency (Hz)", "Magnitude (dB)")

    def level(amplitude: float) -> float:
        return 20.0 * math.log10(abs(amplitude))

    def stem(plot: Plot, frequency: float, amplitude: float, color: str) -> float:
        magnitude = level(amplitude)
        plot.segment(frequency, floor, frequency, magnitude, color, width=6)
        return magnitude

    def label(plot: Plot, frequency: float, magnitude: float, text: str, offset: int = -9) -> None:
        x, y = plot.point(frequency, magnitude)
        draw.text((x, y + offset), text, fill=INK, font=FONT_SMALL, anchor="ms")

    for frequency, text in ((C4, "C4"), (E4, "E4")):
        magnitude = stem(linear, frequency, 1.0, DEEP)
        label(linear, frequency, magnitude, text, offset=36)
    linear.legend([("input", DEEP)], x=965, y=82)
    linear.callout("A", 42.0, -5.0)

    quadratic_products = (
        (E4 - C4, alpha, "E - C"),
        (2.0 * C4, 0.5 * alpha, "2C"),
        (C4 + E4, alpha, "C + E"),
        (2.0 * E4, 0.5 * alpha, "2E"),
    )
    for frequency, amplitude, text in quadratic_products:
        magnitude = stem(quadratic, frequency, amplitude, GOLD)
        label(quadratic, frequency, magnitude, text)
    quadratic.legend([("quadratic products", GOLD)], x=890, y=372)
    quadratic.callout("B", 42.0, -5.0)

    cubic_products = (
        (2.0 * C4 - E4, 0.75 * beta, "2C - E"),
        (2.0 * E4 - C4, 0.75 * beta, "2E - C"),
        (3.0 * C4, 0.25 * beta, "3C"),
        (2.0 * C4 + E4, 0.75 * beta, "2C + E"),
        (C4 + 2.0 * E4, 0.75 * beta, "C + 2E"),
        (3.0 * E4, 0.25 * beta, "3E"),
    )
    for frequency, amplitude, text in cubic_products:
        magnitude = stem(cubic, frequency, amplitude, TEAL)
        label(cubic, frequency, magnitude, text)
    cubic.legend([("cubic products", TEAL)], x=910, y=662)
    cubic.callout("C", 42.0, -5.0)

    save(image, "2026-07-19-what-a-chord-looks-like-nonlinearity.png", (1200, 920))


def figure_six() -> None:
    image, draw = canvas(1200, 630)
    just_g = 1.5 * C4
    c_third = 3.0 * C4
    just_g_second = 2.0 * just_g
    equal_g_second = 2.0 * G4
    delta = equal_g_second - c_third

    left = Plot(draw, (105, 55, 585, 535), (781.0, 788.0), (0.0, 1.08))
    left.axes([781, 783, 785, 787], [0, 0.5, 1.0], "Frequency (Hz)", "Partial magnitude")
    left.segment(c_third, 0.0, c_third, 1.0, DEEP, width=7)
    left.segment(just_g_second, 0.0, just_g_second, 0.78, TEAL, width=3)
    left.segment(equal_g_second, 0.0, equal_g_second, 0.78, GOLD, width=6)
    left.legend([("C x 3", DEEP), ("just G x 2", TEAL), ("12-TET G x 2", GOLD)], x=410, y=88)
    left.callout("A", c_third, 0.93)

    right = Plot(draw, (710, 55, 1160, 535), (0.0, 6.0), (-6.0, 0.2))
    right.axes([0, 1, 2, 3, 4, 5, 6], [-6, -4, -2, 0], "Time (s)", "Phase offset (cycles)")
    time = np.linspace(0.0, 6.0, 800)
    phase_cycles = delta * time
    right.line(time, phase_cycles, GOLD, width=4)
    right.segment(0.0, 0.0, 6.0, 0.0, TEAL, width=3)
    right.legend([("12-TET fifth", GOLD), ("just fifth", TEAL)], x=905, y=88)
    right.callout("B", 4.5, float(delta * 4.5))

    save(image, "2026-07-19-what-a-chord-looks-like-fifth.png", (1200, 630))


def audio_files() -> None:
    duration = 3.0
    pure = chord((C4, E4, G4), duration, harmonic=False)
    rich = chord((C4, E4, G4), duration, harmonic=True)
    beats = normalize(0.5 * (sine(440.0, duration) + sine(442.0, duration)))
    envelope = listening_envelope(pure.size)
    write_wav(DOWNLOADS / "what-a-chord-looks-like-c-major-pure.wav", pure * envelope)
    write_wav(DOWNLOADS / "what-a-chord-looks-like-c-major-harmonic.wav", rich * envelope)
    write_wav(DOWNLOADS / "what-a-chord-looks-like-beats.wav", beats * envelope)

    time = np.arange(round(SR * duration), dtype=np.float64) / SR
    c_phase = 2.0 * np.pi * C4 * time
    e_phase = 2.0 * np.pi * E4 * time
    two_tone = np.sin(c_phase) + np.sin(e_phase)
    quadratic_products = (
        -0.5 * np.cos(2.0 * c_phase)
        - 0.5 * np.cos(2.0 * e_phase)
        + np.cos(c_phase - e_phase)
        - np.cos(c_phase + e_phase)
    )
    cubic_products = (
        -0.25 * np.sin(3.0 * c_phase)
        - 0.25 * np.sin(3.0 * e_phase)
        - 0.75 * np.sin(2.0 * c_phase + e_phase)
        - 0.75 * np.sin(c_phase + 2.0 * e_phase)
        + 0.75 * np.sin(2.0 * c_phase - e_phase)
        + 0.75 * np.sin(2.0 * e_phase - c_phase)
    )
    nonlinear_layers = (
        ("what-a-chord-looks-like-intermod-input.wav", two_tone),
        ("what-a-chord-looks-like-quadratic-products.wav", quadratic_products),
        ("what-a-chord-looks-like-cubic-products.wav", cubic_products),
    )
    for filename, signal in nonlinear_layers:
        audible = normalize_rms(signal * envelope)
        write_wav(DOWNLOADS / filename, audible, peak_normalize=False)
    print("wrote synthetic WAV demonstrations")


def main() -> None:
    figure_one()
    figure_two()
    figure_three()
    figure_four()
    figure_five()
    figure_nonlinearity()
    figure_six()
    audio_files()

    just_g = 1.5 * C4
    partial_gap = abs(2.0 * G4 - 3.0 * C4)
    print(f"python={platform.python_version()} platform={platform.machine()} numpy={np.__version__}")
    print(f"C4={C4:.6f} Hz Eb4={EB4:.6f} Hz E4={E4:.6f} Hz G4={G4:.6f} Hz")
    print(
        f"nonlinear_alpha={NONLINEAR_ALPHA:.2f} nonlinear_beta={NONLINEAR_BETA:.2f} "
        f"audition_rms={AUDITION_RMS:.2f} audition_peak={AUDITION_PEAK:.2f}"
    )
    print(
        "quadratic_products_Hz="
        f"{E4 - C4:.6f},{2.0 * C4:.6f},{C4 + E4:.6f},{2.0 * E4:.6f}"
    )
    print(
        "cubic_products_Hz="
        f"{2.0 * C4 - E4:.6f},{2.0 * E4 - C4:.6f},{3.0 * C4:.6f},"
        f"{2.0 * C4 + E4:.6f},{C4 + 2.0 * E4:.6f},{3.0 * E4:.6f}"
    )
    print(f"just_G4={just_g:.6f} Hz equal_minus_just={G4 - just_g:.6f} Hz")
    print(f"second_G_minus_third_C={2.0 * G4 - 3.0 * C4:.6f} Hz magnitude={partial_gap:.6f} Hz")


if __name__ == "__main__":
    main()

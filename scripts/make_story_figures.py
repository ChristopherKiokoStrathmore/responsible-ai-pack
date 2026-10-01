"""Draw the README story figures from the committed reports.

Numbers and bar lengths come from reports/*.json. Those files are the
output of scripts/run_all.py on the pinned churn model. This script does
not invent a metric and does not retrain anything.

Fonts: Fraunces and Inter Tight, downloaded from the Google Fonts repo.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
ASSETS = ROOT / "assets"
FONT_CACHE = Path("/tmp/story-fonts")

CREAM = (247, 244, 236, 255)
WHITE = (255, 253, 248, 255)
GREEN = (11, 61, 46, 255)
GREEN_MID = (27, 107, 78, 255)
GREEN_SOFT = (226, 236, 229, 255)
GOLD = (200, 150, 46, 255)
GOLD_SOFT = (244, 232, 196, 255)
INK = (22, 40, 34, 255)
MUTED = (90, 107, 99, 255)
LINE = (226, 216, 196, 255)
TRACK = (236, 230, 216, 255)
GRAY = (196, 188, 172, 255)

CREAM_HEX = "#F7F4EC"
WHITE_HEX = "#FFFDF8"
GREEN_HEX = "#0B3D2E"
GREEN_MID_HEX = "#1B6B4E"
GOLD_HEX = "#C8962E"
MUTED_HEX = "#5A6B63"
LINE_HEX = "#E2D8C4"
INK_HEX = "#162822"

FRAUNCES_URL = (
    "https://github.com/google/fonts/raw/main/ofl/fraunces/"
    "Fraunces%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf"
)
INTER_URL = (
    "https://github.com/google/fonts/raw/main/ofl/intertight/"
    "InterTight%5Bwght%5D.ttf"
)


def _download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 1000:
        return
    request = urllib.request.Request(url, headers={"User-Agent": "responsible-ai-pack"})
    with urllib.request.urlopen(request, timeout=120) as response:
        dest.write_bytes(response.read())


def ensure_fonts() -> dict[str, Path]:
    variable = {
        "fraunces": FONT_CACHE / "Fraunces.ttf",
        "inter": FONT_CACHE / "InterTight.ttf",
    }
    _download(FRAUNCES_URL, variable["fraunces"])
    _download(INTER_URL, variable["inter"])
    from fontTools.ttLib import TTFont
    from fontTools.varLib.instancer import instantiateVariableFont

    baked = {
        "Fraunces-Bold.ttf": ("fraunces", {"opsz": 144, "wght": 680, "SOFT": 30, "WONK": 0}),
        "Fraunces-Semibold.ttf": ("fraunces", {"opsz": 72, "wght": 600, "SOFT": 20, "WONK": 0}),
        "InterTight-Regular.ttf": ("inter", {"wght": 430}),
        "InterTight-Medium.ttf": ("inter", {"wght": 520}),
        "InterTight-Semibold.ttf": ("inter", {"wght": 640}),
    }
    paths = dict(variable)
    for name, (source, axes) in baked.items():
        dest = FONT_CACHE / name
        if not dest.is_file():
            font = TTFont(variable[source])
            instantiateVariableFont(font, axes, inplace=False).save(dest)
        paths[name] = dest
        font_manager.fontManager.addfont(str(dest))
    return paths


def load_reports() -> dict:
    fairness = json.loads((REPORTS / "fairness.json").read_text())
    metrics = json.loads((REPORTS / "metrics_recomputed.json").read_text())
    gates = json.loads((REPORTS / "gate_check.json").read_text())
    drift = json.loads((REPORTS / "drift_psi.json").read_text())
    return {
        "fairness": fairness,
        "metrics": metrics,
        "gates": gates,
        "drift": drift,
    }


def _gate(gates: dict, name: str) -> float:
    for row in gates["metrics"]:
        if row["metric"] == name:
            return float(row["gate"])
    raise KeyError(name)


class Board:
    """Logical-pixel canvas, rasterized at a higher scale and then resized."""

    def __init__(self, width: int, height: int, scale: int = 2, background=CREAM):
        self.w = width
        self.h = height
        self.s = scale
        self.im = Image.new("RGBA", (width * scale, height * scale), background)
        self.draw = ImageDraw.Draw(self.im)
        self.fonts: dict[tuple, ImageFont.FreeTypeFont] = {}
        self.boxes: list[tuple[float, float, float, float]] = []
        self.paths = ensure_fonts()

    def _font(self, file_name: str, size: float) -> ImageFont.FreeTypeFont:
        key = (file_name, round(size * self.s, 2))
        if key not in self.fonts:
            self.fonts[key] = ImageFont.truetype(str(self.paths[file_name]), size=key[1])
        return self.fonts[key]

    def display(self, size: float) -> ImageFont.FreeTypeFont:
        return self._font("Fraunces-Bold.ttf", size)

    def display_semi(self, size: float) -> ImageFont.FreeTypeFont:
        return self._font("Fraunces-Semibold.ttf", size)

    def sans(self, size: float, weight: str = "medium") -> ImageFont.FreeTypeFont:
        file_name = {
            "regular": "InterTight-Regular.ttf",
            "medium": "InterTight-Medium.ttf",
            "semibold": "InterTight-Semibold.ttf",
        }[weight]
        return self._font(file_name, size)

    def track(self, box: tuple[float, float, float, float]) -> None:
        self.boxes.append(box)

    def _xy(self, x: float, y: float) -> tuple[float, float]:
        return (x * self.s, y * self.s)

    def _box(self, box: tuple[float, float, float, float]) -> list[float]:
        x0, y0, x1, y1 = box
        return [x0 * self.s, y0 * self.s, x1 * self.s, y1 * self.s]

    def rect(self, box, radius: float, fill, outline=None, width: float = 1) -> None:
        self.track(box)
        self.draw.rounded_rectangle(
            self._box(box),
            radius=radius * self.s,
            fill=fill,
            outline=outline,
            width=max(1, int(round(width * self.s))),
        )

    def line(self, start, end, fill, width: float = 2) -> None:
        self.draw.line([self._xy(*start), self._xy(*end)], fill=fill, width=max(1, int(round(width * self.s))))

    def ellipse(self, box, fill=None, outline=None, width: float = 1) -> None:
        self.draw.ellipse(
            self._box(box),
            fill=fill,
            outline=outline,
            width=max(1, int(round(width * self.s))),
        )

    def polygon(self, points, fill) -> None:
        self.draw.polygon([self._xy(x, y) for x, y in points], fill=fill)

    def length(self, text: str, font) -> float:
        return self.draw.textlength(text, font=font, features=["lnum", "tnum"]) / self.s

    def text(self, xy, text: str, font, fill, anchor: str = "lt") -> None:
        self.draw.text(
            self._xy(*xy),
            text,
            font=font,
            fill=fill,
            anchor=anchor,
            features=["lnum", "tnum"],
        )

    def wrapped(self, xy, text: str, font, fill, max_width: float, line_gap: float) -> float:
        words = text.split()
        lines: list[str] = []
        current = ""
        for word in words:
            trial = word if not current else f"{current} {word}"
            if self.length(trial, font) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        x, y = xy
        for line in lines:
            self.text((x, y), line, font, fill)
            y += line_gap
        return y

    def save(self, path: Path, size: tuple[int, int]) -> None:
        image = self.im.resize(size, Image.Resampling.LANCZOS)
        rgb = Image.new("RGB", size, (CREAM[0], CREAM[1], CREAM[2]))
        rgb.paste(image, mask=image.split()[-1])
        path.parent.mkdir(parents=True, exist_ok=True)
        rgb.save(path, "PNG", optimize=True)


def fmt(value: float, places: int) -> str:
    return f"{value:.{places}f}"


def person(board: Board, cx: float, cy: float, color, scale: float = 1.0) -> None:
    """A plain head-and-shoulders mark. No face, no stock art."""
    head = 14 * scale
    stroke = max(1.6, 2.4 * scale)
    body_w = 22 * scale
    body_h = 28 * scale
    body_top = cy + head * 0.45
    board.rect(
        (cx - body_w, body_top, cx + body_w, body_top + body_h),
        radius=12 * scale,
        fill=GREEN_SOFT,
        outline=color,
        width=stroke,
    )
    board.ellipse(
        (cx - head, cy - head, cx + head, cy + head),
        fill=GREEN_SOFT,
        outline=color,
        width=stroke,
    )


def h_arrow(board: Board, x0: float, x1: float, y: float) -> None:
    board.line((x0, y), (x1 - 12, y), GOLD, width=3)
    board.polygon([(x1 - 14, y - 7), (x1, y), (x1 - 14, y + 7)], GOLD)


def selection_column(board: Board, x: float, y: float, width: float, label: str, rows: int, rate: float, accent) -> None:
    cx = x + width / 2
    person(board, cx, y + 28, GREEN, scale=1.05)
    board.text((cx, y + 108), fmt(rate, 3), board.display(46), accent, anchor="mt")
    board.text((cx, y + 162), "selected", board.sans(16, "medium"), MUTED, anchor="mt")
    track_w = width - 28
    track_x = x + 14
    track_y = y + 192
    board.rect((track_x, track_y, track_x + track_w, track_y + 14), radius=7, fill=TRACK)
    fill_w = max(8, track_w * rate)
    board.rect((track_x, track_y, track_x + fill_w, track_y + 14), radius=7, fill=accent)
    board.text((cx, y + 218), label, board.sans(16, "semibold"), GREEN, anchor="mt")
    board.text((cx, y + 240), f"{rows} rows", board.sans(15, "regular"), MUTED, anchor="mt")


def draw_hero(data: dict, path: Path) -> None:
    fairness = data["fairness"]
    metrics = data["metrics"]
    gates = data["gates"]
    senior = fairness["by_field"]["SeniorCitizen"]["groups"]
    gender = fairness["by_field"]["gender"]["groups"]
    senior_gap = fairness["by_field"]["SeniorCitizen"]["demographic_parity_difference"]
    roc = metrics["churn_models"]["gradient_boosting"]["roc_auc"]
    roc_floor = _gate(gates, "roc_auc")
    fpr = {
        "SeniorCitizen 0": senior["0"]["false_positive_rate"],
        "SeniorCitizen 1": senior["1"]["false_positive_rate"],
        "Female": gender["Female"]["false_positive_rate"],
        "Male": gender["Male"]["false_positive_rate"],
    }

    board = Board(1600, 800, scale=2)
    board.text((48, 28), "RESPONSIBLE AI PACK", board.sans(15, "semibold"), GOLD)
    board.text((48, 52), "A churn score, checked before it is trusted", board.display(36), GREEN)
    board.text(
        (48, 100),
        "Public IBM telco sample. One held-out split. The pinned gradient boosting model.",
        board.sans(16, "regular"),
        MUTED,
    )

    cards = [(44, 455), (551, 498), (1101, 455)]
    top, height = 136, 612
    for x, width in cards:
        board.rect((x, top, x + width, top + height), radius=22, fill=WHITE, outline=LINE, width=1.5)

    arrow_y = top + height / 2
    h_arrow(board, 44 + 455 + 8, 551 - 8, arrow_y)
    h_arrow(board, 551 + 498 + 8, 1101 - 8, arrow_y)

    # Panel 1. The problem: selection rates differ for SeniorCitizen.
    x, width = cards[0]
    board.text((x + 28, top + 22), "01   PROBLEM", board.sans(15, "semibold"), GOLD)
    board.text((x + 28, top + 50), "Seniors are flagged", board.display(30), GREEN)
    board.text((x + 28, top + 88), "more often", board.display(30), GREEN)
    col_w = (width - 56) / 2
    selection_column(
        board,
        x + 20,
        top + 150,
        col_w,
        "SeniorCitizen 0",
        senior["0"]["n"],
        senior["0"]["selection_rate"],
        GREEN,
    )
    selection_column(
        board,
        x + 20 + col_w,
        top + 150,
        col_w,
        "SeniorCitizen 1",
        senior["1"]["n"],
        senior["1"]["selection_rate"],
        GOLD,
    )
    board.text((x + 28, top + 470), "Gender stays close", board.sans(16, "semibold"), GREEN)
    female = gender["Female"]["selection_rate"]
    male = gender["Male"]["selection_rate"]
    board.text(
        (x + 28, top + 496),
        f"Female {fmt(female, 3)}    Male {fmt(male, 3)}",
        board.sans(16, "medium"),
        MUTED,
    )
    bar_y = top + 522
    bar_w = width - 56
    for index, (name, rate) in enumerate((("Female", female), ("Male", male))):
        yy = bar_y + index * 30
        board.text((x + 28, yy - 1), name, board.sans(13, "medium"), MUTED)
        track_x = x + 92
        track_w = bar_w - 64
        board.rect((track_x, yy + 2, track_x + track_w, yy + 14), radius=6, fill=TRACK)
        board.rect((track_x, yy + 2, track_x + track_w * rate, yy + 14), radius=6, fill=GREEN_MID)
    board.text((x + 28, top + 584), "Share selected at P(Churn=Yes) > 0.5", board.sans(14, "regular"), MUTED)

    # Panel 2. The method: scripts/run_all.py, in that order.
    x, width = cards[1]
    board.text((x + 28, top + 22), "02   METHOD", board.sans(15, "semibold"), GOLD)
    board.text((x + 28, top + 50), "What run_all.py measures", board.display(28), GREEN)
    steps = [
        ("1", "Pin the model", "Saved gradient boosting pipeline"),
        ("2", "Score the holdout", "ROC-AUC, PR-AUC, top-decile lift"),
        ("3", "Fairlearn groups", "Gender and SeniorCitizen"),
        ("4", "TreeSHAP", "Global rank and three local scores"),
        ("5", "PSI drift", "Training split against the holdout"),
        ("6", "CI gates", "Three floors on the scoring model"),
    ]
    step_top = top + 112
    step_h = 78
    icon_cx = x + 52
    for index, (number, title, detail) in enumerate(steps):
        cy = step_top + index * step_h + 22
        if index < len(steps) - 1:
            board.line((icon_cx, cy + 18), (icon_cx, cy + step_h - 18), GOLD, width=2)
        board.ellipse((icon_cx - 16, cy - 16, icon_cx + 16, cy + 16), fill=GREEN)
        board.text((icon_cx, cy), number, board.sans(16, "semibold"), CREAM, anchor="mm")
        board.text((x + 84, cy - 16), title, board.sans(20, "semibold"), GREEN)
        board.text((x + 84, cy + 8), detail, board.sans(15, "regular"), MUTED)

    # Panel 3. The result: a passing quality gate, a visible senior gap, real FPR bars.
    x, width = cards[2]
    board.text((x + 28, top + 22), "03   RESULT", board.sans(15, "semibold"), GOLD)
    board.text((x + 28, top + 50), "Gates pass. The gap", board.display(28), GREEN)
    board.text((x + 28, top + 86), "stays visible.", board.display(28), GREEN)

    stat_y = top + 142
    left = x + 28
    right = x + width / 2 + 6
    board.text((left, stat_y), fmt(roc, 3), board.display(48), GREEN)
    board.text((left, stat_y + 58), "ROC-AUC", board.sans(16, "semibold"), GREEN)
    board.text((left, stat_y + 80), f"exact {fmt(roc, 6)}", board.sans(13, "regular"), MUTED)
    board.text((left, stat_y + 100), f"floor {fmt(roc_floor, 2)}  passed", board.sans(15, "semibold"), GREEN_MID)

    board.text((right, stat_y), fmt(senior_gap, 3), board.display(48), GOLD)
    board.text((right, stat_y + 58), "SeniorCitizen gap", board.sans(15, "semibold"), GREEN)
    board.text((right, stat_y + 80), f"exact {fmt(senior_gap, 6)}", board.sans(13, "regular"), MUTED)
    board.text((right, stat_y + 100), "flagged for review", board.sans(15, "semibold"), GOLD)

    chart_x = x + 28
    chart_y = top + 328
    chart_w = width - 118
    board.text((chart_x, chart_y), "False positive rate", board.sans(16, "semibold"), GREEN)
    max_fpr = max(fpr.values())
    scale = chart_w / (max_fpr * 1.18)
    for index, (label, value) in enumerate(fpr.items()):
        yy = chart_y + 34 + index * 58
        color = GOLD if label == "SeniorCitizen 1" else GREEN
        board.text((chart_x, yy), label, board.sans(15, "medium"), INK)
        bar_top = yy + 22
        board.rect((chart_x, bar_top, chart_x + chart_w, bar_top + 14), radius=7, fill=TRACK)
        board.rect((chart_x, bar_top, chart_x + max(8, value * scale), bar_top + 14), radius=7, fill=color)
        board.text((chart_x + chart_w + 10, bar_top - 1), fmt(value, 3), board.sans(15, "semibold"), color)

    board.text(
        (48, 768),
        "One split, one cutoff. Not a fairness certificate. SHAP explains the model. It does not cause churn.",
        board.sans(15, "regular"),
        MUTED,
    )
    board.save(path, (1600, 800))


def draw_social(data: dict, path: Path) -> None:
    fairness = data["fairness"]
    metrics = data["metrics"]
    gates = data["gates"]
    senior = fairness["by_field"]["SeniorCitizen"]["groups"]
    senior_gap = fairness["by_field"]["SeniorCitizen"]["demographic_parity_difference"]
    roc = metrics["churn_models"]["gradient_boosting"]["roc_auc"]
    roc_floor = _gate(gates, "roc_auc")

    board = Board(1280, 640, scale=2)
    # 40px is the safe edge. Content starts further in so antialiasing stays inside it.
    margin = 52
    board.text((margin, 44), "responsible-ai-pack", board.display(38), GREEN)
    board.text(
        (margin, 92),
        "A churn model is only useful if people can trust it.",
        board.sans(20, "medium"),
        INK,
    )

    top = 150
    height = 420
    gap = 26
    width = (1280 - margin * 2 - gap * 2) / 3
    xs = [margin + index * (width + gap) for index in range(3)]
    for index, x in enumerate(xs):
        board.rect((x, top, x + width, top + height), radius=18, fill=WHITE, outline=LINE, width=1.5)
        if index < 2:
            h_arrow(board, x + width + 4, x + width + gap - 4, top + height / 2)

    # Problem
    x = xs[0]
    board.text((x + 22, top + 18), "PROBLEM", board.sans(14, "semibold"), GOLD)
    board.text((x + 22, top + 44), "Seniors are flagged", board.display(24), GREEN)
    board.text((x + 22, top + 76), "more often", board.display(24), GREEN)
    col_w = (width - 36) / 2
    for offset, key, accent in ((0, "0", GREEN), (col_w, "1", GOLD)):
        cx = x + 18 + offset + col_w / 2
        rate = senior[key]["selection_rate"]
        person(board, cx, top + 148, GREEN, scale=0.85)
        board.text((cx, top + 214), fmt(rate, 3), board.display(32), accent, anchor="mt")
        board.text((cx, top + 254), f"Senior {key}", board.sans(14, "semibold"), GREEN, anchor="mt")
        board.text((cx, top + 276), "selected", board.sans(13, "regular"), MUTED, anchor="mt")
    board.text((x + 22, top + 308), "Share selected, same cutoff", board.sans(14, "regular"), MUTED)
    track_y = top + 336
    track_w = width - 44
    label_w = 74
    for index, key in enumerate(("0", "1")):
        yy = track_y + index * 34
        rate = senior[key]["selection_rate"]
        color = GREEN if key == "0" else GOLD
        board.text((x + 22, yy), f"Senior {key}", board.sans(13, "medium"), INK)
        bar_x = x + 22 + label_w
        bar_w = track_w - label_w
        board.rect((bar_x, yy + 2, bar_x + bar_w, yy + 14), radius=6, fill=TRACK)
        board.rect((bar_x, yy + 2, bar_x + bar_w * rate, yy + 14), radius=6, fill=color)

    # Method
    x = xs[1]
    board.text((x + 22, top + 18), "METHOD", board.sans(14, "semibold"), GOLD)
    board.text((x + 22, top + 44), "The real pipeline", board.display(24), GREEN)
    steps = [
        "Pin the model",
        "Score the holdout",
        "Fairlearn groups",
        "TreeSHAP",
        "PSI drift",
        "CI gates",
    ]
    for index, title in enumerate(steps):
        cy = top + 112 + index * 50
        board.ellipse((x + 28, cy, x + 56, cy + 28), fill=GREEN)
        board.text((x + 42, cy + 14), str(index + 1), board.sans(14, "semibold"), CREAM, anchor="mm")
        if index < len(steps) - 1:
            board.line((x + 42, cy + 30), (x + 42, cy + 48), GOLD, width=2)
        board.text((x + 70, cy + 3), title, board.sans(18, "semibold"), GREEN)

    # Result
    x = xs[2]
    board.text((x + 22, top + 18), "RESULT", board.sans(14, "semibold"), GOLD)
    board.text((x + 22, top + 44), "Gates pass.", board.display(24), GREEN)
    board.text((x + 22, top + 74), "The gap stays.", board.display(24), GREEN)
    board.text((x + 22, top + 124), fmt(roc, 3), board.display(36), GREEN)
    board.text((x + 22, top + 166), "ROC-AUC", board.sans(15, "semibold"), GREEN)
    board.text((x + 22, top + 188), f"floor {fmt(roc_floor, 2)} passed", board.sans(14, "medium"), GREEN_MID)
    board.text((x + width / 2, top + 124), fmt(senior_gap, 3), board.display(36), GOLD)
    board.text((x + width / 2, top + 166), "Senior gap", board.sans(15, "semibold"), GREEN)
    board.text((x + width / 2, top + 188), "flagged for review", board.sans(14, "semibold"), GOLD)
    senior_fpr_0 = senior["0"]["false_positive_rate"]
    senior_fpr_1 = senior["1"]["false_positive_rate"]
    board.text((x + 22, top + 236), "False positive rate", board.sans(15, "semibold"), GREEN)
    label_w = 84
    value_w = 48
    bar_x = x + 22 + label_w
    bar_w = width - 44 - label_w - value_w
    fpr_scale = max(senior_fpr_0, senior_fpr_1) * 1.25
    for index, (label, value, color) in enumerate(
        (
            ("Senior 0", senior_fpr_0, GREEN),
            ("Senior 1", senior_fpr_1, GOLD),
        )
    ):
        yy = top + 268 + index * 62
        board.text((x + 22, yy), label, board.sans(14, "medium"), INK)
        board.rect((bar_x, yy + 2, bar_x + bar_w, yy + 16), radius=7, fill=TRACK)
        board.rect((bar_x, yy + 2, bar_x + bar_w * (value / fpr_scale), yy + 16), radius=7, fill=color)
        board.text((bar_x + bar_w + 8, yy), fmt(value, 3), board.sans(14, "semibold"), color)
    board.text((x + 22, top + 384), "Held-out rows, same cutoff", board.sans(13, "regular"), MUTED)

    board.save(path, (1280, 640))
    _assert_social_margins(path)


def _assert_social_margins(path: Path) -> None:
    """Key ink stays inside the 40px safe area. Cream background may fill the edge."""
    image = Image.open(path).convert("RGB")
    width, height = image.size
    if (width, height) != (1280, 640):
        raise RuntimeError(f"social preview is {width}x{height}, expected 1280x640")
    pixels = image.load()
    cream = (247, 244, 236)
    margin = 40
    for x in range(width):
        for y in list(range(margin)) + list(range(height - margin, height)):
            if pixels[x, y] != cream:
                raise RuntimeError(f"content outside vertical margin at {(x, y)}")
    for y in range(height):
        for x in list(range(margin)) + list(range(width - margin, width)):
            if pixels[x, y] != cream:
                raise RuntimeError(f"content outside horizontal margin at {(x, y)}")


def _use_mpl_fonts() -> None:
    plt.rcParams.update(
        {
            "font.family": "Inter Tight",
            "font.size": 12,
            "axes.unicode_minus": False,
            "figure.facecolor": WHITE_HEX,
            "savefig.facecolor": WHITE_HEX,
            "axes.facecolor": WHITE_HEX,
            "text.color": INK_HEX,
            "axes.labelcolor": GREEN_HEX,
            "xtick.color": MUTED_HEX,
            "ytick.color": GREEN_HEX,
            "axes.edgecolor": LINE_HEX,
        }
    )


def _finish(fig, path: Path) -> None:
    fig.savefig(path, dpi=140, bbox_inches="tight", pad_inches=0.35)
    plt.close(fig)
    image = Image.open(path).convert("RGB")
    image.save(path, "PNG", optimize=True)


def chart_fairness(data: dict, path: Path) -> None:
    import numpy as np

    fairness = data["fairness"]
    _use_mpl_fonts()
    fields = ("gender", "SeniorCitizen")
    metric_keys = (
        ("selection_rate", "Selection rate", GREEN_HEX),
        ("false_positive_rate", "False positive rate", GOLD_HEX),
    )
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.0), sharey=True)
    for ax, field in zip(axes, fields):
        groups = fairness["by_field"][field]["groups"]
        names = list(groups)
        display = [f"SeniorCitizen {name}" if field == "SeniorCitizen" else name for name in names]
        xpos = np.arange(len(names))
        width = 0.34
        for index, (key, label, color) in enumerate(metric_keys):
            values = [groups[name][key] for name in names]
            offset = (index - 0.5) * width
            bars = ax.bar(xpos + offset, values, width=width, color=color, label=label, zorder=2)
            for bar, value in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.018,
                    fmt(value, 3),
                    ha="center",
                    va="bottom",
                    fontsize=11,
                    color=GREEN_HEX,
                )
        gap = fairness["by_field"][field]["demographic_parity_difference"]
        ax.set_title(f"{field}    parity gap {fmt(gap, 3)}", loc="left", fontsize=14, color=GREEN_HEX, pad=14)
        ax.set_xticks(xpos, display)
        ax.set_ylim(0, 1.0)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.grid(True, color="#F0EBE0", zorder=0)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Rate")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=2, frameon=False, bbox_to_anchor=(0.72, 1.01))
    fig.suptitle(
        "Held-out group rates",
        x=0.02,
        ha="left",
        fontsize=18,
        color=GREEN_HEX,
        fontproperties=font_manager.FontProperties(fname=str(FONT_CACHE / "Fraunces-Bold.ttf"), size=18),
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.88))
    fig.text(
        0.01,
        0.01,
        "Source: reports/fairness.json. Hard label when P(Churn=Yes) > 0.5.",
        fontsize=9,
        color=MUTED_HEX,
    )
    _finish(fig, path)


def chart_metrics(data: dict, path: Path) -> None:
    metrics = data["metrics"]["churn_models"]
    gates = data["gates"]
    _use_mpl_fonts()
    order = ("dummy_prior", "logistic_regression", "gradient_boosting")
    labels = ["Dummy\nprior", "Logistic\nregression", "Gradient\nboosting"]
    colors = ["#C8C0B0", GREEN_MID_HEX, GREEN_HEX]
    panels = (
        ("roc_auc", "ROC-AUC", 4),
        ("pr_auc", "PR-AUC", 4),
        ("top_decile_lift", "Top-decile lift", 3),
    )
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 4.8))
    for ax, (key, title, places) in zip(axes, panels):
        values = [metrics[name][key] for name in order]
        bars = ax.bar(labels, values, color=colors, width=0.72, zorder=2)
        floor = _gate(gates, key)
        ax.axhline(floor, color=GOLD_HEX, linestyle=(0, (4, 3)), linewidth=1.4, zorder=3)
        ax.set_title(f"{title}    floor {fmt(floor, 2)}", loc="left", fontsize=14, color=GREEN_HEX, pad=10)
        for bar, value in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                fmt(value, places),
                ha="center",
                va="bottom",
                fontsize=9,
                color=GREEN_HEX,
            )
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.yaxis.grid(True, color="#F0EBE0", zorder=0)
        ax.set_axisbelow(True)
        ymax = max(max(values), floor) * 1.28
        ax.set_ylim(0, ymax)
    fig.suptitle(
        "Held-out scoring metrics",
        x=0.02,
        ha="left",
        fontsize=18,
        color=GREEN_HEX,
        fontproperties=font_manager.FontProperties(fname=str(FONT_CACHE / "Fraunces-Bold.ttf"), size=18),
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.90))
    fig.text(
        0.01,
        0.01,
        "Source: reports/metrics_recomputed.json and reports/gate_check.json. Deep green is the scoring model.",
        fontsize=9,
        color=MUTED_HEX,
    )
    _finish(fig, path)


def chart_drift(data: dict, path: Path) -> None:
    drift = data["drift"]
    _use_mpl_fonts()
    rows = sorted(drift["features"], key=lambda row: row["psi"], reverse=True)
    names = [row["name"] for row in rows]
    values = [row["psi"] for row in rows]
    trigger = float(drift["psi_review_trigger"])
    fig, ax = plt.subplots(figsize=(11.4, 5.0))
    ypos = list(range(len(names)))[::-1]
    ax.barh(ypos, values, color=GREEN_HEX, height=0.62, zorder=2)
    ax.axvline(trigger, color=GOLD_HEX, linestyle=(0, (4, 3)), linewidth=1.6, zorder=3)
    ax.text(trigger, len(names) - 0.35, f"  review trigger {fmt(trigger, 2)}", color=GOLD_HEX, va="bottom", fontsize=11)
    for y, value in zip(ypos, values):
        ax.text(value + 0.004, y, fmt(value, 6), va="center", ha="left", fontsize=10, color=GREEN_HEX)
    ax.set_yticks(ypos, names)
    ax.set_xlim(0, 0.32)
    ax.set_xlabel("Population stability index")
    ax.set_title("Training split against the held-out split", loc="left", fontsize=16, color=GREEN_HEX, pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.xaxis.grid(True, color="#F0EBE0", zorder=0)
    ax.set_axisbelow(True)
    fig.suptitle(
        "PSI by feature",
        x=0.02,
        ha="left",
        fontsize=18,
        color=GREEN_HEX,
        fontproperties=font_manager.FontProperties(fname=str(FONT_CACHE / "Fraunces-Bold.ttf"), size=18),
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.90))
    fig.text(
        0.01,
        0.01,
        "Source: reports/drift_psi.json. One stratified split, not two time periods. n_above_trigger is 0.",
        fontsize=9,
        color=MUTED_HEX,
    )
    _finish(fig, path)


def main() -> None:
    data = load_reports()
    ensure_fonts()
    ASSETS.mkdir(parents=True, exist_ok=True)
    draw_hero(data, ASSETS / "hero.png")
    draw_social(data, ASSETS / "social-preview.png")
    chart_fairness(data, ASSETS / "fairness_rates.png")
    chart_metrics(data, ASSETS / "model_metrics.png")
    chart_drift(data, ASSETS / "drift_psi.png")
    for name in ("hero.png", "social-preview.png", "fairness_rates.png", "model_metrics.png", "drift_psi.png"):
        file_path = ASSETS / name
        image = Image.open(file_path)
        size_kb = file_path.stat().st_size / 1024
        print(f"{name} {image.size[0]}x{image.size[1]} {size_kb:.0f} KB")


if __name__ == "__main__":
    main()

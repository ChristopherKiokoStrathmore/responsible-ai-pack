"""Render README figures from the committed report JSON.

Every bar, line, and label is read from reports/*.json. This script does not
recompute the model and does not fill in missing metrics.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Rectangle
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
ASSETS = ROOT / "assets"

GREEN = "#0B3D2E"
GOLD = "#C8962E"
CHARCOAL = "#2B2B2B"
CREAM = "#F6F3EA"
WHITE = "#FFFFFF"
GRID = "#E3DCCE"

FONT_DIR = Path("/usr/share/fonts/truetype/macos")


def _load(name: str) -> dict:
    return json.loads((REPORTS / name).read_text())


def _register_fonts() -> None:
    for name in ("Inter-Regular.ttf", "Inter-Medium.ttf", "Inter-SemiBold.ttf", "Inter-Bold.ttf"):
        font_manager.fontManager.addfont(str(FONT_DIR / name))
    plt.rcParams["font.family"] = "Inter"
    plt.rcParams["axes.unicode_minus"] = False


def _font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    file_for = {
        "regular": "Inter-Regular.ttf",
        "medium": "Inter-Medium.ttf",
        "semibold": "Inter-SemiBold.ttf",
        "bold": "Inter-Bold.ttf",
    }
    return ImageFont.truetype(str(FONT_DIR / file_for[weight]), size)


def _header(fig, title: str, subtitle: str, badge: str | None = None) -> float:
    """Paint the green band. Returns the figure-fraction just below it."""
    height_in = float(fig.get_size_inches()[1])
    frac = 1.05 / height_in
    bottom = 1.0 - frac
    fig.patches.append(
        Rectangle((0, bottom), 1, frac, transform=fig.transFigure, facecolor=GREEN, edgecolor="none", zorder=0)
    )
    fig.patches.append(
        Rectangle((0, bottom), 1, 0.012 / height_in, transform=fig.transFigure, facecolor=GOLD, edgecolor="none", zorder=1)
    )
    fig.text(0.04, bottom + frac * 0.64, title, color=CREAM, fontsize=24, fontweight="bold", va="center", ha="left")
    fig.text(0.04, bottom + frac * 0.28, subtitle, color=GOLD, fontsize=12, va="center", ha="left")
    if badge:
        box = FancyBboxPatch(
            (0.775, bottom + frac * 0.28),
            0.185,
            frac * 0.46,
            boxstyle="round,pad=0.003,rounding_size=0.012",
            transform=fig.transFigure,
            facecolor=GOLD,
            edgecolor="none",
            zorder=2,
        )
        fig.patches.append(box)
        fig.text(0.867, bottom + frac * 0.51, badge, color=GREEN, fontsize=11, fontweight="bold", va="center", ha="center", zorder=3)
    return bottom


def _style(ax) -> None:
    ax.set_facecolor(CREAM)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(CHARCOAL)
    ax.spines["bottom"].set_color(CHARCOAL)
    ax.tick_params(colors=CHARCOAL, labelsize=11, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def _footer(fig, text: str) -> None:
    fig.text(0.04, 0.035, text, color=CHARCOAL, fontsize=10, va="center", ha="left")


def _save(fig, path: Path, width: int, height: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=100, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    image = Image.open(path)
    if image.mode != "RGB":
        base = Image.new("RGB", image.size, CREAM)
        base.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
        image = base
    if image.size != (width, height):
        raise SystemExit(f"{path.name} is {image.size}, expected {(width, height)}")
    image.save(path, format="PNG", optimize=True, compress_level=9)


def render_hero(metrics: dict, gates: dict) -> Path:
    models = (
        ("dummy_prior", "Dummy\nprior", CHARCOAL),
        ("logistic_regression", "Logistic\nregression", GOLD),
        ("gradient_boosting", "Gradient\nboosting", GREEN),
    )
    panels = (
        ("roc_auc", "ROC-AUC", 1.05),
        ("pr_auc", "PR-AUC", 1.05),
        ("top_decile_lift", "Top-decile lift", 3.45),
    )
    gate_by_name = {row["metric"]: float(row["gate"]) for row in gates["metrics"]}
    scoring = metrics["scoring_model"].replace("_", " ")
    badge = "Gate check passed" if gates["passed"] else "Gate check failed"

    fig = plt.figure(figsize=(16, 8), dpi=100, facecolor=CREAM)
    band = _header(
        fig,
        "Responsible AI pack",
        f"Scoring model: {scoring}. Positive class: Churn Yes. Held-out split.",
        badge,
    )
    fig.legend(
        handles=[
            Rectangle((0, 0), 1, 1, facecolor=CHARCOAL, edgecolor="none", label="Dummy prior"),
            Rectangle((0, 0), 1, 1, facecolor=GOLD, edgecolor="none", label="Logistic regression"),
            Rectangle((0, 0), 1, 1, facecolor=GREEN, edgecolor="none", label="Gradient boosting"),
            Line2D([0], [0], color=CHARCOAL, linewidth=1.8, linestyle="--", label="CI floor"),
        ],
        loc="upper left",
        bbox_to_anchor=(0.04, band - 0.01),
        ncol=4,
        frameon=False,
        fontsize=11,
        labelcolor=CHARCOAL,
    )
    lefts = (0.06, 0.375, 0.69)
    for left, (key, title, ymax) in zip(lefts, panels):
        ax = fig.add_axes([left, 0.16, 0.26, band - 0.24])
        _style(ax)
        values = [float(metrics["churn_models"][name][key]) for name, _, _ in models]
        colors = [color for _, _, color in models]
        bars = ax.bar(range(3), values, color=colors, width=0.68, zorder=2)
        gate = gate_by_name[key]
        ax.axhline(gate, color=WHITE, linewidth=4.5, zorder=3)
        ax.axhline(gate, color=CHARCOAL, linewidth=1.5, linestyle="--", zorder=4)
        ax.set_xlim(-0.55, 2.55)
        ax.set_ylim(0, ymax)
        ax.set_xticks(range(3))
        ax.set_xticklabels(
            [f"{label}\n{value:.6f}" for value, (_, label, _) in zip(values, models)],
            fontsize=10,
            color=CHARCOAL,
        )
        ax.set_title(f"{title}\nfloor {gate:.6f}", color=GREEN, fontsize=14, fontweight="semibold", pad=8, loc="left")
        ax.tick_params(axis="x", pad=4)
        del bars
    _footer(
        fig,
        "Source: reports/metrics_recomputed.json and reports/gate_check.json. IBM Telco Customer Churn sample. Floors are not confidence intervals.",
    )
    path = ASSETS / "hero.png"
    _save(fig, path, 1600, 800)
    return path


def _label_horizontal(ax, bars, values, pad: float) -> None:
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_width() + pad,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.6f}",
            va="center",
            ha="left",
            fontsize=10,
            color=CHARCOAL,
        )


def render_fairness(fairness: dict) -> Path:
    groups = (
        ("Female", fairness["by_field"]["gender"]["groups"]["Female"]),
        ("Male", fairness["by_field"]["gender"]["groups"]["Male"]),
        ("SeniorCitizen 0", fairness["by_field"]["SeniorCitizen"]["groups"]["0"]),
        ("SeniorCitizen 1", fairness["by_field"]["SeniorCitizen"]["groups"]["1"]),
    )
    series = (
        ("Label rate", "positive_rate", CHARCOAL),
        ("Selection rate", "selection_rate", GREEN),
        ("False positive rate", "false_positive_rate", GOLD),
    )
    fig = plt.figure(figsize=(16, 8.0), dpi=100, facecolor=CREAM)
    band = _header(
        fig,
        "Fairness on the held-out split",
        "Hard label when P(Churn=Yes) > 0.5. ROC-AUC uses the probability.",
    )
    axes_bottom = 0.20
    axes_h = (band - 0.11) - axes_bottom
    rates = fig.add_axes([0.11, axes_bottom, 0.34, axes_h])
    roc = fig.add_axes([0.54, axes_bottom, 0.18, axes_h])
    gap = fig.add_axes([0.80, axes_bottom, 0.17, axes_h])
    for ax in (rates, roc, gap):
        _style(ax)
        ax.grid(axis="y", visible=False)
        ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)

    y = list(range(len(groups)))
    height = 0.22
    for index, (label, key, color) in enumerate(series):
        offset = (index - 1) * height
        values = [float(row[key]) for _, row in groups]
        positions = [item + offset for item in y]
        bars = rates.barh(positions, values, height=height * 0.92, color=color, zorder=2, label=label)
        _label_horizontal(rates, bars, values, 0.008)
    rates.set_yticks(y)
    rates.set_yticklabels([f"{name}\nn={int(row['n'])}" for name, row in groups])
    rates.invert_yaxis()
    rates.set_xlim(0, 0.70)
    rates.set_xlabel("Rate", color=CHARCOAL)
    rates.set_title("Group rates", color=GREEN, fontsize=14, fontweight="semibold", loc="left")

    roc_values = [float(row["roc_auc"]) for _, row in groups]
    roc_bars = roc.barh(y, roc_values, height=0.62, color=GREEN, zorder=2)
    roc.set_yticks(y)
    roc.set_yticklabels([name for name, _ in groups])
    roc.invert_yaxis()
    roc.set_xlim(0, 1.48)
    roc.set_xlabel("ROC-AUC", color=CHARCOAL)
    roc.set_title("ROC-AUC", color=GREEN, fontsize=14, fontweight="semibold", loc="left")
    _label_horizontal(roc, roc_bars, roc_values, 0.02)

    fields = ("gender", "SeniorCitizen")
    parity = [float(fairness["by_field"][field]["demographic_parity_difference"]) for field in fields]
    odds = [float(fairness["by_field"][field]["equalized_odds_difference"]) for field in fields]
    positions = [1, 0]
    parity_bars = gap.barh([item + 0.16 for item in positions], parity, height=0.28, color=GREEN, zorder=2, label="Demographic parity")
    odds_bars = gap.barh([item - 0.16 for item in positions], odds, height=0.28, color=GOLD, zorder=2, label="Equalized odds")
    _label_horizontal(gap, parity_bars, parity, 0.006)
    _label_horizontal(gap, odds_bars, odds, 0.006)
    gap.set_yticks(positions)
    gap.set_yticklabels(fields)
    gap.set_xlim(0, 0.46)
    gap.set_xlabel("Absolute gap", color=CHARCOAL)
    gap.set_title("Disparity", color=GREEN, fontsize=14, fontweight="semibold", loc="left")
    fig.legend(
        handles=[
            Rectangle((0, 0), 1, 1, facecolor=CHARCOAL, edgecolor="none", label="Label rate"),
            Rectangle((0, 0), 1, 1, facecolor=GREEN, edgecolor="none", label="Selection rate"),
            Rectangle((0, 0), 1, 1, facecolor=GOLD, edgecolor="none", label="False positive rate"),
        ],
        loc="upper left",
        bbox_to_anchor=(0.11, 0.145),
        ncol=3,
        frameon=False,
        fontsize=11,
        labelcolor=CHARCOAL,
    )
    fig.legend(
        handles=[
            Rectangle((0, 0), 1, 1, facecolor=GREEN, edgecolor="none", label="Demographic parity"),
            Rectangle((0, 0), 1, 1, facecolor=GOLD, edgecolor="none", label="Equalized odds"),
        ],
        loc="upper left",
        bbox_to_anchor=(0.80, 0.145),
        ncol=1,
        frameon=False,
        fontsize=10,
        labelcolor=CHARCOAL,
    )

    _footer(fig, "Source: reports/fairness.json. These gaps are not a CI gate and not a fairness certificate.")
    path = ASSETS / "fairness_rates.png"
    _save(fig, path, 1600, 800)
    return path


def render_drift(drift: dict) -> Path:
    rows = sorted(drift["features"], key=lambda row: float(row["psi"]), reverse=True)
    names = [row["name"] for row in rows]
    values = [float(row["psi"]) for row in rows]
    trigger = float(drift["psi_review_trigger"])
    colors = [GOLD if value == max(values) else GREEN for value in values]

    fig = plt.figure(figsize=(16, 6.8), dpi=100, facecolor=CREAM)
    band = _header(
        fig,
        "Drift baseline",
        "Population stability index. Training split versus the held-out split, not two time periods.",
    )
    ax = fig.add_axes([0.16, 0.14, 0.62, band - 0.22])
    _style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    bars = ax.barh(range(len(names)), values, color=colors, height=0.68, zorder=2)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlabel("Population stability index", color=CHARCOAL)
    ax.set_xlim(0, max(values) * 1.55)
    _label_horizontal(ax, bars, values, max(values) * 0.03)
    ax.set_title(
        f"Review trigger {trigger:.6f} is above this axis. Features at or above it: {int(drift['n_above_trigger'])}.",
        color=GREEN,
        fontsize=13,
        fontweight="semibold",
        loc="left",
    )
    _footer(fig, "Source: reports/drift_psi.json. A small PSI here checks the function. It is not evidence about a later month.")
    path = ASSETS / "drift_psi.png"
    _save(fig, path, 1600, 680)
    return path


def render_shap(shap_report: dict) -> Path:
    rows = shap_report["mean_abs_shap_by_original_feature"]
    names = [row["feature"] for row in rows]
    values = [float(row["mean_abs_shap"]) for row in rows]
    colors = [GOLD if value == max(values) else GREEN for value in values]

    fig = plt.figure(figsize=(16, 8.6), dpi=100, facecolor=CREAM)
    band = _header(
        fig,
        "What the scoring model relies on",
        "Mean absolute TreeSHAP by original field, in decision-function log-odds.",
    )
    ax = fig.add_axes([0.16, 0.12, 0.62, band - 0.20])
    _style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    bars = ax.barh(range(len(names)), values, color=colors, height=0.68, zorder=2)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlabel("Mean absolute SHAP", color=CHARCOAL)
    ax.set_xlim(0, max(values) * 1.28)
    _label_horizontal(ax, bars, values, max(values) * 0.02)
    _footer(
        fig,
        "Source: reports/shap_summary.json. Each bar sums the encoded columns for that field. A bar is not a causal effect.",
    )
    path = ASSETS / "shap_original.png"
    _save(fig, path, 1600, 860)
    return path


def _fit_line(draw: ImageDraw.ImageDraw, text: str, max_width: int, start: int, weight: str) -> ImageFont.FreeTypeFont:
    size = start
    while size > 16:
        font = _font(size, weight)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 1
    return _font(16, weight)


def render_social(hero_path: Path) -> Path:
    width, height = 1280, 640
    margin = 40
    image = Image.new("RGB", (width, height), GREEN)
    draw = ImageDraw.Draw(image)
    title = "responsible-ai-pack"
    tagline = "A churn model is only useful if people can trust it."
    title_font = _fit_line(draw, title, width - 2 * margin, 40, "bold")
    tag_font = _fit_line(draw, tagline, width - 2 * margin, 24, "regular")

    draw.text((margin, margin), title, font=title_font, fill=CREAM)
    title_box = draw.textbbox((margin, margin), title, font=title_font)
    rule_y = title_box[3] + 12
    draw.rectangle((margin, rule_y, margin + 88, rule_y + 5), fill=GOLD)
    tag_y = rule_y + 14
    draw.text((margin, tag_y), tagline, font=tag_font, fill=GOLD)
    tag_box = draw.textbbox((margin, tag_y), tagline, font=tag_font)

    hero = Image.open(hero_path).convert("RGB")
    hero_w, hero_h = hero.size
    # Chart panels only. The card already carries the repo name.
    crop = hero.crop((int(0.04 * hero_w), int(0.13 * hero_h), int(0.98 * hero_w), int(0.94 * hero_h)))
    top = tag_box[3] + 16
    border = 4
    avail_w = width - 2 * margin - border * 2
    avail_h = height - margin - top - border * 2
    scale = min(avail_w / crop.size[0], avail_h / crop.size[1])
    thumb = crop.resize((max(1, int(crop.size[0] * scale)), max(1, int(crop.size[1] * scale))), Image.Resampling.LANCZOS)
    frame = Image.new("RGB", (thumb.size[0] + border * 2, thumb.size[1] + border * 2), GOLD)
    frame.paste(thumb, (border, border))
    frame_x = margin + (width - 2 * margin - frame.size[0]) // 2
    frame_y = top + (height - margin - top - frame.size[1]) // 2
    image.paste(frame, (frame_x, frame_y))

    boxes = [title_box, tag_box, (frame_x, frame_y, frame_x + frame.size[0], frame_y + frame.size[1])]
    for box in boxes:
        if box[0] < margin or box[1] < margin or box[2] > width - margin or box[3] > height - margin:
            raise SystemExit(f"Social preview content outside the {margin}px margin: {box}")

    path = ASSETS / "social-preview.png"
    image.save(path, format="PNG", optimize=True, compress_level=9)
    saved = Image.open(path)
    if saved.size != (1280, 640):
        raise SystemExit(f"social-preview.png is {saved.size}")
    return path


def main() -> None:
    _register_fonts()
    metrics = _load("metrics_recomputed.json")
    gates = _load("gate_check.json")
    fairness = _load("fairness.json")
    drift = _load("drift_psi.json")
    shap_report = _load("shap_summary.json")
    paths = [
        render_hero(metrics, gates),
        render_fairness(fairness),
        render_drift(drift),
        render_shap(shap_report),
    ]
    paths.append(render_social(paths[0]))
    for path in paths:
        image = Image.open(path)
        print(f"{path.relative_to(ROOT)} {image.size[0]}x{image.size[1]} {path.stat().st_size} bytes")


if __name__ == "__main__":
    main()

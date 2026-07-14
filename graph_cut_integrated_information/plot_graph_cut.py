"""グラフの切断によって部分間の情報共有が失われる様子を描画する。"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.patches import FancyArrowPatch


NODE_POSITIONS = {
    "A": (0.0, 1.0),
    "B": (1.0, 1.0),
    "C": (2.0, 1.0),
    "D": (3.0, 1.0),
}


def configure_japanese_font() -> None:
    """利用可能な日本語フォントを選び、図中の文字化けを防ぐ。"""
    available_fonts = {font.name for font in font_manager.fontManager.ttflist}
    candidates = ["Yu Gothic", "Meiryo", "MS Gothic", "Noto Sans CJK JP", "IPAexGothic"]
    for font_name in candidates:
        if font_name in available_fonts:
            plt.rcParams["font.family"] = font_name
            break
    plt.rcParams["axes.unicode_minus"] = False


def draw_arrow(ax: Axes, source: str, target: str, color: str = "#355070") -> None:
    """2頂点の間に有向辺を描く。"""
    start = NODE_POSITIONS[source]
    end = NODE_POSITIONS[target]
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=15,
        linewidth=2.2,
        color=color,
        shrinkA=20,
        shrinkB=20,
        connectionstyle="arc3,rad=0.08",
        zorder=1,
    )
    ax.add_patch(arrow)


def draw_network(ax: Axes, cut: bool) -> None:
    """結合されたネットワーク、または中央で切断されたネットワークを描く。"""
    internal_edges = [("A", "B"), ("B", "A"), ("C", "D"), ("D", "C")]
    cross_edges = [("B", "C"), ("C", "B")]

    for source, target in internal_edges:
        draw_arrow(ax, source, target)
    if not cut:
        for source, target in cross_edges:
            draw_arrow(ax, source, target, color="#e56b6f")

    colors = ["#6d9eeb", "#6d9eeb", "#81b29a", "#81b29a"]
    for (label, (x, y)), color in zip(NODE_POSITIONS.items(), colors):
        ax.scatter(x, y, s=950, color=color, edgecolor="white", linewidth=2.5, zorder=2)
        ax.text(x, y, label, ha="center", va="center", fontsize=14, weight="bold", zorder=3)

    if cut:
        ax.axvline(1.5, color="#e56b6f", linestyle="--", linewidth=2.5)
        ax.text(1.5, 0.35, "最小情報分割", ha="center", color="#b23a48", fontsize=10)

    ax.set_xlim(-0.55, 3.55)
    ax.set_ylim(0.15, 1.55)
    ax.axis("off")


def create_figure() -> plt.Figure:
    """ネットワーク比較と情報量の棒グラフからなる図を作る。"""
    configure_japanese_font()
    figure = plt.figure(figsize=(11, 6.2), constrained_layout=True)
    grid = figure.add_gridspec(2, 2, height_ratios=[1.0, 0.9])

    intact_ax = figure.add_subplot(grid[0, 0])
    cut_ax = figure.add_subplot(grid[0, 1])
    bar_ax = figure.add_subplot(grid[1, :])

    draw_network(intact_ax, cut=False)
    intact_ax.set_title("切断前のネットワーク", fontsize=14, weight="bold")
    intact_ax.text(1.5, 1.48, "共通の原因：X = Y", ha="center", fontsize=10)

    draw_network(cut_ax, cut=True)
    cut_ax.set_title("切断後のネットワーク", fontsize=14, weight="bold")
    cut_ax.text(1.5, 1.48, "独立した原因：X と Y", ha="center", fontsize=10)

    labels = ["切断前", "切断後"]
    mutual_information = [1.0, 0.0]
    bars = bar_ax.bar(labels, mutual_information, width=0.5, color=["#e56b6f", "#b8c0cc"])
    bar_ax.set_ylabel("左右部分間の相互情報量（ビット）")
    bar_ax.set_ylim(0, 1.2)
    bar_ax.set_title("分割によって失われる情報量の簡単なモデル", fontsize=13)
    bar_ax.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, mutual_information):
        bar_ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.04,
            f"{value:.1f} ビット",
            ha="center",
            weight="bold",
        )

    figure.suptitle("因果的な結合を切ると情報の統合が失われる", fontsize=17, weight="bold")
    return figure


def parse_args() -> argparse.Namespace:
    """コマンドライン引数を読み取る。"""
    default_output = Path(__file__).with_name("graph_cut_integrated_information.png")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=default_output, help="画像の保存先")
    parser.add_argument("--no-show", action="store_true", help="画面に図を表示しない")
    return parser.parse_args()


def main() -> None:
    """図を保存し、必要なら画面にも表示する。"""
    args = parse_args()
    figure = create_figure()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=180, bbox_inches="tight")
    print(f"図を保存しました: {args.output.resolve()}")
    if not args.no_show:
        plt.show()
    plt.close(figure)


if __name__ == "__main__":
    main()

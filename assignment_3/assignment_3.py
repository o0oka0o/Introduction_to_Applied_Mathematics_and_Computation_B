#!/usr/bin/env python3
"""交差結合した2ビット系の簡略化IIT例を可視化する。"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


STATES = ("00", "01", "10", "11")


def kl_divergence_bits(p: np.ndarray, q: np.ndarray) -> float:
    """離散分布pとqのKLダイバージェンスをbit単位で返す。"""
    mask = p > 0
    return float(np.sum(p[mask] * np.log2(p[mask] / q[mask])))


def build_repertoires() -> tuple[np.ndarray, np.ndarray]:
    """現在状態(1, 0)に対する全体系と切断後の効果レパートリーを作る。"""
    # 交差結合 A(t+1)=B(t), B(t+1)=A(t) より、次状態は(0, 1)。
    whole = np.array([0.0, 1.0, 0.0, 0.0])

    # A|Bを切断し、切断された入力を独立な公平コインで置き換える。
    # 各次状態ビットが0/1を等確率で取るため、積分布は4状態で一様になる。
    partitioned = np.full(4, 0.25)
    return whole, partitioned


def create_plot(output: Path, show: bool = True) -> float:
    """比較図を保存し、簡略化した効果側の統合情報を返す。"""
    whole, partitioned = build_repertoires()
    phi = kl_divergence_bits(whole, partitioned)

    x = np.arange(len(STATES))
    width = 0.36
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.bar(
        x - width / 2,
        whole,
        width,
        label=r"Whole system $p_{\mathrm{eff}}$",
        color="#2864A6",
    )
    ax.bar(
        x + width / 2,
        partitioned,
        width,
        label=r"Partitioned system $q_{\mathrm{eff}}$",
        color="#E69F00",
    )

    ax.set(
        title=(
            r"Cross-coupled bits: $A_{t+1}=B_t,\ B_{t+1}=A_t$"
            "\n"
            r"Current state $(A_t,B_t)=(1,0)$"
        ),
        xlabel=r"Next state $(A_{t+1},B_{t+1})$",
        ylabel="Probability",
        xticks=x,
        xticklabels=STATES,
        ylim=(0, 1.12),
    )
    ax.text(
        0.98,
        0.93,
        rf"$\phi_{{\mathrm{{eff}}}}"
        rf"=D_{{KL}}(p_{{\mathrm{{eff}}}}\Vert q_{{\mathrm{{eff}}}})"
        rf"={phi:.1f}\ \mathrm{{bits}}$",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=12,
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "white", "alpha": 0.9},
    )
    ax.legend(loc="upper left")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180, bbox_inches="tight")
    print(f"図を保存しました: {output}")
    print(f"簡略化した効果側の統合情報: {phi:.1f} bits")

    if show:
        plt.show()
    plt.close(fig)
    return phi


def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析する。"""
    default_output = Path(__file__).with_name("assignment_3.png")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=default_output,
        help="出力画像のパス",
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="画面に図を表示せず、画像の保存だけを行う",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    create_plot(args.output, show=not args.no_show)

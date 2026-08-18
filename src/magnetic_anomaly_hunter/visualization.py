from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


DISTANCE_REQUIRED_COLUMNS = [
    "edge_gap_cm",
    "repeat_count",
    "mean_anomaly_ut",
    "std_anomaly_ut",
]

RUN_REQUIRED_COLUMNS = [
    "edge_gap_cm",
    "anomaly_field_ut",
]


def load_chart_data(
    distance_summary_path,
    anomaly_runs_path,
):
    """Načíta tabuľky potrebné na vytvorenie grafu."""
    distance_summary = pd.read_csv(
        distance_summary_path
    )

    anomaly_runs = pd.read_csv(
        anomaly_runs_path
    )

    missing_distance_columns = [
        column
        for column in DISTANCE_REQUIRED_COLUMNS
        if column not in distance_summary.columns
    ]

    missing_run_columns = [
        column
        for column in RUN_REQUIRED_COLUMNS
        if column not in anomaly_runs.columns
    ]

    if missing_distance_columns:
        raise ValueError(
            "Chýbajú stĺpce v súhrne vzdialeností: "
            f"{missing_distance_columns}"
        )

    if missing_run_columns:
        raise ValueError(
            "Chýbajú stĺpce v jednotlivých meraniach: "
            f"{missing_run_columns}"
        )

    return distance_summary, anomaly_runs


def validate_chart_data(
    distance_summary,
    anomaly_runs,
):
    """Overí, či možno hodnoty zobraziť na logaritmickej osi."""
    if distance_summary.empty:
        raise ValueError("Súhrn vzdialeností je prázdny.")

    if anomaly_runs.empty:
        raise ValueError("Tabuľka meraní je prázdna.")

    if (
        distance_summary["mean_anomaly_ut"] <= 0
    ).any():
        raise ValueError(
            "Priemerné anomálie musia byť kladné."
        )

    if (
        anomaly_runs["anomaly_field_ut"] <= 0
    ).any():
        raise ValueError(
            "Jednotlivé anomálie musia byť kladné."
        )

    lower_error_limit = (
        distance_summary["mean_anomaly_ut"]
        - distance_summary["std_anomaly_ut"]
    )

    if (lower_error_limit <= 0).any():
        raise ValueError(
            "Chybová úsečka zasahuje mimo logaritmickej osi."
        )


def create_anomaly_chart(
    distance_summary,
    anomaly_runs,
    output_path,
):
    """Vytvorí graf anomálie v závislosti od vzdialenosti."""
    validate_chart_data(
        distance_summary,
        anomaly_runs,
    )

    distance_summary = (
        distance_summary
        .sort_values("edge_gap_cm")
        .reset_index(drop=True)
    )

    anomaly_runs = (
        anomaly_runs
        .sort_values(["edge_gap_cm", "repeat"])
        .reset_index(drop=True)
    )

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    figure, axis = plt.subplots(
        figsize=(9, 6),
    )

    figure.patch.set_facecolor("white")
    axis.set_facecolor("#fafafa")

    axis.scatter(
        anomaly_runs["edge_gap_cm"],
        anomaly_runs["anomaly_field_ut"],
        color="#718096",
        alpha=0.65,
        s=38,
        label="Jednotlivé opakovania",
        zorder=2,
    )

    axis.errorbar(
        distance_summary["edge_gap_cm"],
        distance_summary["mean_anomaly_ut"],
        yerr=distance_summary["std_anomaly_ut"],
        fmt="o-",
        color="#c2413b",
        ecolor="#c2413b",
        linewidth=2.2,
        markersize=7,
        markerfacecolor="white",
        markeredgewidth=2,
        capsize=5,
        label="Priemer ± smerodajná odchýlka",
        zorder=3,
    )

    for _, row in distance_summary.iterrows():
        axis.annotate(
            f"{row['mean_anomaly_ut']:.2f} µT",
            (
                row["edge_gap_cm"],
                row["mean_anomaly_ut"],
            ),
            xytext=(0, 11),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            color="#222222",
        )

    axis.set_yscale("log")

    axis.set_xticks(
        distance_summary["edge_gap_cm"]
    )

    axis.set_xlabel(
        "Medzera od hrany telefónu (cm)",
        fontsize=11,
    )

    axis.set_ylabel(
        "Veľkosť magnetickej anomálie ΔB (µT)",
        fontsize=11,
    )

    axis.set_title(
        "Magnetická anomália v závislosti od vzdialenosti",
        fontsize=14,
        pad=14,
    )

    axis.grid(
        True,
        which="major",
        linestyle="-",
        alpha=0.25,
    )

    axis.grid(
        True,
        which="minor",
        axis="y",
        linestyle=":",
        alpha=0.18,
    )

    axis.set_axisbelow(True)
    axis.margins(x=0.08)

    axis.legend(
        frameon=True,
        fontsize=9,
    )

    figure.text(
        0.5,
        0.015,
        (
            "0 cm označuje kontakt obalu s hranou telefónu, "
            "nie nulovú vzdialenosť od senzora."
        ),
        ha="center",
        fontsize=8,
        color="#555555",
    )

    figure.tight_layout(
        rect=(0, 0.045, 1, 1),
    )

    figure.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
    )

    plt.close(figure)

    return output_path


def save_anomaly_chart(
    distance_summary_path,
    anomaly_runs_path,
    output_path,
):
    """Načíta výsledky analýzy a uloží výsledný graf."""
    distance_summary, anomaly_runs = load_chart_data(
        distance_summary_path,
        anomaly_runs_path,
    )

    return create_anomaly_chart(
        distance_summary,
        anomaly_runs,
        output_path,
    )


if __name__ == "__main__":
    output_path = save_anomaly_chart(
        distance_summary_path=(
            "data/processed/distance_summary.csv"
        ),
        anomaly_runs_path=(
            "data/processed/anomaly_runs.csv"
        ),
        output_path=(
            "figures/anomaly_vs_distance.png"
        ),
    )

    print(f"Graf bol uložený do: {output_path}")

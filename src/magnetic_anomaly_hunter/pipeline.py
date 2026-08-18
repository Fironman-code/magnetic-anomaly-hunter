from pathlib import Path

from .analysis import save_analysis
from .processor import save_processed_data
from .visualization import save_anomaly_chart


def run_pipeline(
    raw_archive,
    processed_directory,
    figure_path,
):
    """Z neupraveného archívu znovu vytvorí všetky výsledky."""
    raw_archive = Path(raw_archive)
    processed_directory = Path(processed_directory)
    figure_path = Path(figure_path)

    if not raw_archive.exists():
        raise FileNotFoundError(
            f"Surový archív neexistuje: {raw_archive}"
        )

    measurements_path = (
        processed_directory / "measurements.csv"
    )

    save_processed_data(
        raw_archive,
        measurements_path,
    )

    save_analysis(
        measurements_path,
        processed_directory,
    )

    save_anomaly_chart(
        distance_summary_path=(
            processed_directory / "distance_summary.csv"
        ),
        anomaly_runs_path=(
            processed_directory / "anomaly_runs.csv"
        ),
        output_path=figure_path,
    )

    outputs = {
        "measurements": measurements_path,
        "run_summary": (
            processed_directory / "run_summary.csv"
        ),
        "background_summary": (
            processed_directory / "background_summary.csv"
        ),
        "anomaly_runs": (
            processed_directory / "anomaly_runs.csv"
        ),
        "distance_summary": (
            processed_directory / "distance_summary.csv"
        ),
        "figure": figure_path,
    }

    return outputs


if __name__ == "__main__":
    outputs = run_pipeline(
        raw_archive="data/raw/Anomaly_Hunter.zip",
        processed_directory="data/processed",
        figure_path="figures/anomaly_vs_distance.png",
    )

    print("Analytický pipeline bol dokončený.")

    for output_name, output_path in outputs.items():
        print(f"{output_name}: {output_path}")

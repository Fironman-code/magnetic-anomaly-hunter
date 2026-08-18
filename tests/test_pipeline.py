from pathlib import Path

from magnetic_anomaly_hunter.pipeline import (
    run_pipeline,
)


ARCHIVE_PATH = Path(
    "data/raw/Anomaly_Hunter.zip"
)


def test_pipeline_recreates_all_outputs(tmp_path):
    processed_directory = tmp_path / "processed"
    figure_path = (
        tmp_path
        / "figures"
        / "anomaly_vs_distance.png"
    )

    outputs = run_pipeline(
        raw_archive=ARCHIVE_PATH,
        processed_directory=processed_directory,
        figure_path=figure_path,
    )

    assert set(outputs) == {
        "measurements",
        "run_summary",
        "background_summary",
        "anomaly_runs",
        "distance_summary",
        "figure",
    }

    for output_path in outputs.values():
        assert output_path.exists()
        assert output_path.stat().st_size > 0

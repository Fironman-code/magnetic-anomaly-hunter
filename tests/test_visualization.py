from pathlib import Path

import pytest

from magnetic_anomaly_hunter.visualization import (
    create_anomaly_chart,
    load_chart_data,
)


DISTANCE_SUMMARY_PATH = Path(
    "data/processed/distance_summary.csv"
)

ANOMALY_RUNS_PATH = Path(
    "data/processed/anomaly_runs.csv"
)


def test_load_chart_data_reads_expected_rows():
    distance_summary, anomaly_runs = load_chart_data(
        DISTANCE_SUMMARY_PATH,
        ANOMALY_RUNS_PATH,
    )

    assert len(distance_summary) == 4
    assert len(anomaly_runs) == 12


def test_create_anomaly_chart_creates_png(tmp_path):
    distance_summary, anomaly_runs = load_chart_data(
        DISTANCE_SUMMARY_PATH,
        ANOMALY_RUNS_PATH,
    )

    output_path = tmp_path / "anomaly_chart.png"

    result_path = create_anomaly_chart(
        distance_summary,
        anomaly_runs,
        output_path,
    )

    assert result_path == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 1000


def test_chart_rejects_nonpositive_values(tmp_path):
    distance_summary, anomaly_runs = load_chart_data(
        DISTANCE_SUMMARY_PATH,
        ANOMALY_RUNS_PATH,
    )

    invalid_summary = distance_summary.copy()
    invalid_summary.loc[0, "mean_anomaly_ut"] = 0.0

    with pytest.raises(
        ValueError,
        match="kladné",
    ):
        create_anomaly_chart(
            invalid_summary,
            anomaly_runs,
            tmp_path / "invalid.png",
        )

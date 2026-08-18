
from pathlib import Path

import pandas as pd
import pytest

from magnetic_anomaly_hunter.analysis import (
    calculate_anomaly_runs,
    calculate_background_summary,
    load_processed_data,
    save_analysis,
    summarize_runs,
)


PROCESSED_PATH = Path(
    "data/processed/measurements.csv"
)


def test_summarize_runs_creates_fourteen_rows():
    measurements = load_processed_data(PROCESSED_PATH)

    run_summary = summarize_runs(measurements)

    assert len(run_summary) == 14
    assert run_summary["measurement_id"].nunique() == 14
    assert run_summary["sample_count"].sum() == len(
        measurements
    )
    assert run_summary["sample_count"].gt(0).all()


def test_anomaly_uses_vector_difference():
    run_summary = pd.DataFrame(
        [
            {
                "measurement_id": "background_start_r1",
                "series": "background_start",
                "measurement_type": "background",
                "edge_gap_cm": None,
                "repeat": 1,
                "source_archive": "start.zip",
                "mean_field_x_ut": 0.0,
                "mean_field_y_ut": 0.0,
                "mean_field_z_ut": 0.0,
                "mean_absolute_field_ut": 0.0,
                "std_absolute_field_ut": 0.1,
            },
            {
                "measurement_id": "background_end_r1",
                "series": "background_end",
                "measurement_type": "background",
                "edge_gap_cm": None,
                "repeat": 1,
                "source_archive": "end.zip",
                "mean_field_x_ut": 2.0,
                "mean_field_y_ut": 0.0,
                "mean_field_z_ut": 0.0,
                "mean_absolute_field_ut": 2.0,
                "std_absolute_field_ut": 0.1,
            },
            {
                "measurement_id": "d05_r1",
                "series": "d05",
                "measurement_type": "anomaly",
                "edge_gap_cm": 5.0,
                "repeat": 1,
                "source_archive": "d05.zip",
                "mean_field_x_ut": 4.0,
                "mean_field_y_ut": 3.0,
                "mean_field_z_ut": 0.0,
                "mean_absolute_field_ut": 5.0,
                "std_absolute_field_ut": 0.1,
            },
        ]
    )

    background_summary = calculate_background_summary(
        run_summary
    )

    anomaly_runs = calculate_anomaly_runs(
        run_summary,
        background_summary,
    )

    anomaly = anomaly_runs.iloc[0]

    assert anomaly["delta_field_x_ut"] == pytest.approx(
        3.0
    )
    assert anomaly["delta_field_y_ut"] == pytest.approx(
        3.0
    )
    assert anomaly["delta_field_z_ut"] == pytest.approx(
        0.0
    )
    assert anomaly["anomaly_field_ut"] == pytest.approx(
        18 ** 0.5
    )


def test_save_analysis_creates_result_files(tmp_path):
    tables = save_analysis(
        PROCESSED_PATH,
        tmp_path,
    )

    expected_files = {
        "run_summary.csv",
        "background_summary.csv",
        "anomaly_runs.csv",
        "distance_summary.csv",
    }

    assert {
        path.name
        for path in tmp_path.iterdir()
    } == expected_files

    distance_summary = tables["distance_summary"]

    assert set(distance_summary["edge_gap_cm"]) == {
        0.0,
        5.0,
        10.0,
        20.0,
    }

    assert distance_summary["repeat_count"].eq(3).all()

    anomaly_values = (
        distance_summary
        .sort_values("edge_gap_cm")
        ["mean_anomaly_ut"]
    )

    assert anomaly_values.is_monotonic_decreasing
from pathlib import Path

import pandas as pd

from magnetic_anomaly_hunter.loader import (
    load_all_measurements,
)
from magnetic_anomaly_hunter.processor import (
    PROCESSED_COLUMNS,
    prepare_processed_data,
    save_processed_data,
)


ARCHIVE_PATH = Path("data/raw/Anomaly_Hunter.zip")


def test_prepare_processed_data_creates_clean_schema():
    measurements = load_all_measurements(ARCHIVE_PATH)

    processed = prepare_processed_data(measurements)

    assert list(processed.columns) == PROCESSED_COLUMNS
    assert len(processed) == len(measurements)
    assert processed["measurement_id"].nunique() == 14

    numeric_columns = [
        "sample_index",
        "time_s",
        "field_x_ut",
        "field_y_ut",
        "field_z_ut",
        "absolute_field_ut",
    ]

    assert processed[numeric_columns].notna().all().all()
    assert all(
        pd.api.types.is_numeric_dtype(processed[column])
        for column in numeric_columns
    )


def test_save_processed_data_creates_csv(tmp_path):
    output_path = (
        tmp_path
        / "processed"
        / "measurements.csv"
    )

    processed = save_processed_data(
        ARCHIVE_PATH,
        output_path,
    )

    saved_data = pd.read_csv(output_path)

    assert output_path.exists()
    assert list(saved_data.columns) == PROCESSED_COLUMNS
    assert len(saved_data) == len(processed)
    assert saved_data["measurement_id"].nunique() == 14

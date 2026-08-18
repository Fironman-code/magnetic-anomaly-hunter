from pathlib import Path

import pandas as pd

from .loader import load_all_measurements


COLUMN_RENAMES = {
    "Time (s)": "time_s",
    "Magnetic Field x (µT)": "field_x_ut",
    "Magnetic Field y (µT)": "field_y_ut",
    "Magnetic Field z (µT)": "field_z_ut",
    "Absolute field (µT)": "absolute_field_ut",
}

INPUT_COLUMNS = [
    "series",
    "measurement_type",
    "edge_gap_cm",
    "repeat",
    "source_archive",
    *COLUMN_RENAMES.keys(),
]

PROCESSED_COLUMNS = [
    "measurement_id",
    "series",
    "measurement_type",
    "edge_gap_cm",
    "repeat",
    "source_archive",
    "sample_index",
    "time_s",
    "field_x_ut",
    "field_y_ut",
    "field_z_ut",
    "absolute_field_ut",
]


def prepare_processed_data(measurements):
    """Vyčistí názvy stĺpcov a pripraví dáta na ďalšiu analýzu."""
    missing_columns = [
        column
        for column in INPUT_COLUMNS
        if column not in measurements.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Chýbajú vstupné stĺpce: {missing_columns}"
        )

    processed = measurements.rename(
        columns=COLUMN_RENAMES
    ).copy()

    processed["repeat"] = processed["repeat"].astype("int64")

    processed["measurement_id"] = (
        processed["series"]
        + "_r"
        + processed["repeat"].astype(str)
    )

    processed = processed.sort_values(
        ["series", "repeat", "time_s"],
        kind="stable",
    ).reset_index(drop=True)

    processed["sample_index"] = (
        processed
        .groupby("measurement_id")
        .cumcount()
    )

    return processed[PROCESSED_COLUMNS]


def save_processed_data(zip_path, output_path):
    """Načíta surové dáta a uloží ich spracovanú kópiu do CSV."""
    measurements = load_all_measurements(zip_path)
    processed = prepare_processed_data(measurements)

    output_path = Path(output_path)
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    processed.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
        float_format="%.6f",
    )

    return processed


if __name__ == "__main__":
    raw_archive = Path("data/raw/Anomaly_Hunter.zip")
    output_csv = Path("data/processed/measurements.csv")

    processed = save_processed_data(
        raw_archive,
        output_csv,
    )

    print(f"Výstupný súbor: {output_csv}")
    print(f"Počet riadkov: {len(processed)}")
    print(
        "Počet meraní: "
        f"{processed['measurement_id'].nunique()}"
    )

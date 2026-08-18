from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
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

VECTOR_AXES = ("x", "y", "z")

RUN_GROUP_COLUMNS = [
    "measurement_id",
    "series",
    "measurement_type",
    "edge_gap_cm",
    "repeat",
    "source_archive",
]

ANOMALY_RUN_COLUMNS = [
    "measurement_id",
    "series",
    "edge_gap_cm",
    "repeat",
    "source_archive",
    "mean_field_x_ut",
    "mean_field_y_ut",
    "mean_field_z_ut",
    "mean_absolute_field_ut",
    "std_absolute_field_ut",
    "background_reference_x_ut",
    "background_reference_y_ut",
    "background_reference_z_ut",
    "delta_field_x_ut",
    "delta_field_y_ut",
    "delta_field_z_ut",
    "anomaly_field_ut",
]


def load_processed_data(csv_path):
    """Načíta a skontroluje spracované merania."""
    measurements = pd.read_csv(csv_path)

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in measurements.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Chýbajú spracované stĺpce: {missing_columns}"
        )

    numeric_columns = [
        "repeat",
        "sample_index",
        "time_s",
        "field_x_ut",
        "field_y_ut",
        "field_z_ut",
        "absolute_field_ut",
    ]

    columns_with_missing_values = [
        column
        for column in numeric_columns
        if measurements[column].isna().any()
    ]

    if columns_with_missing_values:
        raise ValueError(
            "Chýbajúce hodnoty v spracovaných stĺpcoch: "
            f"{columns_with_missing_values}"
        )

    anomaly_rows = measurements[
        measurements["measurement_type"] == "anomaly"
    ]

    if anomaly_rows["edge_gap_cm"].isna().any():
        raise ValueError(
            "Anomálne merania nemajú zadanú vzdialenosť."
        )

    return measurements


def summarize_runs(measurements):
    """Vytvorí jednu súhrnnú hodnotu pre každé meranie."""
    run_summary = (
        measurements
        .groupby(
            RUN_GROUP_COLUMNS,
            dropna=False,
        )
        .agg(
            sample_count=("time_s", "size"),
            duration_s=(
                "time_s",
                lambda values: values.max() - values.min(),
            ),
            mean_field_x_ut=("field_x_ut", "mean"),
            mean_field_y_ut=("field_y_ut", "mean"),
            mean_field_z_ut=("field_z_ut", "mean"),
            std_field_x_ut=("field_x_ut", "std"),
            std_field_y_ut=("field_y_ut", "std"),
            std_field_z_ut=("field_z_ut", "std"),
            mean_absolute_field_ut=(
                "absolute_field_ut",
                "mean",
            ),
            std_absolute_field_ut=(
                "absolute_field_ut",
                "std",
            ),
        )
        .reset_index()
        .sort_values(
            ["series", "repeat"],
            kind="stable",
        )
        .reset_index(drop=True)
    )

    return run_summary


def calculate_background_summary(run_summary):
    """Vypočíta referenčný vektor pozadia a jeho drift."""
    background_start = run_summary[
        run_summary["series"] == "background_start"
    ]

    background_end = run_summary[
        run_summary["series"] == "background_end"
    ]

    if background_start.empty or background_end.empty:
        raise ValueError(
            "Chýba počiatočné alebo koncové meranie pozadia."
        )

    mean_columns = [
        f"mean_field_{axis}_ut"
        for axis in VECTOR_AXES
    ]

    start_vector = background_start[mean_columns].mean()
    end_vector = background_end[mean_columns].mean()

    summary = {}

    for axis in VECTOR_AXES:
        mean_column = f"mean_field_{axis}_ut"

        start_value = start_vector[mean_column]
        end_value = end_vector[mean_column]

        summary[f"background_start_{axis}_ut"] = start_value
        summary[f"background_end_{axis}_ut"] = end_value
        summary[f"background_reference_{axis}_ut"] = (
            start_value + end_value
        ) / 2

    summary["background_drift_ut"] = (
        (
            summary["background_end_x_ut"]
            - summary["background_start_x_ut"]
        ) ** 2
        + (
            summary["background_end_y_ut"]
            - summary["background_start_y_ut"]
        ) ** 2
        + (
            summary["background_end_z_ut"]
            - summary["background_start_z_ut"]
        ) ** 2
    ) ** 0.5

    return pd.DataFrame([summary])


def calculate_anomaly_runs(
    run_summary,
    background_summary,
):
    """Odčíta referenčný vektor pozadia od každého merania."""
    if background_summary.empty:
        raise ValueError("Súhrn pozadia je prázdny.")

    background = background_summary.iloc[0]

    anomaly_runs = run_summary[
        run_summary["measurement_type"] == "anomaly"
    ].copy()

    if anomaly_runs.empty:
        raise ValueError("Neboli nájdené anomálne merania.")

    for axis in VECTOR_AXES:
        reference_column = (
            f"background_reference_{axis}_ut"
        )
        mean_column = f"mean_field_{axis}_ut"
        delta_column = f"delta_field_{axis}_ut"

        anomaly_runs[reference_column] = (
            background[reference_column]
        )

        anomaly_runs[delta_column] = (
            anomaly_runs[mean_column]
            - anomaly_runs[reference_column]
        )

    anomaly_runs["anomaly_field_ut"] = (
        anomaly_runs["delta_field_x_ut"] ** 2
        + anomaly_runs["delta_field_y_ut"] ** 2
        + anomaly_runs["delta_field_z_ut"] ** 2
    ) ** 0.5

    return (
        anomaly_runs[ANOMALY_RUN_COLUMNS]
        .sort_values(
            ["edge_gap_cm", "repeat"],
            kind="stable",
        )
        .reset_index(drop=True)
    )


def summarize_distances(anomaly_runs):
    """Spojí tri opakovania pre každú vzdialenosť."""
    distance_summary = (
        anomaly_runs
        .groupby("edge_gap_cm")
        .agg(
            repeat_count=("measurement_id", "nunique"),
            mean_anomaly_ut=("anomaly_field_ut", "mean"),
            std_anomaly_ut=("anomaly_field_ut", "std"),
            min_anomaly_ut=("anomaly_field_ut", "min"),
            max_anomaly_ut=("anomaly_field_ut", "max"),
        )
        .reset_index()
        .sort_values("edge_gap_cm")
        .reset_index(drop=True)
    )

    return distance_summary


def save_analysis(processed_path, output_directory):
    """Spustí analýzu a uloží všetky výsledné tabuľky."""
    measurements = load_processed_data(processed_path)
    run_summary = summarize_runs(measurements)

    background_summary = calculate_background_summary(
        run_summary
    )

    anomaly_runs = calculate_anomaly_runs(
        run_summary,
        background_summary,
    )

    distance_summary = summarize_distances(anomaly_runs)

    output_directory = Path(output_directory)
    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    tables = {
        "run_summary": run_summary,
        "background_summary": background_summary,
        "anomaly_runs": anomaly_runs,
        "distance_summary": distance_summary,
    }

    for filename, table in tables.items():
        table.to_csv(
            output_directory / f"{filename}.csv",
            index=False,
            encoding="utf-8",
            float_format="%.6f",
        )

    return tables


if __name__ == "__main__":
    processed_path = Path(
        "data/processed/measurements.csv"
    )

    output_directory = Path("data/processed")

    tables = save_analysis(
        processed_path,
        output_directory,
    )

    background_drift = tables[
        "background_summary"
    ].iloc[0]["background_drift_ut"]

    print(
        "Zmena pozadia medzi začiatkom a koncom: "
        f"{background_drift:.3f} µT"
    )

    print("\nVýsledná veľkosť anomálie:")
    print(
        tables["distance_summary"].to_string(
            index=False,
            float_format=lambda value: f"{value:.3f}",
        )
    )

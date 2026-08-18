from io import BytesIO, StringIO
from pathlib import PurePosixPath
from zipfile import ZipFile

import pandas as pd


REQUIRED_COLUMNS = [
    "Time (s)",
    "Magnetic Field x (µT)",
    "Magnetic Field y (µT)",
    "Magnetic Field z (µT)",
    "Absolute field (µT)",
]


MEASUREMENT_GROUPS = {
    "background_start": {
        "series": "background_start",
        "measurement_type": "background",
        "edge_gap_cm": None,
    },
    "backgorund_end": {
        "series": "background_end",
        "measurement_type": "background",
        "edge_gap_cm": None,
    },
    "dmin": {
        "series": "dmin",
        "measurement_type": "anomaly",
        "edge_gap_cm": 0.0,
    },
    "d05": {
        "series": "d05",
        "measurement_type": "anomaly",
        "edge_gap_cm": 5.0,
    },
    "d10": {
        "series": "d10",
        "measurement_type": "anomaly",
        "edge_gap_cm": 10.0,
    },
    "d20": {
        "series": "d20",
        "measurement_type": "anomaly",
        "edge_gap_cm": 20.0,
    },
}


def list_measurement_archives(zip_path):
    """Vráti zoradený zoznam ciest ku všetkým vnoreným ZIP exportom."""
    with ZipFile(zip_path) as outer_zip:
        names = outer_zip.namelist()

    archives = [
        name
        for name in names
        if name.lower().endswith(".zip")
    ]

    return sorted(archives)


def read_raw_csv(zip_path, archive_name):
    """Vráti obsah Raw Data.csv z jedného vnoreného ZIP-u ako text."""
    with ZipFile(zip_path) as outer_zip:
        inner_zip_data = outer_zip.read(archive_name)

    with ZipFile(BytesIO(inner_zip_data)) as inner_zip:
        csv_data = inner_zip.read("Raw Data.csv")

    return csv_data.decode("utf-8-sig")


def validate_required_columns(measurement_table):
    """Overí prítomnosť všetkých povinných stĺpcov."""
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in measurement_table.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Chýbajú povinné stĺpce: {missing_columns}"
        )


def validate_measurement_values(measurement_table):
    """Overí číselné typy a chýbajúce hodnoty."""
    columns_with_missing_values = [
        column
        for column in REQUIRED_COLUMNS
        if measurement_table[column].isna().any()
    ]

    if columns_with_missing_values:
        raise ValueError(
            "Chýbajúce hodnoty v stĺpcoch: "
            f"{columns_with_missing_values}"
        )

    non_numeric_columns = [
        column
        for column in REQUIRED_COLUMNS
        if not pd.api.types.is_numeric_dtype(
            measurement_table[column]
        )
    ]

    if non_numeric_columns:
        raise ValueError(
            f"Nečíselné údaje v stĺpcoch: {non_numeric_columns}"
        )


def parse_raw_csv(csv_text):
    """Premení CSV text na skontrolovanú dátovú tabuľku."""
    csv_file = StringIO(csv_text)
    measurement_table = pd.read_csv(csv_file)

    validate_required_columns(measurement_table)
    validate_measurement_values(measurement_table)

    return measurement_table


def get_measurement_metadata(archive_name):
    """Vráti názov surovej skupiny a jej normalizované metadáta."""
    folder_name = PurePosixPath(archive_name).parent.name

    if folder_name not in MEASUREMENT_GROUPS:
        raise ValueError(
            f"Neznáma skupina merania: {folder_name}"
        )

    return folder_name, MEASUREMENT_GROUPS[folder_name]


def load_all_measurements(zip_path):
    """Načíta všetky merania a spojí ich do jednej tabuľky."""
    archives = list_measurement_archives(zip_path)

    if not archives:
        raise ValueError("Archív neobsahuje žiadne merania.")

    measurement_tables = []
    repeat_counts = {}

    for archive_name in archives:
        folder_name, metadata = get_measurement_metadata(
            archive_name
        )

        repeat_counts[folder_name] = (
            repeat_counts.get(folder_name, 0) + 1
        )

        csv_text = read_raw_csv(zip_path, archive_name)
        measurement_table = parse_raw_csv(csv_text).copy()

        measurement_table["series"] = metadata["series"]
        measurement_table["measurement_type"] = (
            metadata["measurement_type"]
        )
        measurement_table["edge_gap_cm"] = (
            metadata["edge_gap_cm"]
        )
        measurement_table["repeat"] = repeat_counts[folder_name]
        measurement_table["source_archive"] = archive_name

        measurement_tables.append(measurement_table)

    all_measurements = pd.concat(
        measurement_tables,
        ignore_index=True,
    )

    metadata_columns = [
        "series",
        "measurement_type",
        "edge_gap_cm",
        "repeat",
        "source_archive",
    ]

    return all_measurements[
        metadata_columns + REQUIRED_COLUMNS
    ]


if __name__ == "__main__":
    zip_path = "data/raw/Anomaly_Hunter.zip"

    all_measurements = load_all_measurements(zip_path)

    print(f"Počet riadkov: {len(all_measurements)}")
    print(
        "Počet načítaných archívov: "
        f"{all_measurements['source_archive'].nunique()}"
    )

    summary = (
        all_measurements
        .groupby(
            ["series", "repeat"],
            dropna=False,
        )
        .size()
        .reset_index(name="samples")
    )

    print("\nPočet vzoriek v jednotlivých meraniach:")
    print(summary.to_string(index=False))
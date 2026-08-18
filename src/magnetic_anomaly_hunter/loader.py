from io import BytesIO, StringIO
from zipfile import ZipFile

import pandas as pd


REQUIRED_COLUMNS = [
    "Time (s)",
    "Magnetic Field x (µT)",
    "Magnetic Field y (µT)",
    "Magnetic Field z (µT)",
    "Absolute field (µT)",
]


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
    """Overí, že povinné stĺpce obsahujú čísla a nemajú prázdne hodnoty."""
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


if __name__ == "__main__":
    zip_path = "data/raw/Anomaly_Hunter.zip"

    archives = list_measurement_archives(zip_path)

    print(f"Počet meracích archívov: {len(archives)}")

    for archive in archives:
        print(archive)

    first_archive = archives[0]
    csv_text = read_raw_csv(zip_path, first_archive)
    csv_header = csv_text.splitlines()[0]

    print("\nHlavička prvého Raw Data.csv:")
    print(csv_header)

    measurement_table = parse_raw_csv(csv_text)

    print("\nRozmery tabuľky:")
    print(measurement_table.shape)

    print("\nPrvých päť riadkov:")
    print(measurement_table.head())
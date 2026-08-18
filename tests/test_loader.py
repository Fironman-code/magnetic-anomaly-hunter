from pathlib import Path

import pytest

from magnetic_anomaly_hunter.loader import (
    list_measurement_archives,
    parse_raw_csv,
    read_raw_csv,
)


ARCHIVE_PATH = Path("data/raw/Anomaly_Hunter.zip")

EXPECTED_HEADER = (
    '"Time (s)","Magnetic Field x (µT)",'
    '"Magnetic Field y (µT)","Magnetic Field z (µT)",'
    '"Absolute field (µT)"'
)

EXPECTED_COLUMNS = [
    "Time (s)",
    "Magnetic Field x (µT)",
    "Magnetic Field y (µT)",
    "Magnetic Field z (µT)",
    "Absolute field (µT)",
]


def test_list_measurement_archives_finds_all_exports():
    archives = list_measurement_archives(ARCHIVE_PATH)

    assert len(archives) == 14
    assert archives == sorted(archives)
    assert all(name.lower().endswith(".zip") for name in archives)


def test_read_raw_csv_returns_expected_data():
    archives = list_measurement_archives(ARCHIVE_PATH)

    csv_text = read_raw_csv(ARCHIVE_PATH, archives[0])
    lines = csv_text.splitlines()

    assert isinstance(csv_text, str)
    assert lines[0] == EXPECTED_HEADER
    assert len(lines) > 1


def test_parse_raw_csv_returns_numeric_table():
    archives = list_measurement_archives(ARCHIVE_PATH)
    csv_text = read_raw_csv(ARCHIVE_PATH, archives[0])

    measurement_table = parse_raw_csv(csv_text)

    assert list(measurement_table.columns) == EXPECTED_COLUMNS
    assert not measurement_table.empty
    assert all(dtype.kind in "fi" for dtype in measurement_table.dtypes)


def test_parse_raw_csv_rejects_missing_column():
    invalid_csv = (
        '"Time (s)","Magnetic Field x (µT)",'
        '"Magnetic Field y (µT)","Magnetic Field z (µT)"\n'
        "0.0,1.0,2.0,3.0\n"
    )

    with pytest.raises(ValueError, match="Absolute field"):
        parse_raw_csv(invalid_csv)


def test_parse_raw_csv_rejects_missing_value():
    invalid_csv = (
        '"Time (s)","Magnetic Field x (µT)",'
        '"Magnetic Field y (µT)","Magnetic Field z (µT)",'
        '"Absolute field (µT)"\n'
        "0.0,1.0,,3.0,4.0\n"
    )

    with pytest.raises(ValueError, match="Chýbajúce hodnoty"):
        parse_raw_csv(invalid_csv)


def test_parse_raw_csv_rejects_non_numeric_value():
    invalid_csv = (
        '"Time (s)","Magnetic Field x (µT)",'
        '"Magnetic Field y (µT)","Magnetic Field z (µT)",'
        '"Absolute field (µT)"\n'
        '0.0,"chyba",2.0,3.0,4.0\n'
    )

    with pytest.raises(ValueError, match="Nečíselné údaje"):
        parse_raw_csv(invalid_csv)
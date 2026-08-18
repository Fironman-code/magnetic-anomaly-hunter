from pathlib import Path

from magnetic_anomaly_hunter.loader import (
    list_measurement_archives,
    read_raw_csv,
)


ARCHIVE_PATH = Path("data/raw/Anomaly_Hunter.zip")

EXPECTED_HEADER = (
    '"Time (s)","Magnetic Field x (µT)",'
    '"Magnetic Field y (µT)","Magnetic Field z (µT)",'
    '"Absolute field (µT)"'
)


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
from pathlib import Path

from magnetic_anomaly_hunter.loader import list_measurement_archives


def test_list_measurement_archives_finds_all_exports():
    archive_path = Path("data/raw/Anomaly_Hunter.zip")

    archives = list_measurement_archives(archive_path)

    assert len(archives) == 14
    assert archives == sorted(archives)
    assert all(name.lower().endswith(".zip") for name in archives)
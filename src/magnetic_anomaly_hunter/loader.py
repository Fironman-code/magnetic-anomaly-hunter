from zipfile import ZipFile


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


if __name__ == "__main__":
    archives = list_measurement_archives("data/raw/Anomaly_Hunter.zip")

    print(len(archives))

    for archive in archives:
        print(archive)
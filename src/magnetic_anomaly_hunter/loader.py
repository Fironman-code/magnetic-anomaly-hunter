from io import BytesIO
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


def read_raw_csv(zip_path, archive_name):
    """Vráti obsah Raw Data.csv z jedného vnoreného ZIP-u ako text."""
    with ZipFile(zip_path) as outer_zip:
        inner_zip_data = outer_zip.read(archive_name)

    with ZipFile(BytesIO(inner_zip_data)) as inner_zip:
        csv_data = inner_zip.read("Raw Data.csv")

    return csv_data.decode("utf-8-sig")


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
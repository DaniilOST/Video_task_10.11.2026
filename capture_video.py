import csv
import qscript

qscript.PATH_TO_VIDEO_FOLDER = "./video"

with open("input.csv", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f, delimiter=";", quotechar='"')

    for row in reader:
        path = qscript.CaptureVideo_Magento(
            row["URL"],
            row["Company Name"],
            row["Language"],
            row["Country"],
            row["Postcode"],
            row["City"],
            row["Street"],
            row["HouseNo"],
        )
        print(row["Company Name"], "->", path)
import csv
import gzip
from io import BytesIO
import os
import shutil

import pandas as pd
import requests

import constants


def mkdir(directory: str):
    """
    Create a requested directory in the current project if that directory does not exist yet

    :param directory: Name of the
    :return: None
    """
    if os.path.exists(directory):
        print(f"Directory '{directory}' already exists, skipping mkdir")
    else:
        os.mkdir(directory)
        print(f"Created directory {directory}")


def download_and_save_gzip_from_url(source: str, destination: str):
    """
    Download a gzip file from source, decompress the archive and store it at the destination

    :param source: The full URL of the gzipped file to download
    :param destination: The location where the downloaded file will be stored
    :return: The name of the
    """

    mkdir(directory=destination)

    h = requests.head(source)
    if h.headers.get("content-type") == "application/x-gzip":
        r = requests.get(source)
        target_filename = os.path.join(destination, source.rsplit("/", 1)[1]).rsplit(".", 1)[0]
        with gzip.open(BytesIO(r.content), "rb") as f_in:
            with open(target_filename, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        print(f"File saved as {target_filename}")
    else:
        print(f"Provided source {source} is not a gzipped archive. Source not downloaded.")


def read_data_into_list():
    data_list = list()
    with open("data/vehicle.csv0001_part_00", "rb") as f:
        reader = csv.reader(f, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in reader:
            if len(row) < 36:
                row = fix_short_row(row=row)
            data_list.append(row)


def fix_short_row(row: list):
    new_row = list()
    for item in row:
        new_row.extend(item.split(','))
    return new_row


if __name__ == '__main__':

    for file in constants.FILES:
        # Download, extract and save the files to disk
        download_and_save_gzip_from_url(source=file, destination="data")

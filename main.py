import csv
import gzip
from io import BytesIO
import os
import shutil
from typing import Any, List, Tuple, Type

import pandas as pd
import requests
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

import constants
import database
import utils


def download_and_save_gzip_from_url(source: str, destination: str) -> None:
    """
    Download a gzip file from source, decompress the archive and store it at the destination

    :param source: The full URL of the gzipped file to download
    :param destination: The location where the downloaded file will be stored
    :return: The name of the
    """

    # Get header to check file type
    h = requests.head(source)
    if h.headers.get("content-type") == "application/x-gzip":
        # Download file if it is a gzip file
        r = requests.get(source)
        target_filename = os.path.join(destination, source.rsplit("/", 1)[1]).rsplit(".", 1)[0]
        with gzip.open(BytesIO(r.content), "rb") as f_in:
            with open(target_filename, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        print(f"File saved as {target_filename}")
    else:
        print(f"Provided source {source} is not a gzipped archive. Source not downloaded.")


def read_data_from_csv(source: str) -> List[List[str]]:
    """
    Reads in the csv files line by line because some processing needs to be done to make all entries same length.

    :param source: Path to the csv file to be read in
    :return: a list containing all the rows of the csv as lists
    """
    data_list = list()
    print(f"Reading csv file {source}")
    with open(source, "r") as f:
        reader = csv.reader(f, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True)
        # skip the header
        next(reader)
        for row in reader:
            # Make all PK fields upper case for deduplication later
            row[:3] = [x.upper() for x in row[:3]]
            data_list.append(row)

    print(f"Read {len(data_list)} entries")
    return data_list


def fix_short_row(row: List[str]) -> List[str]:
    """
    All short rows (less than 36 fields) contain an extra " in a field value. This is either due to typos in the colour
    field (example: Pure White",sedan") or because of wheel sizes in inches in the type field (example: 1.5d N-TEC 17")

    :param row: a list containing less than 36 items
    :return: A list containing 36 items
    """
    new_row = list()
    for item in row:
        new_row.extend(item.split('",'))
    return new_row


def make_long_enough(row: List[str]) -> List[str]:
    if len(row) > 40:
        row = row[:40]
    else:
        for i in range(40-len(row)):
            row.append("")

    return row


def split_into_long_and_normal_lists(data_list: List[List[str]], mater: List[List[str]], vehicles: List[List[str]]) -> \
        Tuple[List[List[str]], List[List[str]]]:
    """
    Because the actual data load first changes the data list of list to a pandas DataFrame the length of all rows need
    to be equal. This function splits rows based on their length into two data sets.
    The assumption here is that rows of length 36 are read in correctly, shorter rows just have 1 or 2 easily rectified
    errors and longer rows are kept separate.
    The 36 long rows are extended with an extra empty field because the destination table has 37 columns.

    :param data_list: new set of data to be split
    :param mater: the list of rows that are too long
    :param vehicles: the list of rows with the right number of fields
    :return: The list of too-long rows and the list of correct length rows
    """
    for row in data_list:
        if len(row) > 36:
            # Know too little about long_rows to pull erroneous fields together therefore
            # make every mater row exactly 40 long to fit mater table
            row = make_long_enough(row)
            mater.append(row)
            continue
        elif len(row) < 36:
            # explanation on short_row cause and fix in fix_short_row
            row = fix_short_row(row)
            # All rows with 36 fields can be appended to vehicles after receiving an empty column for insertion
        row.append(None)
        vehicles.append(row)

    return mater, vehicles


def insert_into_table(data_list: List[List[str]], table: Type[database.declarative_base], engine: Any) -> None:
    """
    This function uploads the data into the database, leveraging the power of pandas dataframe for deduplication and
    talking to the database backend for quick dataload. Duplication is checked on the primary key, duplicate rows are
    dropped.

    :param data_list: A list containing same length rows (as list) from the 7 different csv's
    :param table: sqlalchemy declarativeMeta class of the table to upload the data to
    :param engine: a Sqlalchemy engine object
    :return: None
    """
    print(f"Transform data for {table.__table__.name} into dataframe")

    df = pd.DataFrame(data=data_list, columns=inspect(table).columns.keys())
    pre_size = len(df.index)
    print(f"Created dataframe with {pre_size} rows")

    df.drop_duplicates(subset=[key.name for key in inspect(vehicle_table).primary_key], inplace=True)
    unique_size = len(df.index)
    print(f"Dataframa contains {unique_size} unique primary key entries")
    print(f"Dropped {pre_size - unique_size} non-unique primary key entries")

    df.to_sql(name=table.__table__.name,
              con=engine,
              schema=constants.CONFIG.get("database"),
              if_exists='append',
              index=False)
    print("loaded data into table")


def check_db_filled(engine: Any) -> bool:
    """
    Check if there is data in the database
    This is not a very extensive check. But the data load either hasn't been done or is complete

    :param engine: a Sqlalchemy engine object
    :return: Boolean indicating whether the database contains data or not
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    vehicles = database.Vehicle

    cnt = session.execute(vehicles.nr_of_rows())
    if cnt.scalar() == 0:
        session.close()
        return False
    else:
        session.close()
        return True


def run_db_updates(engine: Any) -> None:
    """
    Execute all data transformation queries on the database.

    :param engine: a Sqlalchemy engine object
    :return: None
    """
    Session = sessionmaker(bind=engine)
    session = Session()

    vehicles = database.Vehicle
    weirdyears = database.WeirdYears
    pistoncup = database.PistonCup

    try:
        print("Sanitizing build_year")
        session.execute(weirdyears.save_weird_years(source_table=vehicles))
        session.execute(vehicles.sanitize_build_year())

        print("Change empty string to NULL")
        vehicles.null_empty_string(session)

        print("Calculate normalized damage")
        session.execute(vehicles.normalize_amount_damage())

        print("Storing top 10 avg dmg per make-model per country")
        top_x = vehicles.create_topx()
        session.execute(pistoncup.import_scoreboard(top_x))

        session.commit()
    except:
        session.rollback()
        raise
    finally:
        print(f"All update done. Result can be found in table {pistoncup.__table__.name}.")
        session.close()


if __name__ == '__main__':
    # Download, extract and save the data files to disk
    utils.mkdir(directory=constants.DATA_FOLDER)
    for file in constants.FILES:
        download_and_save_gzip_from_url(source=file, destination=constants.DATA_FOLDER)

    # initialize objects to talk to database
    engine = utils.get_db_engine()
    if not database.is_initialized(engine):
        database.initialize_database(engine)

    if not check_db_filled(engine):
        vehicle_table = database.Vehicle
        mater_table = database.Mater

        # Read csv files into lists
        mater: List[List[str]] = list()
        vehicles: List[List[str]] = list()
        for file in os.listdir(constants.DATA_FOLDER):
            file_vehicle_list = read_data_from_csv(source=os.path.join(constants.DATA_FOLDER, file))
            mater, vehicles = split_into_long_and_normal_lists(file_vehicle_list, mater, vehicles)

        # Load data lists into database tables
        insert_into_table(data_list=vehicles, table=vehicle_table, engine=engine)
        insert_into_table(data_list=mater, table=mater_table, engine=engine)

    run_db_updates(engine)

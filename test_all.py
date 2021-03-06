import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import Column, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import String

import main
import utils


class Temp_table(declarative_base()):
    __tablename__ = 'test_table'
    __table_args__ = (
        PrimaryKeyConstraint('country', 'vehicle_id', 'licence'),
    )
    country = Column(String(4))
    vehicle_id = Column(String(255))
    licence = Column(String(255))


def test_mkdir_create_new_dir(tmpdir):
    new_directory = os.path.join(tmpdir, "test")
    utils.mkdir(new_directory)
    assert os.path.exists(new_directory)


def test_get_db_engine_works():
    engine = utils.get_db_engine()
    r = engine.execute("SHOW DATABASES;").scalar()
    assert r == "ACT"


def test_download_and_save_gzip(tmpdir):
    url = "https://s3-eu-west-1.amazonaws.com/carnext-data-engineering-assignment/test_data/vehicle.csv0001_part_00.gz"
    file = "vehicle.csv0001_part_00"
    main.download_and_save_gzip_from_url(source=url, destination=tmpdir)
    file_path = os.path.join(tmpdir, file)
    assert os.path.exists(file_path)


def test_not_download_zip(tmpdir):
    url = "http://www.awitness.org/prophecy.zip"
    file = "prophecy"
    main.download_and_save_gzip_from_url(source=url, destination=tmpdir)
    file_path = os.path.join(tmpdir, file)
    assert not(os.path.exists(file_path))


def test_read_csv_no_header():
    data = main.read_data_from_csv(source="test/vehicle.csv0001_part_00")
    assert data[0][0] == "LPAE"
    assert data[0][0] != "country"


def test_read_csv_pk_upper():
    data = main.read_data_from_csv(source="test/vehicle.csv0001_part_00")
    assert data[0][2] != "shouldnt_lower_case"


def test_read_csv_rest_not_upper():
    data = main.read_data_from_csv(source="test/vehicle.csv0001_part_00")
    assert data[0][3] == "should_lower_case"


def test_read_csv_all_rows():
    data = main.read_data_from_csv(source="test/vehicle.csv0001_part_00")
    assert len(data) == 9


def test_fix_short_row_incorrect():
    data = main.read_data_from_csv(source="test/vehicle.csv0001_part_00")
    not_fixed_row = main.fix_short_row(data[5])
    assert len(not_fixed_row) == 36


def test_fix_short_row_correct():
    data = main.read_data_from_csv(source="test/vehicle.csv0001_part_00")
    fixed_row = main.fix_short_row(data[8])
    assert len(fixed_row) == 36


def test_make_long_enough_shorter():
    data = main.read_data_from_csv(source="test/vehicle.csv0001_part_00")
    fixed_row = main.make_long_enough(data[6])
    assert len(fixed_row) == 40


def test_make_long_enough_longer():
    data = main.read_data_from_csv(source="test/vehicle.csv0001_part_00")
    fixed_row = main.make_long_enough(data[7])
    assert len(fixed_row) == 40


def test_split_into_long_and_normal_lists():
    data = main.read_data_from_csv(source="test/vehicle.csv0001_part_00")
    long, short = main.split_into_long_and_normal_lists(data_list=data, mater=list(), vehicles=list())
    assert len(short) == 7
    assert len(long) == 2


def test_insert_into_table():
    engine = utils.get_db_engine()
    Temp_table.__table__.create(bind=engine, checkfirst=True)

    data = main.read_data_from_csv(source="test/vehicle.csv0001_part_00")
    long, short = main.split_into_long_and_normal_lists(data_list=data, mater=list(), vehicles=list())

    test_short = list()
    for row in short:
        test_short.append(row[:3])
    test_short.append(test_short[6])

    main.insert_into_table(data_list=test_short, table=Temp_table, engine=engine)

    length = engine.execute("SELECT COUNT(*) FROM test_table").scalar()
    Temp_table.__table__.drop(bind=engine)

    assert length == 7

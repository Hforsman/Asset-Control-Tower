FILES = [
    "https://s3-eu-west-1.amazonaws.com/carnext-data-engineering-assignment/test_data/vehicle.csv0001_part_00.gz",
    "https://s3-eu-west-1.amazonaws.com/carnext-data-engineering-assignment/test_data/vehicle.csv0002_part_00.gz",
    "https://s3-eu-west-1.amazonaws.com/carnext-data-engineering-assignment/test_data/vehicle.csv0003_part_00.gz",
    "https://s3-eu-west-1.amazonaws.com/carnext-data-engineering-assignment/test_data/vehicle.csv0004_part_00.gz",
    "https://s3-eu-west-1.amazonaws.com/carnext-data-engineering-assignment/test_data/vehicle.csv0005_part_00.gz",
    "https://s3-eu-west-1.amazonaws.com/carnext-data-engineering-assignment/test_data/vehicle.csv0006_part_00.gz",
    "https://s3-eu-west-1.amazonaws.com/carnext-data-engineering-assignment/test_data/vehicle.csv0007_part_00.gz"
]

CONFIG = {
    "type": "mysql",
    "driver": "pymysql",
    "host": "localhost",
    "port": 3306,
    "user": "lightning",
    "password": "McQueen95",
    "database": "ACT"
}

DATA_FOLDER = "data"

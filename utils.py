from typing import Any
import os

import sqlalchemy

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


def get_db_engine() -> Any:
    db_type = constants.CONFIG.get('type')
    db_driver = constants.CONFIG.get("driver")
    db_user = constants.CONFIG.get('user')
    db_pwd = constants.CONFIG.get('password')
    db_host = constants.CONFIG.get('host')
    db_port = constants.CONFIG.get('port')
    db_name = constants.CONFIG.get('database')

    conn_string = f"{db_type}+{db_driver}://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}"

    return sqlalchemy.create_engine(conn_string)

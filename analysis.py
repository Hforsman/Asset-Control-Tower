from typing import Any, Type

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Query

import constants
import database


# TODO: sanitize make
# TODO: sanitize model

def create_topx_query(session: Type[sessionmaker],
                      table: Type[database.declarative_base] = database.Vehicle,
                      top: int = 10,
                      build_year: int = 2016) -> Query:
    """

    :param session:
    :param table: A declarative_base class object on which to perform the query
    :param top: The max rank to return; If top=3 will show you the top 3
    :param build_year: The car build year for which to run the query
    :return: A sqlalchemy ORM query object to be performed against the database
    """
    rank_avg_dmg_year = session.query(
        table.country,
        table.make,
        table.model,
        sa.func.avg(sa.cast(table.amount_damage, sa.Float)).label("avg_dmg"),
        sa.func.rank().over(
            partition_by=table.country,
            order_by=sa.func.avg(sa.cast(table.amount_damage, sa.Float)).desc()
        ).label("rank")
    )\
        .filter(table.build_year == str(build_year)) \
        .filter(table.make != "") \
        .filter(table.model != "") \
        .group_by(
            table.country,
            table.make,
            table.model
        )\
        .subquery()

    top_10 = session.query(rank_avg_dmg_year).filter(rank_avg_dmg_year.c.rank <= top)

    return top_10


def sanitize_build_year(table: Type[database.declarative_base] = database.Vehicle,) -> sa.sql.Update:
    stmt = sa.update(table).prefix_with("IGNORE").where(sa.or_(
        sa.cast(table.build_year, sa.Integer) < constants.MIN_YEAR,
        sa.cast(table.build_year, sa.Integer) > constants.MAX_YEAR)
    ).values(
        build_year=sa.cast(sa.extract('year', sa.cast(table.firstuse, sa.Date)), sa.String)
    )
    return stmt


def save_weird_years(source_table: Type[database.declarative_base] = database.Vehicle,
                     destination_table: Type[database.declarative_base] = database.WeirdYears) -> sa.sql.Insert:
    """
    Using sqlalchemy Core because ORM does not have a satisfying solution for INSERT INTO ... SELECT FROM.
    This function generates the statement to insert weird build_years with accompanying primary keys to a
    separate table.
    The `prefix_with("IGNORE")` is to run the query even though some strings cannot be converted to integers.
    The result is still as expected.

    :param source_table: Main table where all unsanitized data is stored, is. vehicles
    :param destination_table: Table to save entries with weird years for later analysis
    :return: insert statement object that can be executed against the database
    """

    stmt = sa.insert(destination_table).prefix_with("IGNORE").from_select(
        sa.inspect(destination_table).columns.keys(),
        sa.select(
            [source_table.country, source_table.vehicle_id, source_table.licence, source_table.build_year]
        ).where(
            sa.or_(
                sa.cast(source_table.build_year, sa.Integer) < constants.MIN_YEAR,
                sa.cast(source_table.build_year, sa.Integer) > constants.MAX_YEAR)
        )
    )
    return stmt


if __name__ == '__main__':
    engine = utils.get_db_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    vehicles = database.Vehicle
    weirdyears = database.WeirdYears

    session.execute(save_weird_years(source_table=vehicles, destination_table=weirdyears))
    session.commit()

    session.execute(sanitize_build_year(table=vehicles))
    session.commit()
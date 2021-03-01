from typing import Any, Type

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Query

import constants
import database


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


def null_empty_string(session: Type[sessionmaker], table: Type[database.declarative_base] = database.Vehicle,
                      field: Type[Any] = database.Vehicle.amount_damage) -> None:
    """
    Fields to be case to Numeric need to be NULL first instead of an empty string because CAST works differently
    underwater in SELECT than it does in UPDATE queries. The UPDATE query raises a
    "Incorrect DECIMAL value: '0' for column '' at row -1" error
    This update uses ORM to immediately run query against the passed session

    :param session: sqlalchemy session object to talk to the database
    :param table: Database table on which to run the query
    :param field: Field that needs to NULLed
    :return: None
    """
    session.query(table).filter(field == "").\
        update({field: sa.null()}, synchronize_session=False)


def normalize_amount_damage(table: Type[database.declarative_base] = database.Vehicle) -> sa.sql.Update:
    """
    Apply feature normalization on the amount_damage in the vehicles table. In a perfect world this would work
    regardless of table or field and do all necessary checks.

    :param table: The table against which to run the normalization query
    :return: A sql statement to update the amount_damage_norm column with normalized amount_damage per country/car
    """
    # First compute the minimum and maximum amount damage per country
    min_max = sa.select([table.country,
                         sa.case([(sa.func.max(sa.cast(table.amount_damage, sa.Numeric(14, 2))) == 0, 1)],
                                 else_=sa.func.max(sa.cast(table.amount_damage, sa.Numeric(14, 2)))).label("max_dmg"),
                         sa.func.min(sa.cast(table.amount_damage, sa.Numeric(14, 2))).label("min_dmg")]).\
        group_by(table.country).alias("min_max")

    # Second, use the min and max damage to normalize the damage per car per country and store in separate column
    norm = sa.update(table).\
        where(min_max.c.country == table.country). \
        values(amount_damage_norm=(
            (sa.cast(table.amount_damage, sa.Numeric(14, 2)) - min_max.c.min_dmg) /
            (sa.case([(min_max.c.max_dmg == 0, 1)], else_=min_max.c.max_dmg) - min_max.c.min_dmg)
        ))

    return norm


def sanitize_build_year(table: Type[database.declarative_base] = database.Vehicle,) -> sa.sql.Update:
    """
    Query to update build_year with the year in firstuse if build_year is lower than 1940 and higher than 2020.
    A quick scna of the data showed that 1940 is approximately the lowest build_year found that looks reasonable
    compared with firstuse. Somewhere it showed that the data files were created in 2018, therefore 2020 is a bit
    optimistic.
    All "years" that fall outside of this range are overwritten with the year of firstuse. If firstuse has a diverging
    year that is not further remedied because there is not anything to quickly test or check against.

    :param table: The table against which to run the query
    :return: A sql statement to update the build_year column with the firstuse year
    """

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
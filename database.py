from typing import Any, Type

from sqlalchemy import inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sqlalchemy.sql.expression as sase
from sqlalchemy.sql.schema import Column, PrimaryKeyConstraint
from sqlalchemy.sql.sqltypes import Date, Float, Integer, Numeric, String

import constants


class Vehicle(declarative_base()):
    __tablename__ = 'vehicles'
    __table_args__ = (
        PrimaryKeyConstraint('country', 'vehicle_id', 'licence'),
    )
    country = Column(String(4))
    vehicle_id = Column(String(255))
    licence = Column(String(255))
    make = Column(String(255))
    model = Column(String(255))
    type = Column(String(255))
    trim = Column(String(255))
    colour = Column(String(255))
    bodytype = Column(String(255))
    fueltype = Column(String(255))
    engine_capacity = Column(String(255))
    engine_power = Column(String(255))
    cylindercapacity = Column(String(255))
    horsepower = Column(String(255))
    geartype = Column(String(255))
    number_of_gears = Column(String(255))
    emission_class = Column(String(255))
    emission_class_incl_co2 = Column(String(255))
    co2_level_combined = Column(String(255))
    segmentation = Column(String(255))
    number_of_doors = Column(String(255))
    number_of_seats = Column(String(255))
    milage = Column(String(255))
    age = Column(String(255))
    firstuse = Column(String(255))
    build_year = Column(String(255))
    amount_damage = Column(String(255))
    price_class = Column(String(255))
    has_air_conditioning = Column(String(255))
    has_air_conditioning_automatic = Column(String(255))
    has_alloy_wheels = Column(String(255))
    has_automatic_transmission = Column(String(255))
    has_cruise_control = Column(String(255))
    has_heated_seats = Column(String(255))
    has_leather_alcantara = Column(String(255))
    has_leather_upholstery = Column(String(255))
    amount_damage_norm = Column(Numeric(10, 9))

    @classmethod
    def create_topx(cls, top: int = 10, filter_on_year: int = 2016) -> sase.select:
        rank_avg_dmg_year = sase.select([
                cls.country,
                cls.make,
                cls.model,
                sase.func.avg(sase.cast(cls.amount_damage_norm, Float)).label("avg_dmg"),
                sase.func.rank().over(
                    partition_by=cls.country,
                    order_by=sase.func.avg(sase.cast(cls.amount_damage_norm, Float)).desc()
                ).label("rnk")]) \
            .where(cls.build_year == str(filter_on_year)) \
            .where(cls.make != "") \
            .where(cls.model != "") \
            .group_by(
                cls.country,
                cls.make,
                cls.model
        ).alias("rank_dmg")

        return sase.select(rank_avg_dmg_year.columns).where(rank_avg_dmg_year.c.rnk <= top).alias("top_x")

    @classmethod
    def normalize_amount_damage(cls) -> sase.Update:
        """
        Apply feature normalization on the amount_damage in the table.

        :return: A sql statement to update the amount_damage_norm column with normalized amount_damage per country/car
        """
        # First compute the minimum and maximum amount damage per country
        min_max = sase.select([
            cls.country,
            sase.case([(sase.func.max(sase.cast(cls.amount_damage, Numeric(14, 2))) == 0, 1)],
                      else_=sase.func.max(sase.cast(cls.amount_damage, Numeric(14, 2)))).label("max_dmg"),
            sase.func.min(sase.cast(cls.amount_damage, Numeric(14, 2))).label("min_dmg")
        ]).group_by(cls.country).alias("min_max")

        # Second, use the min and max damage to normalize the damage per car per country and store in separate column
        norm = sase.update(cls). \
            where(min_max.c.country == cls.country). \
            values(amount_damage_norm=(
                (sase.cast(cls.amount_damage, Numeric(14, 2)) - min_max.c.min_dmg) /
                (sase.case([(min_max.c.max_dmg == 0, 1)], else_=min_max.c.max_dmg) - min_max.c.min_dmg)
            ))

        return norm

    @classmethod
    def nr_of_rows(cls):
        return sase.select([sase.func.count()]).select_from(cls)

    @classmethod
    def null_empty_string(cls, session: Type[sessionmaker], field: Type[Any] = amount_damage) -> None:
        """
        Fields to be case to Numeric need to be NULL first instead of an empty string because CAST works differently
        underwater in SELECT than it does in UPDATE queries. The UPDATE query raises a
        "Incorrect DECIMAL value: '0' for column '' at row -1" error
        This update uses ORM to immediately run query against the passed session

        :param session: sqlalchemy session object to talk to the database
        :param field: Field that needs to NULLed
        :return: None
        """
        session.query(cls).filter(field == "").update({field: sase.null()}, synchronize_session=False)

    @classmethod
    def sanitize_build_year(cls) -> sase.Update:
        """
        Query to update build_year with the year in firstuse if build_year is lower than 1940 and higher than 2020.
        A quick scna of the data showed that 1940 is approximately the lowest build_year found that looks reasonable
        compared with firstuse. Somewhere it showed that the data files were created in 2018, therefore 2020 is a bit
        optimistic.
        All "years" that fall outside of this range are overwritten with the year of firstuse. If firstuse has a
        diverging year that is not further remedied because there is not anything to quickly test or check against.

        :return: A sql statement to update the build_year column with the firstuse year
        """

        stmt = sase.update(cls).prefix_with("IGNORE").where(sase.or_(
            sase.cast(cls.build_year, Integer) < constants.MIN_YEAR,
            sase.cast(cls.build_year, Integer) > constants.MAX_YEAR)
        ).values(
            build_year=sase.cast(sase.extract('year', sase.cast(cls.firstuse, Date)), String)
        )
        return stmt


class Mater(declarative_base()):
    __tablename__ = 'mater'
    __table_args__ = (
        PrimaryKeyConstraint('country', 'vehicle_id', 'licence'),
    )
    country = Column(String(4))
    vehicle_id = Column(String(255))
    licence = Column(String(255))
    col04 = Column(String(255))
    col05 = Column(String(255))
    col06 = Column(String(255))
    col07 = Column(String(255))
    col08 = Column(String(255))
    col09 = Column(String(255))
    col10 = Column(String(255))
    col11 = Column(String(255))
    col12 = Column(String(255))
    col13 = Column(String(255))
    col14 = Column(String(255))
    col15 = Column(String(255))
    col16 = Column(String(255))
    col17 = Column(String(255))
    col18 = Column(String(255))
    col19 = Column(String(255))
    col20 = Column(String(255))
    col21 = Column(String(255))
    col22 = Column(String(255))
    col23 = Column(String(255))
    col24 = Column(String(255))
    col25 = Column(String(255))
    col26 = Column(String(255))
    col27 = Column(String(255))
    col28 = Column(String(255))
    col29 = Column(String(255))
    col30 = Column(String(255))
    col31 = Column(String(255))
    col32 = Column(String(255))
    col33 = Column(String(255))
    col34 = Column(String(255))
    col35 = Column(String(255))
    col36 = Column(String(255))
    col37 = Column(String(255))
    col38 = Column(String(255))
    col39 = Column(String(255))
    col40 = Column(String(255))


class PistonCup(declarative_base()):
    __tablename__ = 'pistoncup'
    __table_args__ = (
        PrimaryKeyConstraint('country', 'make', 'model'),
    )
    country = Column(String(4))
    make = Column(String(255))
    model = Column(String(255))
    amount_damage = Column(String(255))
    rnk = Column(Integer)

    def __repr__(self):
        return f"pistoncup(country={self.country}; make={self.make}; model={self.model}; " \
               f"amount_damage={self.amount_damage}; rank={self.rnk})"

    @classmethod
    def wipe_slate(cls):
        return sase.delete(cls).alias("delete_all")

    @classmethod
    def import_scoreboard(cls, top_x: sase.select) -> sase.insert:
        return sase.insert(cls).from_select(inspect(cls).columns.keys(), sase.select(top_x.columns))


class WeirdYears(declarative_base()):
    __tablename__ = 'weirdyears'
    __table_args__ = (
        PrimaryKeyConstraint('country', 'make', 'model'),
    )
    country = Column(String(4))
    make = Column(String(255))
    model = Column(String(255))
    build_year = Column(String(255))

    def __repr__(self):
        return f"weirdyears(country={self.country}; make={self.make}; model={self.model}; build_year={self.build_year})"

    @classmethod
    def save_weird_years(cls, source_table: Type[declarative_base] = Vehicle) -> sase.Insert:
        """
        This function generates the statement to insert weird build_years with accompanying primary keys to
        this table.
        The `prefix_with("IGNORE")` is to run the query even though some strings cannot be converted to integers.
        The result is still as expected.

        :param source_table: Main table where all unsanitized data is stored, is. vehicles
        :return: insert statement object that can be executed against the database
        """

        stmt = sase.insert(cls).prefix_with("IGNORE").from_select(
            inspect(cls).columns.keys(),
            sase.select(
                [source_table.country, source_table.vehicle_id, source_table.licence, source_table.build_year]
            ).where(
                sase.or_(
                    sase.cast(source_table.build_year, Integer) < constants.MIN_YEAR,
                    sase.cast(source_table.build_year, Integer) > constants.MAX_YEAR)
            )
        )
        return stmt


def initialize_database(engine: Any) -> None:
    Vehicle.__table__.create(bind=engine, checkfirst=True)
    Mater.__table__.create(bind=engine, checkfirst=True)
    PistonCup.__table__.create(bind=engine, checkfirst=True)
    WeirdYears.__table__.create(bind=engine, checkfirst=True)


def is_initialized(engine: Any) -> bool:
    table_names = inspect(engine).get_table_names()
    is_empty = table_names == []
    return not is_empty

from typing import Any

from sqlalchemy import Column, inspect, Integer, Numeric, PrimaryKeyConstraint, String
from sqlalchemy.ext.declarative import declarative_base


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
    rank = Column(Integer)

    def __repr__(self):
        return f"pistoncup(country={self.country}; make={self.make}; model={self.model}; " \
               f"amount_damage={self.amount_damage}; rank={self.rank})"


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


def initialize_database(engine: Any) -> None:
    Vehicle.__table__.create(bind=engine, checkfirst=True)
    Mater.__table__.create(bind=engine, checkfirst=True)
    PistonCup.__table__.create(bind=engine, checkfirst=True)
    WeirdYears.__table__.create(bind=engine, checkfirst=True)


def is_initialized(engine: Any) -> bool:
    table_names = inspect(engine).get_table_names()
    is_empty = table_names == []
    return not is_empty

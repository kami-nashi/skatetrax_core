from sqlalchemy import func
from models.cyberconnect2 import Session, engine

from models.t_ice_time import Ice_Time
from models.t_locations import Locations
from models.t_icetype import IceType
from models.t_coaches import Coaches
from models.t_equip import uSkateConfig, uSkaterBlades, uSkaterBoots
from models.t_classes import Skate_School

from models.t_skaterMeta import uSkaterConfig

session = Session()


class Coach_Data():

    def add_coaches(coaches):
        for coach in coaches:
            try:
                session.add(Coaches(**coach))
                session.commit()
            except Exception as why:
                print(why)
        session.close()


class Equipment_Data():

    def add_blades(blades):
        for blade in blades:
            try:
                session.add(uSkaterBlades(**blade))
                session.commit()
            except Exception as why:
                print(why)
        session.close()

    def add_boots(boots):
        for boot in boots:
            try:
                session.add(uSkaterBoots(**boot))
                session.commit()
            except Exception as why:
                print(why)
        session.close()

    def add_combo(configs):
        for config in configs:
            try:
                session.add(uSkateConfig(**config))
                session.commit()
            except Exception as why:
                print(why)
        session.close()

    def add_maintenance():
        print('work in progress')


class Ice_Session():

    def add_skate_time(sessions):
        for asession in sessions:
            try:
                session.add(Ice_Time(**asession))
                session.commit()
            except Exception as why:
                print(why)
                session.rollback()
        session.close()

    def add_skate_school(classes):
        for aclass in classes:
            try:
                session.add(Skate_School(**aclass))
                session.commit()
            except Exception as why:
                print(why)
        session.close()


class Location_Data():

    def add_ice_type(types):
        for ice_type in types:
            try:
                session.add(IceType(**ice_type))
                session.commit()
            except Exception as why:
                print(why)
        session.close()

    def add_ice_rink(rinks):
        for rink in rinks:
            try:
                session.add(Locations(**rink))
                session.commit()
            except Exception as why:
                print(why)
        session.close()


class User_Data():

    def add_skater(skater_data):
        for data in skater_data:
            try:
                session.add(uSkaterConfig(**data))
                session.commit()
            except Exception as why:
                print(why)
        session.close()

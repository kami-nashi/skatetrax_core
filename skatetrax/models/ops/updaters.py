from sqlalchemy import func

from ..cyberconnect2 import create_session

from ..t_ice_time import Ice_Time
from ..t_locations import Locations
from ..t_icetype import IceType
from ..t_coaches import Coaches
from ..t_equip import uSkateConfig, uSkaterBlades, uSkaterBoots
from ..t_classes import Skate_School

from ..t_skaterMeta import uSkaterConfig


class Coach_Data():

    def add_coaches(coaches, session=None):
        def _run(sess):
            for coach in coaches:
                try:
                    sess.add(Coaches(**coach))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)


class Equipment_Data():

    def add_blades(blades, session=None):
        def _run(sess):
            for blade in blades:
                try:
                    sess.add(uSkaterBlades(**blade))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_boots(boots, session=None):
        def _run(sess):
            for boot in boots:
                try:
                    sess.add(uSkaterBoots(**boot))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_combo(configs, session=None):
        def _run(sess):
            for config in configs:
                try:
                    sess.add(uSkateConfig(**config))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_maintenance(session=None):
        print('work in progress')


class Ice_Session():

    def add_skate_time(sessions, session=None):
        def _run(sess):
            for asession in sessions:
                try:
                    sess.add(Ice_Time(**asession))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_skate_school(classes, session=None):
        def _run(sess):
            for aclass in classes:
                try:
                    sess.add(Skate_School(**aclass))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)


class Location_Data():

    def add_ice_type(types, session=None):
        def _run(sess):
            for ice_type in types:
                try:
                    sess.add(IceType(**ice_type))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)

    def add_ice_rink(rinks, session=None):
        def _run(sess):
            for rink in rinks:
                try:
                    sess.add(Locations(**rink))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)


class User_Data():

    def add_skater(skater_data, session=None):
        def _run(sess):
            for data in skater_data:
                try:
                    sess.add(uSkaterConfig(**data))
                    sess.commit()
                except Exception as why:
                    sess.rollback()
                    print(why)
        if session is not None:
            _run(session)
        else:
            with create_session() as sess:
                _run(sess)
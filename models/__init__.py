# coding=utf-8
import pandas as pd
from sqlalchemy import func
from models.cyberconnect2 import Session, engine

from models.t_ice_time import Ice_Time
from models.t_locations import Locations
from models.t_icetype import IceType
from models.t_coaches import Coaches


session = Session()


class coaches():

    def add_coaches(coaches):
        for coach in coaches:
            session.add(Coaches(**coach))
            session.commit()
        session.close()


class locations():

    def add_rink(rinks):
        for rink in rinks:
            session.add(Locations(**rink))
            session.commit()
        session.close()

    def add_types(ice_types):
        for types in ice_types:
            session.add(IceType(**types))
            session.commit()
        session.close()


class ice_cost():
    def __init__(self, uSkateUUID):
        self.uSkateUUID = uSkateUUID

    def ice_cost(self):
        '''
        Total cost of time on ice, by uSkaterUUID.
        '''

        with Session() as s:
            cost = (
                s.query(func.sum(Ice_Time.ice_cost))
                .where(Ice_Time.uSkaterUUID == self.uSkateUUID)
                .scalar()
                    )

        return cost


class ice_time():
    def __init__(self, uSkaterUUID):
        self.uSkaterUUID = uSkaterUUID

    def ice_time_in_minutes(self):
        '''
        Get all minutes for a skater, by uSkaterUUID.
        '''

        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.ice_time))
                .where(Ice_Time.uSkaterUUID == self.uSkaterUUID)
                .scalar()
                        )
        return minutes

    def ice_time_config_in_minutes(self, uSkaterConfig):
        '''
        Get all minutes for a specific configuration of a skater.
        Requires the uSkaterConfig as an ID to match on.
        '''

        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.ice_time))
                .where(Ice_Time.uSkaterUUID == self.uSkaterUUID)
                .where(Ice_Time.uSkaterConfig == uSkaterConfig)
                .scalar()
                        )
        return minutes


class insert_data():

    def add_bulk_session(ice_session):
        with Session() as s:
            for session in ice_session:
                s.add(Ice_Time(**session))
                s.commit()
        s.close()


class ice_sessions():

    def list_all(uSkaterUUID):
        with Session() as s:
            all_sessions = (
                s.query(Ice_Time, Locations, IceType)
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .join(Locations, Ice_Time.rink_id == Locations.rink_id)
                .join(IceType, Ice_Time.skate_type == IceType.id)
                .all()
                )

        return all_sessions

    def df_all(uSkaterUUID):
        df = pd.read_sql_query(
            sql=Session().query(
                Ice_Time.date,
                Ice_Time.ice_time,
                Ice_Time.ice_cost,
                IceType.ice_type,
                Ice_Time.coach_time,
                Coaches.coach_Fname,
                Coaches.coach_Lname,
                Ice_Time.coach_cost,
                Locations.rink_name,
                Locations.rink_city,
                Locations.rink_state,
                )
            .where(Ice_Time.uSkaterUUID == uSkaterUUID)
            .join(Locations, Ice_Time.rink_id == Locations.rink_id)
            .join(IceType, Ice_Time.skate_type == IceType.id)
            .join(Coaches, Ice_Time.coach_id == Coaches.id)
            .statement, con=engine
        )

        return df

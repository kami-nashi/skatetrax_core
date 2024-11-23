# coding=utf-8
from sqlalchemy import func
from models.cyberconnect2 import Session
from models.ice_time import Ice_Time

session = Session()


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

    def add_data(ice_session):
        with Session() as s:
            session = Ice_Time(**ice_session)
            s.add(session)
            s.commit()
            s.close()

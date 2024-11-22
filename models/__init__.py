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
        cost = session.query(
            func.sum(Ice_Time.ice_cost)
        ).where(
            Ice_Time.uSkaterUUID == self.uSkateUUID
            ).scalar()

        return cost


class ice_time():
    def __init__(self, uSkaterUUID):
        self.uSkaterUUID = uSkaterUUID

    def ice_time_in_minutes(self):
        '''
        Get all minutes for a skater, by uSkaterUUID.
        '''

        minutes = session.query(
            func.sum(Ice_Time.ice_time)
                                ).where(
                                    Ice_Time.uSkaterUUID == self.uSkaterUUID
                                    ).scalar()
        return minutes

    def ice_time_config_in_minutes(self, uSkaterConfig):
        '''
        Get all minutes for a specific configuration of a skater.
        Requires the uSkaterConfig as an ID to match on.
        '''

        minutes = session.query(
            func.sum(Ice_Time.ice_time)
                                ).where(
                                    Ice_Time.uSkaterUUID == self.uSkaterUUID
                                    ).where(
                                        Ice_Time.uSkaterConfig == uSkaterConfig
                                        ).scalar()
        return minutes

import pandas as pd
# from sqlalchemy import func
from models.cyberconnect2 import Session, engine

from utils.common import Timelines
# from utils.common import minutes_to_hours, currency_usd

from models.t_ice_time import Ice_Time
from models.t_locations import Locations
from models.t_icetype import IceType
from models.t_coaches import Coaches
from models.t_equip import uSkateConfig, uSkaterBlades, uSkaterBoots
from models.ops.data_aggregates import Sessions_Time
# from models.t_classes import Skate_School

# from models.t_skaterMeta import uSkaterConfig

session = Session()


class Equipment():

    def skate_configs(uSkaterUUID):
        '''
        Lists all boot and blade combinations defined for a skater
        '''

        df = pd.read_sql_query(
            sql=Session().query(
                uSkateConfig.date_created,
                uSkaterBoots.bootsName,
                uSkaterBoots.bootsModel,
                uSkaterBlades.bladesName,
                uSkaterBlades.bladesModel,
                uSkateConfig.sConfigID
                )
            .where(uSkateConfig.uSkaterUUID == uSkaterUUID)
            .join(
                uSkaterBoots,
                uSkateConfig.uSkaterBootsID == uSkaterBoots.bootsID
                  )
            .join(
                uSkaterBlades,
                uSkateConfig.uSkaterBladesID == uSkaterBlades.bladesID
                  )
            .statement, con=engine
            )

        df['hours'] = df.apply(lambda x: Sessions_Time.ice_time_config_in_minutes(uSkaterUUID, x['sConfigID']), axis=1)
        df = df.drop(columns=['sConfigID'])
        df = df.sort_values('date_created', ascending=False)

        return df


class Sessions_Tables():

    def ice_time(uSkaterUUID):
        '''
        lists all ice sessions of a particular skater via uSkaterUUID
        Returns a pandas dataframe containing joined data of:
        date, ice session meta, coach meta, rink meta.
        '''

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
            .join(IceType, Ice_Time.skate_type == IceType.ice_type_id)
            .join(Coaches, Ice_Time.coach_id == Coaches.uSkaterUUID)
            .statement, con=engine
        )

        df['coach'] = df['coach_Fname'].fillna('') + ' ' + df['coach_Lname'].fillna('')
        df = df.drop(columns=['coach_Fname', 'coach_Lname'])

        return df

    def ice_time_current_month(uSkaterUUID):
        '''
        lists all ice sessions of a particular skater via uSkaterUUID
        for the current month.
        Returns a pandas dataframe containing joined data of:
        date, ice session meta, coach meta, rink meta.
        '''
        tl = Timelines.current_month()

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
            .filter(Ice_Time.date >= tl['last'])
            .filter(Ice_Time.date <= tl['first'])
            .join(Locations, Ice_Time.rink_id == Locations.rink_id)
            .join(IceType, Ice_Time.skate_type == IceType.ice_type_id)
            .join(Coaches, Ice_Time.coach_id == Coaches.uSkaterUUID)
            .statement, con=engine
        )

        df['coach'] = df['coach_Fname'].fillna('') + ' ' + df['coach_Lname'].fillna('')
        df = df.drop(columns=['coach_Fname', 'coach_Lname'])

        return df

    def active_config(uSkaterUUID):
        '''
        returns a pandas dataframe of only the current skate
        config combo for a specific uSkaterUUID
        '''

        df = pd.read_sql_query(
            sql=Session()
            .query(
                uSkateConfig.date_created,
                uSkaterBoots.bootsModel,
                uSkaterBoots.bootsName,
                uSkaterBlades.bladesModel,
                uSkaterBlades.bladesName
            )
            .where(
                (uSkateConfig.uSkaterUUID == uSkaterUUID)
                & (uSkateConfig.uConfigActive == 1)
                & (uSkaterBoots.uSkaterUUID == uSkaterUUID)
                & (uSkaterBlades.uSkaterUUID == uSkaterUUID)
                )
            .join(
                uSkaterBoots,
                uSkateConfig.uSkaterBootsID == uSkaterBoots.bootsID
                )
            .join(
                uSkaterBlades,
                uSkateConfig.uSkaterBladesID == uSkaterBlades.bladesID
                )
            .distinct()
            .statement, con=engine
        )

        return df


class Skating_Locations():

    def rinks():
        '''
        lists all ice sessions of a particular skater via uSkaterUUID
        Returns a pandas dataframe containing joined data of:
        date, ice session meta, coach meta, rink meta.
        '''

        df = pd.read_sql_query(
            sql=Session().query(
                Locations
                )
            .statement, con=engine
        )

        return df

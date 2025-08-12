from sqlalchemy import func
from ...models.cyberconnect2 import Session

from ...utils.common import Timelines
from ...utils.common import minutes_to_hours, currency_usd

from ..t_ice_time import Ice_Time
# from models.t_locations import Locations
# from models.t_icetype import IceType
# from models.t_coaches import Coaches
from ..t_equip import uSkateConfig, uSkaterBlades, uSkaterBoots
# from models.t_classes import Skate_School

from ..t_skaterMeta import uSkaterConfig

session = Session()


class Equipment():

    def config_active(uSkaterUUID):
        config = UserMeta.skater_config_active_ice(uSkaterUUID)

        with Session() as s:
            data = (
                s.query(
                    uSkateConfig.date_created,
                    uSkaterBoots.bootsName,
                    uSkaterBoots.bootsModel,
                    uSkaterBlades.bladesName,
                    uSkaterBlades.bladesModel
                        )
                .join(uSkaterBoots, uSkateConfig.uSkaterBootsID == uSkaterBoots.bootsID)
                .join(uSkaterBlades, uSkateConfig.uSkaterBladesID == uSkaterBlades.bladesID)
                .where(uSkateConfig.sConfigID == config)
                .one()
            )
        return data._asdict()


class Sessions_Time():

    @minutes_to_hours
    def skated_total(uSkaterUUID):
        '''
        Get all minutes for a skater, by uSkaterUUID.
        '''

        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.ice_time))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .scalar()
                        )
        return minutes

    @minutes_to_hours
    def skated_current_month(uSkaterUUID):
        tl = Timelines.current_month()
        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.ice_time))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .filter(Ice_Time.date >= tl['last'])
                .filter(Ice_Time.date <= tl['first'])
                .scalar()
                        )
        return minutes

    @minutes_to_hours
    def skated_last_month(uSkaterUUID):
        tl = Timelines.last_month()
        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.ice_time))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .filter(Ice_Time.date >= tl['first'])
                .filter(Ice_Time.date <= tl['last'])
                .scalar()
                        )
        return minutes

    @minutes_to_hours
    def skated_3month(uSkaterUUID):
        tl = Timelines.last_3m()
        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.ice_time))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .filter(Ice_Time.date >= tl['first'])
                .filter(Ice_Time.date <= tl['last'])
                .scalar()
                        )
        return minutes

    @minutes_to_hours
    def coached_total(uSkaterUUID):
        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.coach_time))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .scalar()
                        )
        return minutes

    @minutes_to_hours
    def coached_current_month(uSkaterUUID):
        tl = Timelines.current_month()
        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.coach_time))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .filter(Ice_Time.date >= tl['last'])
                .filter(Ice_Time.date <= tl['first'])
                .scalar()
                        )
        return minutes

    @minutes_to_hours
    def coached_last_month(uSkaterUUID):
        tl = Timelines.last_month()
        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.coach_time))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .filter(Ice_Time.date >= tl['first'])
                .filter(Ice_Time.date <= tl['last'])
                .scalar()
                        )
        return minutes

    @minutes_to_hours
    def coached_3month(uSkaterUUID):
        tl = Timelines.last_3m()
        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.coach_time))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .filter(Ice_Time.date >= tl['first'])
                .filter(Ice_Time.date <= tl['last'])
                .scalar()
                        )
        return minutes

    @minutes_to_hours
    def ice_time_config_in_minutes(uSkaterUUID, uSkaterConfig):
        '''
        Get all minutes for a specific configuration of a skater.
        Requires the uSkaterConfig as an ID to match on.
        '''

        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.ice_time))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .where(Ice_Time.uSkaterConfig == uSkaterConfig)
                .scalar()
                        )
        return minutes


class Sessions_Costs():

    @currency_usd
    def ice_total(uSkaterUUID):
        '''
        Get cost of all skate entries for a skater, by uSkaterUUID.
        '''

        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.ice_cost))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .scalar()
                        )
        return minutes

    @currency_usd
    def ice_current_month(uSkaterUUID):
        tl = Timelines.current_month()
        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.ice_cost))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .filter(Ice_Time.date >= tl['last'])
                .filter(Ice_Time.date <= tl['first'])
                .scalar()
                        )
        return minutes

    @currency_usd
    def ice_last_month(uSkaterUUID):
        tl = Timelines.last_month()
        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.ice_cost))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .filter(Ice_Time.date >= tl['first'])
                .filter(Ice_Time.date <= tl['last'])
                .scalar()
                        )
        return minutes

    @currency_usd
    def ice_3month(uSkaterUUID):
        tl = Timelines.last_3m()
        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.ice_cost))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .filter(Ice_Time.date >= tl['first'])
                .filter(Ice_Time.date <= tl['last'])
                .scalar()
                        )
        return minutes

    @currency_usd
    def coached_total(uSkaterUUID):
        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.coach_cost))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .scalar()
                        )
        return minutes

    @currency_usd
    def coached_current_month(uSkaterUUID):
        tl = Timelines.current_month()
        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.coach_cost))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .filter(Ice_Time.date >= tl['last'])
                .filter(Ice_Time.date <= tl['first'])
                .scalar()
                        )
        return minutes

    @currency_usd
    def coached_last_month(uSkaterUUID):
        tl = Timelines.last_month()
        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.coach_cost))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .filter(Ice_Time.date >= tl['first'])
                .filter(Ice_Time.date <= tl['last'])
                .scalar()
                        )
        return minutes

    @currency_usd
    def coached_3month(uSkaterUUID):
        tl = Timelines.last_3m()
        with Session() as s:
            minutes = (
                s.query(func.sum(Ice_Time.coach_cost))
                .where(Ice_Time.uSkaterUUID == uSkaterUUID)
                .filter(Ice_Time.date >= tl['first'])
                .filter(Ice_Time.date <= tl['last'])
                .scalar()
                        )
        return minutes


class UserMeta():

    def skater_profile(uSkaterUUID):
        with Session() as s:
            data = (
                s.query(uSkaterConfig)
                .where(uSkaterConfig.uSkaterUUID == uSkaterUUID)
                .one()
                )

        return data

    def skater_config_active_ice(uSkaterUUID):
        with Session() as s:
            data = (
                s.query(uSkaterConfig.uSkaterComboIce)
                .where(uSkaterConfig.uSkaterUUID == uSkaterUUID)
                .scalar()
                )
        return data

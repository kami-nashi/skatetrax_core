from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float
from sqlalchemy.orm import sessionmaker, declarative_base
# from datetime import datetime
import os


db_url = os.environ['pgdb_host']
db_name = os.environ['pgdb_name']
db_user = os.environ['pgdb_user']
passwd = os.environ['pgdb_password']
# date_now = datetime()

engine = create_engine(f'postgresql://{db_user}:{passwd}@{db_url}/{db_name}')
Session = sessionmaker(bind=engine)
Base = declarative_base()


class IceType():
    '''
    This table describes the different types of ice sessions, used
    as part of foreign keys. If you want a human readable experience,
    this needs to be populated at setup.

    Used to calcuate things like how many hours or dollars have been spent
    competing vs practicing, or practicing on freestyle vs public time
    '''

    id = Column(Integer, primary_key=True)
    ice_type = Column(String)

    def __init__(self, ice_type):
        self.ice_type = ice_type


class Coaches():
    '''
    This table describes basic coach data, such as name and rate.
    Its worth mentioning that this table complicates other areas because
    it defines what coaches can be used to track time, but we also want
    to define coaches in the uSkaterConfig table.  This table may either
    be dropped in the future or we may need some logic to account for using
    this table when a skater wants to track coach time with a coach that isnt
    a skatetrax user.  Currently, this logic doesn't exist.

    A coach with a uSkaterUUID of NULL should indicate that the coach isnt
    a skatetrax user yet.

    Row 1 should always be a generic entry for 'no coach'.
    '''

    id = Column(Integer, primary_key=True)
    coach_Fname = Column(String)
    coach_Lname = Column(String)
    coach_rate = Column(Float)
    uSkaterUUID = Column(Integer)

    def __init__(self, coach_Fname, coach_Lname, coach_rate, uSkaterUUID):
        self.coach_Fname = coach_Fname
        self.coach_Lname = coach_Lname
        self.coach_rate = coach_rate
        self.uSkaterUUID = uSkaterUUID


class uSkaterConfig():
    '''
    Contains data about the skater specifically, including preferences.
    The uSkaterUUID drives most of this app, it connects literally every
    row and piece of data together to show hours and costs for any specific
    part of the skating journey.
    '''

    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime)
    uSkaterUUID = Column(Integer)
    uSkaterFname = Column(String)
    uSkaterMname = Column(String)
    uSkaterLname = Column(String)
    uSkaterZip = Column(Integer)
    uSkaterCity = Column(String)
    uSkaterState = Column(String)
    uSkaterCountry = Column(String)
    uSkaterComboIce = Column(Integer)
    uSkaterComboOff = Column(Integer)
    uSkaterRinkPref = Column(Integer)
    uSkaterMaintPref = Column(Integer)
    uSkaterSolo = Column(Integer)
    uSkaterParent = Column(Integer)
    uSkaterPair = Column(Integer)
    uSkaterCoach = Column(Integer)
    activeCoach = Column(Integer)
    org_Club_Name = Column(String)
    org_Club_Join_Date = Column(DateTime)
    org_USFSA_number = Column(Integer)

    def __init__(
        self,
        date_created,
        uSkaterUUID,
        uSkaterFname,
        uSkaterMname,
        uSkaterLname,
        uSkaterZip,
        uSkaterCity,
        uSkaterState,
        uSkaterCountry,
        uSkaterComboIce,
        uSkaterComboOff,
        uSkaterRinkPref,
        uSkaterMaintPref,
        uSkaterSolo,
        uSkaterParent,
        uSkaterPair,
        uSkaterCoach,
        activeCoach,
        org_Club_Name,
        org_Club_Join_Date,
        org_USFSA_number
            ):

        self.date_created = date_created
        self.uSkaterUUID = uSkaterUUID
        self.uSkaterFname = uSkaterFname
        self.uSkaterMname = uSkaterMname
        self.uSkaterLname = uSkaterLname
        self.uSkaterZip = uSkaterZip
        self.uSkaterCity = uSkaterCity
        self.uSkaterState = uSkaterState
        self.uSkaterCountry = uSkaterCountry
        self.uSkaterComboIce = uSkaterComboIce
        self.uSkaterComboOff = uSkaterComboOff
        self.uSkaterRinkPref = uSkaterRinkPref
        self.uSkaterMaintPref = uSkaterMaintPref
        self.uSkaterSolo = uSkaterSolo
        self.uSkaterParent = uSkaterParent
        self.uSkaterPair = uSkaterPair
        self.uSkaterCoach = uSkaterCoach
        self.activeCoach = activeCoach
        self.org_Club_Name = org_Club_Name
        self.org_Club_Join_Date = org_Club_Join_Date
        self.org_USFSA_number = org_USFSA_number


class uSkateConfig():
    '''
    This table describes a pair of skates, as a combo, per skater.
    A combo contains a set of blades, and a set of boots.

    By default, there should be a 'rental' skate config available
    to evey user, for new skaters that havent purchased skates yet.

    sConfigType is a key for ice skates vs roller/pic/box skates.
    sConfigActiveID is determines if a combo is currently in use.
    uConfigActice specifies what user (uSkaterUUID) owns the config

    Every field is required for this to work correctly, but is all
    either true/false or foreign key data except for the date.
    '''

    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime)
    uSkaterUUID = Column(Integer)
    uSkaterBladesID = Column(Integer)
    uSkaterBootsID = Column(Integer)
    sConfigType = Column(Integer)
    sConfigActiveID = Column(Integer)
    uConfigActive = Column(Integer)

    def __init__(
        self,
        date_created,
        uSkaterUUID,
        uSkaterBladesID,
        uSkaterBootsID,
        sConfigType,
        sConfigActiveID,
        uConfigActive
    ):

        self.date_created = date_created
        self.uSkaterUUID = uSkaterUUID
        self.uSkaterBladesID = uSkaterBladesID
        self.uSkaterBootsID = uSkaterBootsID
        self.sConfigType = sConfigType
        self.sConfigActiveID = sConfigActiveID
        self.uConfigActive = uConfigActive


class uSkaterBlades():
    '''
    This table contains all data we would ever want to have about blades.
    Where did they come from, where did they go, and how much did it cost us.
    ID's are for foreign keys, so that any boot and can be used with any blade
    '''

    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime)
    bladesID = Column(Integer)
    bladesName = Column(String)
    bladesModel = Column(String)
    bladesSize = Column(String)
    bladesPurchaseAmount = Column(Float)
    uSkaterUUID = Column(Integer)

    def __init__(
        self,
        date_created,
        bladesID,
        bladesName,
        bladesModel,
        bladesSize,
        bladesPurchaseAmount,
        uSkaterUUID
            ):

        self.date_created = date_created
        self.bladesID = bladesID
        self.bladesName = bladesName
        self.bladesModel = bladesModel
        self.bladesSize = bladesSize
        self.bladesPurchaseAmount = bladesPurchaseAmount
        self.uSkaterUUID = uSkaterUUID


class uSkaterBoots():
    '''
    This table contains all data we would ever want to have about boots.
    Where did they come from, where did they go, and how much did it cost us.
    ID's are for foreign keys, so that any boot and can be used with any blade
    '''

    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime)
    bootsID = Column(Integer)
    bootsName = Column(String)
    bootsModel = Column(String)
    bootsSize = Column(String)
    bootsPurchaseAmount = Column(Float)
    uSkaterUUID = Column(Integer)

    def __init__(
        self,
        date_created,
        bootsID,
        bootsName,
        bootsModel,
        bootsSize,
        bootsPurchaseAmount,
        uSkaterUUID
            ):

        self.date_created = date_created
        self.bootsID = bootsID
        self.bootsName = bootsName
        self.bootsModel = bootsModel
        self.bootsSize = bootsSize
        self.bootsPurchaseAmount = bootsPurchaseAmount
        self.uSkaterUUID = uSkaterUUID


class events_competition():
    '''
    This table should describe a competition, though the legacy installation
    isn't clear about what data should be here. Use with caution.
    '''

    id = Column(Integer, primary_key=True)
    event_date = Column(DateTime)
    event_type = Column(Integer)
    event_cost = Column(Float)
    event_location = Column(Integer)
    config_id = Column(Integer)
    routine_id = Column(Integer)
    award_level = Column(Integer)
    award_points = Column(Integer)
    uSkaterUUID = Column(Integer)

    def __init__(
        self,
        event_date,
        event_type,
        event_cost,
        event_location,
        config_id,
        routine_id,
        award_level,
        award_points,
        uSkaterUUID,
            ):

        self.event_date = event_date
        self.event_type = event_type
        self.event_cost = event_cost
        self.event_location = event_location
        self.config_id = config_id
        self.routine_id = routine_id
        self.award_level = award_level
        self.award_points = award_points
        self.uSkaterUUID = uSkaterUUID


class event_performance():
    '''
    This table should describe any kind of informal or unscanctioned
    performance. Showcases and seasonal shows are a great example of this.
    '''

    id = Column(Integer, primary_key=True)
    performance_date = Column(DateTime)
    performance_type = Column(Integer)
    performance_cost = Column(Float)
    performance_location = Column(Integer)
    config_id = Column(Integer)
    routine_id = Column(Integer)
    award_level = Column(Integer)
    award_points = Column(Integer)
    uSkaterUUID = Column(Integer)

    def __init__(
        self,
        performance_date,
        performance_type,
        performance_cost,
        performance_location,
        config_id,
        routine_id,
        award_level,
        award_points,
        uSkaterUUID,
            ):

        self.performance_date = performance_date
        self.performance_type = performance_type
        self.performance_cost = performance_cost
        self.performance_location = performance_location
        self.config_id = config_id
        self.routine_id = routine_id
        self.award_level = award_level
        self.award_points = award_points
        self.uSkaterUUID = uSkaterUUID


class event_test():
    '''
    This table describes any testing done by a skater.
    '''

    id = Column(Integer, primary_key=True)
    test_date = Column(DateTime)
    test_type = Column(Integer)
    test_cost = Column(Float)
    test_location = Column(Integer)
    config_id = Column(Integer)
    routine_id = Column(Integer)
    award_level = Column(Integer)
    award_points = Column(Integer)
    uSkaterUUID = Column(Integer)

    def __init__(
        self,
        test_date,
        test_type,
        test_cost,
        test_location,
        config_id,
        routine_id,
        award_level,
        award_points,
        uSkaterUUID,
            ):

        self.test_date = test_date
        self.test_type = test_type
        self.test_cost = test_cost
        self.test_location = test_location
        self.config_id = config_id
        self.routine_id = routine_id
        self.award_level = award_level
        self.award_points = award_points
        self.uSkaterUUID = uSkaterUUID


class j_notes():
    '''
    This table is for session notes.
    '''

    id = Column(Integer, primary_key=True)
    notes_date = Column(DateTime)
    notes = Column(String)
    uSkaterUUID = Column(Integer)

    def __init__(self, notes_date, notes, uSkaterUUID):
        self.notes_date = notes_date
        self.notes = notes
        self.uSkaterUUID = uSkaterUUID


class j_video():
    '''
    This table is for storing info about where to find video for a session.
    There is no download here, only storage of links, name, platform, etc
    '''

    id = Column(Integer, primary_key=True)
    video_date = Column(DateTime)
    video_url = Column(String)
    video_platform = Column(String)
    video_type = Column(String)
    video_name = Column(String)
    uSkaterUUID = Column(Integer)

    def __init__(
        self,
        video_date,
        video_url,
        video_platform,
        video_type,
        video_name,
        uSkaterUUID
            ):

        self.video_date = video_date
        self.video_url = video_url
        self.video_platform = video_platform
        self.video_type = video_type
        self.video_name = video_name
        self.uSkaterUUID = uSkaterUUID


class uSkaterMaint():
    id = Column(Integer, primary_key=True)
    m_date = Column(DateTime)
    m_hours_on = Column(Integer)
    m_cost = Column(Float)
    m_location = Column(Integer)
    m_notes = Column(String)
    m_roh = Column(Integer)
    uSkateConfig = Column(Integer)
    uSkaterUUID = Column(Integer)

    def __init__(
        self,
        m_date,
        m_hours_on,
        m_cost,
        m_location,
        m_notes,
        uSkateConfig,
        uSkaterUUID,
            ):

        self.m_date = m_date
        self.m_hours_on = m_hours_on
        self.m_cost = m_cost
        self.m_location = m_location
        self.m_notes = m_notes
        self.uSkateConfig = uSkateConfig
        self.uSkaterUUID = uSkaterUUID


class uSkaterEquipManifest():
    '''
    This table keeps track of items purchased along the skater's jouney
    excluding boots and blades.  This is a good place for things like
    tights, gloves, bags and other associated items that don't really
    have specified lifetimes but may need replaced or even avoided in the
    future.
    '''

    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime)
    equip_manufacturer = Column(String)
    equip_model = Column(String)
    equip_notes = Column(String)
    equip_size = Column(String)
    equip_color = Column(String)
    equip_vendor = Column(String)
    equip_cost = Column(Float)
    equip_url = Column(String)
    uSkaterUUID = Column(Integer)

    def __init__(
        self,
        date_created,
        equip_manufacturer,
        equip_model,
        equip_notes,
        equip_size,
        equip_color,
        equip_vendor,
        equip_cost,
        uSkaterUUID
            ):

        self.date_created = date_created
        self.equip_manufacturer = equip_manufacturer
        self.equip_model = equip_model
        self.equip_notes = equip_notes
        self.equip_size = equip_size
        self.equip_color = equip_color
        self.equip_vendor = equip_vendor
        self.equip_cost = equip_cost
        self.uSkaterUUID = uSkaterUUID


class punch_cards():
    '''
    This table tracks punch cards if rinks have them.  In some cases, a rink
    may allow one punch for unlimited minutes or one punch may be for a set
    amount of time such as 30 minutes or an hour.

    This data is to assist in knowing how much money has been spent on
    cards/time and how many punches remain on the card.
    '''

    id = Column(Integer, primary_key=True)
    date_created = Column(DateTime)
    punch_time = Column(Integer)
    punch_cost = Column(Float)
    punch_location = Column(Integer)
    uSkaterUUID = Column(Integer)

    def __init__(
        self,
        date_created,
        punch_time,
        punch_cost,
        punch_location,
        uSkaterUUID
            ):

        self.date_created = date_created
        self.punch_time = punch_time
        self.punch_cost = punch_cost
        self.punch_location = punch_location
        self.uSkaterUUID = uSkaterUUID


class skate_camp():
    '''
    This table tracks meta data regarding a skate camp.
    Currently mostly used for cost tracking but will
    likely evovle into something useful later.
    '''

    id = Column(Integer, primary_key=True)
    location_id = Column(Integer)
    camp_cost = Column(Float)
    camp_name = Column(String)
    date_start = Column(DateTime)
    date_end = Column(DateTime)
    uSkaterUUID = Column(Integer)

    def __init__(
        self,
        location_id,
        camp_cost,
        camp_name,
        date_start,
        date_end,
        uSkaterUUID
            ):

        self.location_id = location_id
        self.camp_cost = camp_cost
        self.camp_name = camp_name
        self.date_start = date_start
        self.date_end = date_end
        self.uSkaterUUID = uSkaterUUID


class club_membership():
    '''
    This table tracks data regarding club memberships. Currently, the club
    name is manually entered, but there is a possiblity that it can be moved
    to the same type of setup that we're going to be doing with the
    location/icemaker project where things are ID based on another table.
    Since this is mostly used for cost tracking, this method still works.
    '''

    id = Column(Integer, primary_key=True)
    location_id = Column(Integer)
    club_cost = Column(Float)
    club_name = Column(String)
    date_start = Column(DateTime)
    date_end = Column(DateTime)
    uSkaterUUID = Column(Integer)

    def __init__(
        self,
        location_id,
        club_cost,
        club_name,
        date_start,
        date_end,
        uSkaterUUID
            ):

        self.location_id = location_id
        self.club_cost = club_cost
        self.club_name = club_name
        self.date_start = date_start
        self.date_end = date_end
        self.uSkaterUUID = uSkaterUUID


class skate_school():
    '''
    This table tracks things like LearnToSkate classes and the relevant
    metadata, used mostly for cost tracking at this time
    '''

    id = Column(Integer, primary_key=True)
    location_id = Column(Integer)
    class_cost = Column(Float)
    class_name = Column(String)
    date_start = Column(DateTime)
    date_end = Column(DateTime)
    uSkaterUUID = Column(Integer)

    def __init__(
        self,
        location_id,
        class_cost,
        class_name,
        date_start,
        date_end,
        uSkaterUUID
            ):

        self.location_id = location_id
        self.class_cost = class_cost
        self.class_name = class_name
        self.date_start = date_start
        self.date_end = date_end
        self.uSkaterUUID = uSkaterUUID

from sqlalchemy import Column, String, Integer, DateTime, UUID, text
from sqlalchemy.dialects.postgresql import JSONB

from .base import Base


class uSkaterConfig(Base):
    '''
    Contains data about the skater specifically, including preferences.
    The uSkaterUUID drives most of this app, it connects literally every
    row and piece of data together to show hours and costs for any specific
    part of the skating journey.
    '''

    __tablename__ = 'uSkaterConfig'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    
    # who meta
    date_created = Column(DateTime)
    uSkaterUUID = Column(UUID, unique=True)
    uSkaterFname = Column(String)
    uSkaterMname = Column(String)
    uSkaterLname = Column(String)
    uSkaterZip = Column(Integer)
    uSkaterCity = Column(String)
    uSkaterState = Column(String)
    uSkaterCountry = Column(String)
    uSkaterRoles = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
    
    #equip configs
    uSkaterComboIce = Column(UUID, unique=True)
    uSkaterComboOff = Column(UUID, unique=True)
    uSkaterRinkPref = Column(UUID)
    uSkaterMaintPref = Column(Integer)
    
    #training meta
    activeCoach = Column(UUID)
    org_Club = Column(UUID)
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
        uSkaterRoles,
        uSkaterComboIce,
        uSkaterComboOff,
        uSkaterRinkPref,
        uSkaterMaintPref,
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
        self.uSkaterRoles = uSkaterRoles
        self.uSkaterComboIce = uSkaterComboIce
        self.uSkaterComboOff = uSkaterComboOff
        self.uSkaterRinkPref = uSkaterRinkPref
        self.uSkaterMaintPref = uSkaterMaintPref
        self.activeCoach = activeCoach
        self.org_Club_Name = org_Club_Name
        self.org_Club_Join_Date = org_Club_Join_Date
        self.org_USFSA_number = org_USFSA_number


class SkaterType(Base):
    """
    This table should hold various types of skater roles. An adult skater may
    also be other types, such as a coach AND guardian. To grow these columns, 
    simply add the name and mark the column as a boolean
    
    Starting options:
    1: Adult - Regular Smegular
    2: Coach - Probably also an adult skater, but specifically a coach
    3: Minor - Under 18, requires guardian representation and care
    4: Guardian - Maybe not a skater, but a parent of one or more.
    """

    __tablename__ = 'u_skater_types'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    label = Column(String)

    def __init__(
        self,
        label
            ):

        self.label = label
    
    def __repr__(self):
        return f"<SkaterType(id={self.id}, label={self.label})>"
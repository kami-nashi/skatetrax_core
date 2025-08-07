from sqlalchemy import Column, String, Integer, DateTime, UUID
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
    date_created = Column(DateTime)
    uSkaterUUID = Column(UUID, unique=True)
    uSkaterFname = Column(String)
    uSkaterMname = Column(String)
    uSkaterLname = Column(String)
    uSkaterZip = Column(Integer)
    uSkaterCity = Column(String)
    uSkaterState = Column(String)
    uSkaterCountry = Column(String)
    uSkaterComboIce = Column(UUID, unique=True)
    uSkaterComboOff = Column(UUID, unique=True)
    uSkaterRinkPref = Column(UUID)
    uSkaterMaintPref = Column(Integer)
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
        self.uSkaterComboIce = uSkaterComboIce
        self.uSkaterComboOff = uSkaterComboOff
        self.uSkaterRinkPref = uSkaterRinkPref
        self.uSkaterMaintPref = uSkaterMaintPref
        self.activeCoach = activeCoach
        self.org_Club_Name = org_Club_Name
        self.org_Club_Join_Date = org_Club_Join_Date
        self.org_USFSA_number = org_USFSA_number

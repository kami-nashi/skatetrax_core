from sqlalchemy import Column, DateTime, Integer, String
from .base import Base


class Locations(Base):
    __tablename__ = 'locations'
    __table_args__ = {'extend_existing': True}

    rink_id = Column(Integer, primary_key=True)
    rink_name = Column(String)
    rink_address = Column(String)
    rink_city = Column(String)
    rink_state = Column(String)
    rink_country = Column(String)
    rink_url = Column(String)
    rink_phone = Column(String)
    data_source = Column(String)
    date_created = Column(DateTime)

    def __init__(
        self,
        rink_id,
        rink_name,
        rink_address,
        rink_city,
        rink_state,
        rink_country,
        rink_url,
        rink_phone,
        data_source,
        date_created
            ):

        self.rink_id = rink_id
        self.rink_name = rink_name
        self.rink_address = rink_address
        self.rink_city = rink_city
        self.rink_state = rink_state
        self.rink_country = rink_country
        self.rink_url = rink_url
        self.rink_phone = rink_phone
        self.data_source = data_source
        self.date_created = date_created

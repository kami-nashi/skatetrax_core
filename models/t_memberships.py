from sqlalchemy import Column, Float, Integer, DateTime, String, ForeignKey, UUID
from sqlalchemy.orm import mapped_column, Mapped
from uuid import uuid4, UUID as UUIDV4
from .base import Base


class Club_Membership(Base):
    '''
    This table tracks data regarding club memberships. Currently, the club
    name is manually entered, but there is a possiblity that it can be moved
    to the same type of setup that we're going to be doing with the
    location/icemaker project where things are ID based on another table.
    Since this is mostly used for cost tracking, this mechanism still works.
    '''

    __tablename__ = 'club_membership'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(UUID)
    club_home_rink = Column(UUID, ForeignKey("locations.rink_id", ondelete='CASCADE'))
    club_cost = Column(Float)
    club_name = Column(String)

    def __init__(
        self,
        club_id,
        club_home_rink,
        club_cost,
        club_name
            ):

        self.club_id = club_id
        self.club_home_rink = club_home_rink
        self.club_cost = club_cost
        self.club_name = club_name


class Club_Members(Base):
    __tablename__ = 'club_members'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(UUID)
    uSkaterUUID = Column(UUID, ForeignKey("uSkaterConfig.uSkaterUUID", ondelete='CASCADE'))
    joined_date = Column(DateTime, nullable=True)
    membership_fee = Column(Float)
    
    def __init__(self, club_id, uSkaterUUID, joined_date, membership_fee):
        self.club_id = club_id
        self.uSkaterUUID = uSkaterUUID
        self.joined_date = joined_date
        self.membership_fee = membership_fee

    def __repr__(self):
        return f"<Club_Member skater={self.uSkaterUUID} club={self.club_id}>"

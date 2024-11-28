from models.cyberconnect2 import engine
from .base import Base

# import table models to be created
# start with basic needs for functionality
from .t_ice_time import Ice_Time
from .t_icetype import IceType
from .t_locations import Locations, Punch_cards
from .t_skaterMeta import uSkaterConfig

# items for configuring skates, cost of gear
from .t_equip import uSkateConfig, uSkaterBlades, uSkaterBoots, uSkaterEquipManifest

# coaching data
from .t_coaches import Coaches

# maintenance
from .t_maint import uSkaterMaint

# memberships (USFSA)
from .t_memberships import Club_Membership

# camps, LTS, multiweek series
from .t_classes import Skate_Camp, Skate_School

# competitions, tests, etc
from .t_events import Event_Test, Events_Competition, Event_Performance

# last, import supporting tables for things like notes, videos
from .t_journal import Journal_Notes, Journal_Videos


if __name__ == "__main__":
    Base.metadata.create_all(engine)

    # we know that some tables need default starting data
    # so lets populate those
    # IceType should have some default sessions listed
    # Boots, Blades, Config should contain at least a rental setting
    # Locations table should have at least the rinks in the user's state
    # uSkaterConfig should have a nearby rink suggested

# to create, run: python -m models.setup_db

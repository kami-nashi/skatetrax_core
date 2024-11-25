from models.cyberconnect2 import engine
from .base import Base

# import table models to be created
from .t_icetype import IceType
from .t_locations import Locations
from .t_ice_time import Ice_Time
from .t_coaches import Coaches
from .t_equip_skates import uSkateConfig, uSkaterBlades, uSkaterBoots

if __name__ == "__main__":
    Base.metadata.create_all(engine)

# to create, run: python -m models.setup_db

from models.cyberconnect2 import engine
from .base import Base

# import table models to be created
from .t_icetype import IceType
from .t_locations import Locations
from .t_ice_time import Ice_Time


if __name__ == "__main__":
    Base.metadata.create_all(engine)

# to create, run: python -m models.setup_db

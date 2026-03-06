import argparse
#from models import coaches, locations, insert_data, equipment

from skatetrax.models.ops.pencil import (Location_Data, Coach_Data, User_Data,
                                         Club_Data, Event_Data)

from skatetrax.models.cyberconnect2 import engine
from datetime import datetime, timezone
from .base import Base

# import table models to be created
# start with basic needs for functionality
from .t_auth import uAuthTable
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

# skate club directory and memberships
from .t_memberships import Club_Directory, Club_Members

# camps, LTS, multiweek series
from .t_classes import Skate_Camp, Skate_School

# events (competitions, showcases, exhibitions) and scoring
from .t_events import (GoverningBody, EventType, SkaterEvent, EventEntry,
                       Score6_0, ScoreCJS, ScoreIJSComponent, ScoreIJSElement,
                       EventDeduction, ImportLog)

#Import table for skating tests
from .t_tests import Event_Test

# last, import supporting tables for things like notes, videos
from .t_journal import Journal_Notes, Journal_Videos


date_created = datetime.now(timezone.utc)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate or Delete Default data and tables')
    parser.add_argument('-c','--create', action='store_true', help='Create tables, then insert defaults')
    parser.add_argument('-d','--drop', action='store_true', help='Drop all tables. The end.')
    args = parser.parse_args()

    if args.create:
        # code here

        Base.metadata.create_all(engine)

        # we know that some tables need default starting data for all users
        ice_types = [
            {'ice_type_id': 'dc812842-a9a9-4902-b680-361420baffe5', 'ice_type': 'Free Style (Walk On)'},
            {'ice_type_id': 'cedbb4e9-ab5b-4a14-a273-fd9783aaac86', 'ice_type': 'Public'},
            {'ice_type_id': '12208eeb-9ffe-4ac3-90d3-976741a34249', 'ice_type': 'Coaching Session'},
            {'ice_type_id': '7a3b3441-04d6-4b5a-afb6-eb556022c2e7', 'ice_type': 'Competition'},
            {'ice_type_id': '88f87085-927d-4b77-b1c9-77d6de7c2d28', 'ice_type': 'Performance'},
            {'ice_type_id': 'e48d17a7-d092-4320-8e5b-6670d57b104b', 'ice_type': 'Club Ice'},
            {'ice_type_id': 'db32094e-9b0d-42a5-b87f-cd47729b6c65', 'ice_type': 'Group Class'},
            {'ice_type_id': '0bcb0d7a-f5f0-41e2-bccb-78e80eb6673f', 'ice_type': 'Free Style (Punch Card)'},
            {'ice_type_id': 'a2250306-a238-4ff3-b772-ae86cbda0d7c', 'ice_type': 'Off Ice - Concrete or Asphalt'},
            {'ice_type_id': '43cae2d2-909c-47a1-ac7d-a1a923c25d4e', 'ice_type': 'Off Ice - Rink'}
        ]

        default_coaches = [
            {
                'coach_Fname': '-',
                'coach_Lname': '-',
                'coach_rate': '0',
                'coach_id': '487d43b5-0a4d-4dc4-8cc2-ab06870a10bf',
                'coach_phone': None,
                'coach_email': None,
                'coach_ijs_id': None,
                'coach_usfsa_id': None,
                'uSkaterUUID': None
                }
        ]

        default_clubs = [
            {
                'club_id': 'c4dd2b9c-50f1-4f5b-a439-fd8f36a654d6',
                'club_name': 'No Club',
                'club_home_rink': None,
                'club_cost': 0
            }
        ]

        default_locations = [
            {
                'rink_id': 'b261166b-9e7c-4a96-ab06-ec630deb3321',
                'rink_name': 'Off Ice',
                'rink_address': '-',
                'rink_city': '-',
                'rink_state': '-',
                'rink_country': '-',
                'rink_zip': '00000',
                'rink_url': '-',
                'rink_phone': '-',
                'rink_tz': None,
                'data_source': 'skatetrax',
                'date_created': date_created
            }
        ]

        governing_bodies = [
            {'id': 'a0000000-0000-0000-0000-000000000001', 'short_name': 'None', 'full_name': 'Unaffiliated'},
            {'id': 'a0000000-0000-0000-0000-000000000002', 'short_name': 'USFSA', 'full_name': 'U.S. Figure Skating Association'},
            {'id': 'a0000000-0000-0000-0000-000000000003', 'short_name': 'ISI', 'full_name': 'Ice Sports Industry'},
            {'id': 'a0000000-0000-0000-0000-000000000004', 'short_name': 'Other', 'full_name': 'Other'},
        ]

        event_types = [
            {'id': 'b0000000-0000-0000-0000-000000000001', 'category': 'Competition', 'scoring_system': '6.0', 'governing_body_id': 'a0000000-0000-0000-0000-000000000002'},
            {'id': 'b0000000-0000-0000-0000-000000000002', 'category': 'Competition', 'scoring_system': '6.0', 'governing_body_id': 'a0000000-0000-0000-0000-000000000001'},
            {'id': 'b0000000-0000-0000-0000-000000000003', 'category': 'Showcase', 'scoring_system': 'CJS', 'governing_body_id': 'a0000000-0000-0000-0000-000000000002'},
            {'id': 'b0000000-0000-0000-0000-000000000004', 'category': 'Showcase', 'scoring_system': None, 'governing_body_id': 'a0000000-0000-0000-0000-000000000001'},
            {'id': 'b0000000-0000-0000-0000-000000000005', 'category': 'Exhibition', 'scoring_system': None, 'governing_body_id': 'a0000000-0000-0000-0000-000000000001'},
            {'id': 'b0000000-0000-0000-0000-000000000006', 'category': 'Competition', 'scoring_system': 'IJS', 'governing_body_id': 'a0000000-0000-0000-0000-000000000002'},
        ]

        Location_Data.add_ice_type(ice_types)
        Location_Data.add_ice_rink(default_locations)
        Coach_Data.add_coaches(default_coaches)
        Club_Data.add_club(default_clubs)
        Event_Data.add_governing_bodies(governing_bodies)
        Event_Data.add_event_types(event_types)

    if args.drop:
        Base.metadata.drop_all(bind=engine)

# to create, run: python -m models.setup_db -c
# to drop all, run: python -m models.setup_db -d

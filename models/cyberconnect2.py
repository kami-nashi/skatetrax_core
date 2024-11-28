from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os


db_url = os.environ['pgdb_host']
db_name = os.environ['pgdb_name']
db_user = os.environ['pgdb_user']
passwd = os.environ['pgdb_password']

engine = create_engine(f'postgresql://{db_user}:{passwd}@{db_url}/{db_name}')
Session = sessionmaker(bind=engine)

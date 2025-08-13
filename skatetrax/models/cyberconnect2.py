from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

db_url = os.environ.get('PGDB_HOST', -1)
db_name = os.environ.get('PGDB_NAME', -1)
db_user = os.environ.get('PGDB_USER', -1)
passwd = os.environ.get('PGDB_PASSWORD', -1)

engine = create_engine(f'postgresql://{db_user}:{passwd}@{db_url}/{db_name}')
Session = sessionmaker(bind=engine)


def check_db_health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"DB health check failed: {e}")
        return False

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from djangoproject.constants import Constants
from urllib.parse import quote_plus

constants = Constants()

def create_engine_and_session(database='financeApp'):
    conn_info = constants.get_conn_info(database)
    engine = create_engine(
        f"""mysql+mysqlconnector://{conn_info["user"]}:{quote_plus(conn_info["password"])}@{conn_info["host"]}:{conn_info["port"]}/{conn_info["database"]}""",
        pool_size=1
    )

    Session = sessionmaker(bind=engine)

    return Session
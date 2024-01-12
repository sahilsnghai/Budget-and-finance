from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lumenore_apps.constants import Constants
from urllib.parse import quote_plus

constants = Constants()


def create_engine_and_session(database="financeApp"):
    """create_engine_and_session Session

    Args:
        database (str, optional): Defaults to 'financeApp'.

    Returns:
        session: Session Object
    """
    conn_info = constants.get_conn_info(database)
    engine = create_engine(
        f"""mysql+mysqlconnector://{conn_info["user"]}:{quote_plus(conn_info["password"])}@{conn_info["host"]}:{conn_info["port"]}/{conn_info["database"]}""",
        pool_size=1,
    )

    session = sessionmaker(bind=engine)

    constants.engine = engine
    constants.session = session
    return session

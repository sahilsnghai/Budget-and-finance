# Copyright © Lumenore Inc. All rights reserved.
# This software is the confidential and proprietary information of
# Lumenore Inc. "Confidential Information".
# You shall * not disclose such Confidential Information and shall use it only in
# accordance with the terms of the intellectual property agreement
# you entered into with Lumenore Inc.
# THIS SOFTWARE IS INTENDED STRICTLY FOR USE BY Lumenore Inc.
# AND ITS PARENT AND/OR SUBSIDIARY COMPANIES. Lumenore
# MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY OF THE SOFTWARE,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.
# Lumenore SHALL NOT BE LIABLE FOR ANY DAMAGES SUFFERED BY ANY PARTY AS A RESULT
# OF USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

"""db.py"""

from sqlalchemy import create_engine, engine as Engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
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
    config = constants.get_conn_info(database)
    driver = config.pop('driver')
    connector = None

    if 'mysql' in driver:
        connector = 'mysql+mysqlconnector'
    if config.get("warehouse"):
        engine_str = Engine.URL.create(drivername=connector,
                                    username=config["userName"],
                                    password=config["password"],
                                    host=config["host"],
                                    port=config["port"],
                                    database=config["schema"],
                                    warehouse=config["warehouse"])
    else:
        engine_str = Engine.URL.create(drivername=connector,
                                    username=config["user"],
                                    password=config["password"],
                                    host=config["host"],
                                    port=config["port"],
                                    database=config["database"])


    engine = create_engine(url=engine_str, pool_pre_ping=True, pool_recycle=3600)
    session = scoped_session(sessionmaker(bind=engine))

    constants.engine = engine
    constants.session = session
    return session

def create_async_session(database: str ="financeApp") -> AsyncSession:
    '''create_async_session _summary_

    Args:
        database_url (str): _description_

    Returns:
        AsyncSession: _description_

    Yields:
        Iterator[AsyncSession]: _description_
    '''
    config = constants.get_conn_info(database)
    driver = config.pop('driver')
    connector = None

    if 'mysql' in driver:
        connector = 'mysql+aiomysql'
    if config.get("warehouse"):
        engine_str = Engine.URL.create(drivername=connector,
                                    username=config["userName"],
                                    password=config["password"],
                                    host=config["host"],
                                    port=config["port"],
                                    database=config["schema"],
                                    warehouse=config["warehouse"])
    else:
        engine_str = Engine.URL.create(drivername=connector,
                                    username=config["user"],
                                    password=config["password"],
                                    host=config["host"],
                                    port=config["port"],
                                    database=config["database"])
    engine_str = create_async_engine(engine_str)
    async_session = async_sessionmaker(
        bind=engine_str, class_=AsyncSession, expire_on_commit=False
    )
    return async_session

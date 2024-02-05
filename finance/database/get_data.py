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

"""get_data"""

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, case, func, literal, desc, update
from lumenore_apps.main_logger import set_up_logging
from time import perf_counter
from threading import Thread
from .db import create_engine_and_session, create_async_session
from .models import FnForm, FnUserData, FnScenario, FnScenarioData, JwtSettings

Session = create_engine_and_session()
logger = set_up_logging()


SELECT_SENARIO_ITEMS = (
        FnScenarioData.fn_scenario_data_id.label("data_id"),
        func.DATE_FORMAT(FnScenarioData.date, "%Y%m%d").label("Date"),
        FnScenarioData.receipt_number.label("Receipt Number"),
        FnScenarioData.business_unit.label("Business Unit"),
        FnScenarioData.account_type.label("Account Type"),
        FnScenarioData.account_subtype.label("Account SubType"),
        FnScenarioData.project_name.label("Project Name"),
        case(
            (FnScenarioData.amount_type == 1, "Actual"),
            (FnScenarioData.amount_type == 0, "Budget"),
            else_="Unknown",
        ).label("Amount Type"),
        func.round(
            FnScenarioData.amount * (FnScenarioData.change_value / 100 + 1),
            3,
        ).label("Amount"),
        FnScenarioData.amount.label("base value"),
        FnScenarioData.customer_name.label("Customer Name"),
        FnScenarioData.change_value.label("changePrecentage"),
        case(
            (func.extract("month", FnScenarioData.date) == 1, "January"),
            (func.extract("month", FnScenarioData.date) == 2, "February"),
            (func.extract("month", FnScenarioData.date) == 3, "March"),
            (func.extract("month", FnScenarioData.date) == 4, "April"),
            (func.extract("month", FnScenarioData.date) == 5, "May"),
            (func.extract("month", FnScenarioData.date) == 6, "June"),
            (func.extract("month", FnScenarioData.date) == 7, "July"),
            (func.extract("month", FnScenarioData.date) == 8, "August"),
            (func.extract("month", FnScenarioData.date) == 9, "September"),
            (func.extract("month", FnScenarioData.date) == 10, "October"),
            (func.extract("month", FnScenarioData.date) == 11, "November"),
            (func.extract("month", FnScenarioData.date) == 12, "December"),
            else_="",
        ).label("Month")
)


def receive_query(query):
    """

    Parameters
    ----------
    query

    Returns
    -------

    """
    return [row._asdict() for row in query]


async def create_form(form_name, lum_user_id, lum_org_id, session):
    """Create Entry in fn_form

    Args:
        form_name (int):
        lum_user_id (int):
        lum_org_id (int):

    Returns:
        formid :int
    """
    form_name = form_name.split(".")[0]
    formid = None
    try:
        logger.info("creating form")
        (
            session.execute(
                    update(FnForm)
                    .values({"is_active": False})
                    .where(
                        and_(
                            FnForm.lum_org_id == lum_org_id,
                            FnForm.created_by == lum_user_id
                        )
                    )
                )
        )

        form_instance = FnForm(
            form_name=form_name,
            lum_user_id=lum_user_id,
            lum_org_id=lum_org_id,
            created_by=lum_user_id,
            modified_by=lum_user_id,
        )
        session.add(form_instance)
        session.commit()
        logger.info(f"Form saved with ID: {form_instance.fn_form_id}")
        formid = form_instance.fn_form_id
    except SQLAlchemyError as e:
        logger.exception(f"Error saving form: {e}")
    except Exception as e:
        logger.exception(f"Error in SQL ORM: {e}")
    return formid


async def create_user_data(df, formid, session):
    """Create Entry in fn_user_data

    Args:
        df (Database):
        formid (int):
        userid (int):

    Returns:
        user_data: [{......}]
    """
    try:
        logger.info("Updating user data")
        df = df.dropna()
        data = df.to_dict(orient="records")

        session.bulk_insert_mappings(FnUserData, data)
        session.commit()

        logger.info(
            f"User data saved with ID : {formid}"
        )
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error saving user data.: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL ORM: {e}")
    finally:
        session.close()


def fetch_from(userid, orgid):
    """Fetch form data

    Args:
        userid (int):
        orgid (int):

    Returns:
        form names: [{...}]
    """
    form_names = {}
    try:
        logger.info(f"Fetching forms for user {userid}")
        with Session() as session:
            form_names = receive_query(
                session.query(
                    FnForm.form_name.label("filename"),
                    FnForm.fn_form_id.label("formid"),
                )
                .filter(
                    FnForm.lum_user_id == userid,
                    FnForm.lum_org_id == orgid,
                    FnForm.is_active == True,
                )
                .order_by(desc(FnForm.fn_form_id))
                .limit(1)
                .all()
            )
            logger.info(f"Form_name for user {userid}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error fetching form: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL ORM: {e}")
    finally:
        session.close()
    return form_names


def fetch_scenario(formid, userid):
    """fetch scenarios

    Args:
        formid (int):
        userid (int):

    Returns:
        scenario_names: [{......}]
    """
    scenario_names = {}
    try:
        logger.info(f"fetch scenario for form id {formid} and user {userid}")
        with Session() as session:
            scenario_names = receive_query(
                session.query(
                    FnScenario.fn_scenario_id.label("scenarioid"),
                    FnScenario.scenario_description.label("scenario_description"),
                    FnScenario.scenario_name.label("scenario_name"),
                    FnScenario.is_active.label("scenario_status"),
                )
                .join(
                    FnScenarioData,
                    FnScenario.fn_scenario_id == FnScenarioData.fn_scenario_id,
                )
                .group_by(FnScenario.fn_scenario_id)
                .filter(
                    FnScenario.fn_form_id == formid,
                    FnScenario.created_by == userid,
                    FnScenario.is_draft == False,
                    FnScenarioData.is_active == True,
                )
                .all()
            )
            logger.info(f"{len(scenario_names)}")
            logger.info(f"scenario_name for formid {formid} : {len(scenario_names)}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error fetching scenario form: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL ORM: {e}")
    finally:
        session.close()
    return scenario_names


def get_user_data(formid, userid, session=None, created_session=False, **karwgs):
    """fetch user data from fn_user_data

    Args:
        formid (int):
        userid (int):
        session (session object, optional): Defaults to None.
        created_session (bool, optional): Defaults to False.

    Returns:
        user_data: [{....}]
    """
    user_data = {}
    try:
        logger.info(f"getting user data for form id {formid}")

        if session is None:
            session = Session()
            created_session = True

        start = perf_counter()
        if karwgs.get("migrate") is not None:
            common_columns = [
                FnUserData.date,
                FnUserData.receipt_number,
                FnUserData.business_unit,
                FnUserData.account_type,
                FnUserData.account_subtype,
                FnUserData.project_name,
                FnUserData.customer_name,
                FnUserData.amount,
                literal(karwgs.get("scenarioid")).label("fn_scenario_id"),
                FnUserData.created_by,
                FnUserData.modified_by,
                FnUserData.amount_type,
            ]
        else:
            common_columns = [
                func.DATE_FORMAT(FnUserData.date, "%Y%m%d").label("Date"),
                FnUserData.receipt_number.label("Receipt Number"),
                FnUserData.business_unit.label("Business Unit"),
                FnUserData.account_type.label("Account Type"),
                FnUserData.account_subtype.label("Account SubType"),
                FnUserData.project_name.label("Project Name"),
                FnUserData.customer_name.label("Customer Name"),
                FnUserData.amount.label("Amount"),
                case(
                    (FnUserData.amount_type == 1, "Actual"),
                    (FnUserData.amount_type == 0, "Budget"),
                    else_="Unknown",
                ).label("Amount Type"),
            ]

        user_data = receive_query(
            session.query(*common_columns)
            .filter(
                FnUserData.fn_form_id == formid,
                FnUserData.created_by == userid,
            )
            .all()
        )
        logger.info(
            f"got user data for  {len(user_data)} time took {perf_counter() - start}"
        )
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error fetching scenario form: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL ORM: {e}")
        raise ValueError("Error while migrating.")
    finally:
        created_session and session.close()
    return user_data


def filter_column(scenarioid, formid, userid, **kwargs):
    """fetch and filter user scenario data

    Args:
        scenarioid (int):
        formid (int):
        userid (int):

    Returns:
        user_data:[{.....}]
    """
    user_data = {}
    try:
        logger.info(f"getting user data for form id {scenarioid}")
        with Session() as session:
            start = perf_counter()
            query = (
                session.query(
                    *SELECT_SENARIO_ITEMS,
                    (func.extract("year", FnScenarioData.date).label("year")),
                )
                .join(
                    FnScenario,
                    FnScenario.fn_scenario_id == FnScenarioData.fn_scenario_id,
                )
                .filter(
                    FnScenarioData.fn_scenario_id == scenarioid,
                    FnScenarioData.is_active == True,
                    FnScenario.created_by == userid,
                    FnScenario.fn_form_id == formid,
                )
            )
            if kwargs["year"]:
                query = query.filter(
                    func.extract("year", FnScenarioData.date) == kwargs["year"]
                )

            if kwargs["business_unit"] and kwargs["business_unit"].lower() != "all":
                query = query.filter(
                    FnScenarioData.business_unit == kwargs.get("business_unit")
                )

            user_data = receive_query(query.all())
            logger.info(
                f"got user data len {len(user_data)} time took {perf_counter() - start}"
            )
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error filtering columns: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL ORM: {e}")
    finally:
        session.close()
    return user_data


def create_scenario(
    scenario_name,
    scenario_decription,
    formid,
    userid,
    session=None,
    created_session=False,
):
    """Create New Scenario

    Args:
        scenario_name (string):
        scenario_decription (string):
        formid (int):
        userid (int):
        session (session, optional): Defaults to None.
        created_session (bool, optional): Defaults to False.

    Raises:
        Exception:
        e: "Scenario already exits"

    Returns:
        scenarioid: int
        status: bool
    """
    scenarioid = status = None

    try:
        logger.info("creating form")

        if session is None:
            logger.info("Creating Session for new scenario")
            session = Session()
            created_session = True

        scenario_name_list = fetch_scenario(formid=formid, userid=userid)
        scenario_name_list = (
            {item["scenario_name"] for item in scenario_name_list}
            if len(scenario_name_list) > 0
            else ()
        )

        logger.info(scenario_name_list)
        if scenario_name not in scenario_name_list:
            scenario_instance = FnScenario(
                fn_form_id=formid,
                scenario_name=scenario_name,
                scenario_description=scenario_decription,
                created_by=userid,
                modified_by=userid,
            )
            session.add(scenario_instance)
            session.commit()
            logger.info(f"scenario saved with ID: {scenario_instance.fn_scenario_id}")
            scenarioid = scenario_instance.fn_scenario_id
            status = scenario_instance.is_active
        else:
            logger.info(f"found similar. scenario_name for {userid}")
            raise ValueError("Scenario already exists")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error saveing and creating scenario: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL ORM: {e}")
        raise e
    finally:
        created_session and session.close()
    return scenarioid, status


def create_user_data_scenario(
    dataframe, scenarioid, session=None, created_session=False
):
    """Migrate user data from fn_user_data to fn_scenario_data

    Args:
        dataframe (list(dict)):
        scenarioid (ing):
        session (session, optional): Defaults to None.
        created_session (bool, optional): Defaults to False.
    """
    try:
        if session is None:
            session = Session()
            created_session = True

        logger.info("Updating user data")
        start = perf_counter()
        session.bulk_insert_mappings(FnScenarioData, dataframe)
        session.commit()
        logger.info(f"time taken by save scenario is {perf_counter() - start}")
        logger.info(f"User data saved with ID: {scenarioid}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error scenario meta data: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL ORM: {e}")
    finally:
        created_session and session.close()


def get_user_scenario_new(scenarioid, formid, session=None, created_session=False):
    """Fetch user scenario data

    Args:
        scenarioid (int):
        formid (int):
        session (_type_, optional):. Defaults to None.
        created_session (bool, optional):. Defaults to False.

    Returns:
        _type_:
    """
    scenario_data = {}
    try:
        if session is None:
            session = Session()
            created_session = True

        logger.info("fetching user data")
        start = perf_counter()

        scenario_data = receive_query(
            session.query(*SELECT_SENARIO_ITEMS)
            .join(
                FnScenario, FnScenario.fn_scenario_id == FnScenarioData.fn_scenario_id
            )
            .join(FnForm, FnScenario.fn_form_id == FnForm.fn_form_id)
            .filter(
                FnForm.is_active == True,
                FnScenario.fn_form_id == formid,
                FnScenarioData.fn_scenario_id == scenarioid,
                FnScenarioData.is_active == True,
            )
            .all()
        )

        logger.info(f"scenario data {len(scenario_data)}")
        logger.info(f"time taken by fetching scenario is {perf_counter() - start}")
        logger.info(f"User data fetch with ID: {scenarioid} ")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error getting user scenario data: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL ORM: {e}")
    finally:
        created_session and session.close()
    return scenario_data


def update_scenario_percentage(data, filters_list, userid, scenarioid):
    """This function update Change value column in fn_scenario_data.

    Args:
        data (dict):
        filters_list (list):
        userid (int):
        scenarioid (int):
        session (session, optional): Defaults to None.
        created_session (bool, optional): Defaults to False.

    Returns:
        updated_data_list: [{.......}]
    """
    updated_data_list = []

    try:
        logger.info("Session Created")
        session = Session()

        logger.info("Fetching user data")
        start = perf_counter()
        logger.info(f"{data}")

        filters, update = filters_list
        logger.info("Creating Filters")

        filter_conditions = [
            getattr(FnScenarioData, column).ilike(f"{column_value}")
            for column, column_value in filters.items()
        ]

        logger.info("Filters Done")
        logger.info("Creating Dynamic Filters")

        dynamic_filter_condition = and_(
            *filter_conditions,
            FnScenarioData.created_by == userid,
            FnScenarioData.fn_scenario_id == scenarioid,
            FnScenarioData.is_active == True,
        )

        if data.get("date"):
            dynamic_filter_condition = and_(
                dynamic_filter_condition,
                func.date_format(FnScenarioData.date, data.get("dateformat", "%Y"))
                == data["date"],
            )

        logger.info(dynamic_filter_condition)
        logger.info(f"Before Calculation {update['changePrecentage']=}")

        try:
            update = (
                session.query(
                    case(
                        (update['changePrecentage'] == 0, 0.0),
                        (update['changePrecentage'] == -100, -100),
                        else_=((-1 +
                                ((func.sum(
                                    case((FnScenarioData.amount_type == 1,
                                            (FnScenarioData.amount * (FnScenarioData.change_value / 100 + 1))),
                                        else_=0.0)
                                ) +
                                func.sum(
                                    case((FnScenarioData.amount_type == 0,
                                            FnScenarioData.amount), else_=0.0))
                                ) * update['changePrecentage'] -
                                func.sum(
                                    case((FnScenarioData.amount_type == 1,
                                            (FnScenarioData.amount * (FnScenarioData.change_value / 100 + 1))),
                                        else_=0.0))
                                ) /
                                func.sum(
                                    case(
                                        (FnScenarioData.amount_type == 0,
                                            FnScenarioData.amount),
                                            else_=0.0))
                                )

                                * 100)).label("change_value")
                                        ).filter(dynamic_filter_condition)
                                )
            print(update.statement.compile(dialect=session.bind.dialect, compile_kwargs={"literal_binds": True}))
            update = receive_query(update.all())[0]

            logger.info(f"New Update Value {update=}")
            if update["change_value"] is not None:
                logger.info("start updating")
                updated_data = (
                    session.query(FnScenarioData)
                    .filter(
                        dynamic_filter_condition, FnScenarioData.amount_type == 0
                    )
                    .update(update, synchronize_session="fetch")
                )
                logger.info(f"Number of rows updated: {updated_data}")

            session.commit()
        except Exception as e:
            logger.exception(f"Exception while Updating Change Precentage: {e}")
            return

        logger.info("Fetchning data")
        updated_data_list = receive_query(
            session.query(
                *SELECT_SENARIO_ITEMS
            )
            .filter(dynamic_filter_condition)
            .all()
        )
        logger.info(f"Scenario data {len(updated_data_list)}")
        logger.info(f"Time taken by fetching scenario is {perf_counter() - start}")
        logger.info("User data fetch with ID:")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error could not perform SQL query: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL ORM: {e}")
    finally:
        session.close()
    return updated_data_list


def scenario_status_update(
    userid, scenarioid, formid, status, session=None, created_session=False
):
    """Scenario

    Args:
        userid (int):
        scenarioid (int):
        formid (int):
        status (bool):
        session (session, optional): Defaults to None.
        created_session (bool, optional): Defaults to False.

    Returns:
        stmt: int
    """
    stmt = {}
    try:
        if session is None:
            session = Session()
            created_session = True

        start = perf_counter()

        stmt = (
            session.query(FnScenario)
            .filter(
                FnScenario.created_by == userid,
                FnScenario.fn_scenario_id == scenarioid,
                FnScenario.fn_form_id == formid,
            )
            .update({"is_active": status}, synchronize_session="fetch")
        )
        session.commit()

        logger.info(f"Changes Status to {stmt} ")
        logger.info(f"Status Change time {perf_counter() - start}")

    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error updating status : {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL ORM: {e}")
    finally:
        created_session and session.close()
    return stmt


def scenario_data_status_update(
    userid, scenarioid, formid, status, session=None, created_session=False
):
    """scenario_data_status_update

    _extended_summary_

    Args:
        userid (int):
        scenarioid (int):
        formid (int):
        status (bool):
        session (session, optional):. Defaults to None.
        created_session (bool, optional):. Defaults to False.

    Returns:
        _type_:
    """

    stmt = {}
    try:
        if session is None:
            session = Session()
            created_session = True

        start = perf_counter()

        stmt = (
            session.query(FnScenario)
            .filter(
                FnScenario.created_by == userid,
                FnScenario.fn_scenario_id == scenarioid,
                FnScenario.fn_form_id == formid,
            )
            .update({"is_active": status}, synchronize_session="fetch")
        )

        stmt2 = (
            session.query(FnScenarioData)
            .filter(
                FnScenarioData.created_by == userid,
                FnScenarioData.fn_scenario_id == scenarioid,
            )
            .update({"is_active": status}, synchronize_session="fetch")
        )
        session.commit()

        logger.info(f"Changes Status to {stmt} {stmt2} ")
        logger.info(f"Status Change time {perf_counter() - start}")

    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error delete : {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL ORM: {e}")
    finally:
        created_session and session.close()
    return stmt


def save_scenario(data, session=None, created_session=False):
    """save_scenario This function save scenario

    Args:
        data (dict):
        session (_type_, optional):. Defaults to None.
        created_session (bool, optional):. Defaults to False.

    Returns:
        _type_:
    """
    stmt = {}
    try:
        start = perf_counter()
        logger.info(f"{data=}")
        userid = data["userid"]
        formid = data["formid"]
        scenarioid = data["scenarioid"]

        logger.info("Saving Scenario")

        if session is None:
            session = Session()
            created_session = True

        update_values = {"is_draft": False}

        if data.get("scenario_name") is not None:
            update_values["scenario_name"] = data["scenario_name"]

        if data.get("scenario_decription") is not None:
            update_values["scenario_description"] = data["scenario_decription"]

        logger.info(f"{update_values=}")
        stmt = (
            session.query(FnScenario)
            .filter(
                FnScenario.created_by == userid,
                FnScenario.fn_scenario_id == scenarioid,
                FnScenario.fn_form_id == formid,
                FnScenario.is_active == True,
            )
            .update(update_values, synchronize_session="fetch")
        )
        session.commit()
        logger.info(f"{stmt}")
        logger.info("Scenario Saved")
        logger.info(f"saving took time {perf_counter() - start}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error saving scenario : {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL ORM: {e}")
    finally:
        created_session and session.close()
    return stmt


def update_change_value(data, filters_list, userid=None, scenarioid=None):
    '''update_change_value _summary_

    Args:
        data (dict):
        filters_list (_type_):
        userid (int, optional): Defaults to None.
        scenarioid (int, optional): Defaults to None.
        session (session, optional): Defaults to None.
        created_session (bool, optional): Defaults to None.

    Returns:
        updated_data_list: [{.........}]
    '''
    updated_data_list = 0

    try:
        logger.info("Session Created")
        session = Session()

        logger.info("Value Fetching user data")
        start = perf_counter()
        logger.info(data)

        filters, changed = filters_list
        logger.info("Value Creating Filters")

        filter_conditions = [
            getattr(FnScenarioData, column).ilike(f"{column_value}")
            for column, column_value in filters.items()
        ]
        logger.info(f"Unchanged {changed=}")
        logger.info("Value Filters Done")

        logger.info("Value Creating Dynamic Filters value")

        try:
            dynamic_filter_condition = and_(
                *filter_conditions,
                FnScenarioData.created_by == userid,
                FnScenarioData.fn_scenario_id == scenarioid,
                FnScenarioData.is_active == True,
                and_(
                    func.date_format(
                        FnScenarioData.date, changed.get("dateformat", "%Y%m")
                    )
                    == changed.pop("date"),
                    func.date_format(
                        FnScenarioData.date, changed.pop("dateformat", "%Y%m")
                    )
                    != None,
                ),
            )

            logger.info(dynamic_filter_condition)
            logger.info(f"{changed=}")

            changed = receive_query(
                session.query(
                    (((changed["changeValue"] - func.sum(FnScenarioData.amount)) /
                    func.sum(FnScenarioData.amount)) * 100 )
                    .label("change_value"),
                )
                .filter(dynamic_filter_condition)
                .all()
            )[0]

            logger.info(f"{changed=}")

            updated_data_list = (
                session.query(FnScenarioData)
                .filter(dynamic_filter_condition)
                .update(changed, synchronize_session="fetch")
            )

            session.commit()
        except Exception as e:
            logger.exception(f"Exception while Updating Change Precentage: {e}")
            return 0

        logger.info(f"Scenario data {updated_data_list}")
        logger.info(f"Time taken by fetching scenario is {perf_counter() - start}")
        logger.info("User data fetch with ID:")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error could not perform SQL query: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL ORM: {e}")
    finally:
        if session:
            logger.info("CLOSING SESSION")
            session.close()
    return updated_data_list


def update_amount_type(
    date, amount_type, userid=None, scenarioid=None, session=None, created_session=False
):
    '''update_amount_type _summary_

    Args:
        date (dict):
        amount_type (int):
        userid (int, optional): Defaults to None.
        scenarioid (int, optional): Defaults to None.
        session (session, optional): Defaults to None.
        created_session (bool, optional): Defaults to False.

    Returns:
        updated_data: int
    '''
    try:
        if session is None:
            session = Session()
            created_session = True

        logger.info("Actual Fetching user data")
        start = perf_counter()
        update = {"amount_type": amount_type}

        updated_data = (
            session.query(FnScenarioData)
            .filter(
                func.date_format(FnScenarioData.date, "%Y%m") == date,
                FnScenarioData.fn_scenario_id == scenarioid,
                FnScenarioData.created_by == userid,
            )
            .update(update, synchronize_session="fetch")
        )
        session.commit()
        logger.info(f"len of updated_data_query {updated_data}")

        logger.info(f"Time taken by fetching scenario is {perf_counter() - start}")

    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error could not perform SQL query: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL ORM: {e}")
    finally:
        created_session and session.close()
    return updated_data


def get_secret(orgid=None):
    '''get_secret from jwt_settings

    Args:
        orgid (int, optional): Defaults to None.
        session_obj (session, optional): Defaults to create_engine_and_session(database="ccplatform").

    Returns:
        SECRET_CLIENT, SECRET_CLIENTID: str, str
    '''
    SECRET_CLIENT, SECRET_CLIENTID = None, None
    try:
        session_obj = create_engine_and_session(database="ccplatform")
        client = receive_query(
            session_obj().query(
                JwtSettings.secret.label("SECRET_CLIENT"),
                JwtSettings.client_id.label("SECRET_CLIENTID"),
            )
            .filter(JwtSettings.organizationId == orgid, JwtSettings.isActive == True)
            .all()
        )[0]
        logger.info(f"{client=}")
        SECRET_CLIENT, SECRET_CLIENTID = (
            client["SECRET_CLIENT"],
            client["SECRET_CLIENTID"],
        )

    except SQLAlchemyError as e:
        session_obj().rollback()
        logger.exception(f"Error could not perform SQL query: {e}")
    except Exception as e:
        session_obj().rollback()
        logger.exception(f"Error in SQL ORM: {e}")
    finally:
        session_obj().close()
    return SECRET_CLIENT, SECRET_CLIENTID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, case, update
from .models import FnForm, FnUserData, FnScenario, FnScenarioData
from djangoproject.main_logger import set_up_logging
from .db import Session
from time import perf_counter

logger = set_up_logging()


def receive_query(query):
    """

    Parameters
    ----------
    query

    Returns
    -------

    """
    return [row._asdict() for row in query]


def create_form(form_name, lum_user_id, lum_org_id):
    form_name = form_name.split(".")[0]
    formid = None
    try:
        logger.info(f"creating form")
        with Session() as session:
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
        logger.exception(f"Error in SQL: {e}")
    finally:
        session.close()
    return formid


def create_user_data(df, formid, userid):
    user_data = None
    try:
        logger.info(f"Updating user data")
        df = df.dropna()
        with Session() as session:
            data = df.to_dict(orient="records")

            session.bulk_insert_mappings(FnUserData, data)
            session.commit()

            user_data = receive_query(
                session.query(
                    FnUserData.fn_user_data_id.label("user_data_id"),
                    FnUserData.date.label("Date"),
                    FnUserData.receipt_number.label("Receipt Number"),
                    FnUserData.business_unit.label("Business Unit"),
                    FnUserData.account_type.label("Account Type"),
                    FnUserData.account_subtype.label("Account SubType"),
                    FnUserData.project_name.label("Project Name"),
                    case(
                        (FnUserData.amount_type == 1, "Actual"),
                        (FnUserData.amount_type == 0, "Projected"),
                        else_="Unknown",
                    ).label("Amount Type"),
                    FnUserData.amount.label("Amount"),
                    FnUserData.amount.label("base value"),
                )
                .filter(
                    FnUserData.fn_form_id == formid, FnUserData.created_by == userid
                )
                .all()
            )

            logger.info(
                f"User data saved with ID : {formid} and len is {len(user_data)} "
            )
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error saving user form data: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        session.close()
    return user_data


def fetch_from(userid, orgid):
    form_names = None
    try:
        logger.info(f"Fetching forms for user {userid}")
        with Session() as session:
            form_names = (
                session.query(FnForm.form_name, FnForm.fn_form_id)
                .filter(
                    FnForm.lum_user_id == userid,
                    FnForm.lum_org_id == orgid,
                    FnForm.is_active == True,
                )
                .all()
            )
            form_names = [
                {"formid": form_name.fn_form_id, "form_name": form_name.form_name}
                for form_name in form_names
            ]
            logger.info(f"Form_name for user {userid}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error fetching form: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        session.close()
    return form_names


def fetch_scenario(formid, userid):
    scenario_names = {}
    try:
        logger.info(f"fetch scenario for form id {formid} and user {userid}")
        with Session() as session:
            scenario_names = (
                session.query(
                    FnScenario.fn_scenario_id,
                    FnScenario.scenario_description,
                    FnScenario.scenario_name,
                    FnScenario.is_active,
                )
                .distinct(FnScenario.fn_scenario_id)
                .join(
                    FnScenarioData,
                    FnScenarioData.fn_scenario_id == FnScenario.fn_scenario_id,
                )
                .filter(
                    FnScenario.fn_form_id == formid,
                    FnScenario.created_by == userid,
                    FnScenarioData.is_active == True,
                )
                .all()
            )

            logger.info(scenario_names)
            scenario_names = [
                {
                    "scenario_id": scenario.fn_scenario_id,
                    "scenario_description": scenario.scenario_description,
                    "scenario_name": scenario.scenario_name,
                    "scenario_status": scenario.is_active,
                }
                for scenario in scenario_names
            ]
            logger.info(f"scenario_name for formid {formid} : {len(scenario_names)}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error fetching scenario form: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        session.close()
    return scenario_names


def get_user_data(formid, userid, session=None, created_session=False):
    user_data = None
    try:
        logger.info(f"getting user data for form id {formid}")

        if session is None:
            session = Session()
            created_session = True
        with Session() as session:
            start = perf_counter()
            user_data = receive_query(
                session.query(
                    FnUserData.fn_user_data_id.label("user_data_id"),
                    FnUserData.date.label("Date"),
                    FnUserData.receipt_number.label("Receipt Number"),
                    FnUserData.business_unit.label("Business Unit"),
                    FnUserData.account_type.label("Account Type"),
                    FnUserData.account_subtype.label("Account SubType"),
                    FnUserData.project_name.label("Project Name"),
                    case(
                        (FnUserData.amount_type == 1, "Actual"),
                        (FnUserData.amount_type == 0, "Projected"),
                        else_="Unknown",
                    ).label("Amount Type"),
                    FnUserData.amount.label("Amount"),
                    FnUserData.amount.label("base value"),
                )
                .filter(
                    FnUserData.fn_form_id == formid, FnUserData.created_by == userid
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
        logger.exception(f"Error in SQL: {e}")
    finally:
        created_session and session.close()
    return user_data


def filter_column(scenarioid, formid, userid, value):
    user_data = None
    try:
        logger.info(f"getting user data for form id {scenarioid}")
        with Session() as session:
            start = perf_counter()
            query = (
                session.query(
                    FnScenarioData.fn_scenario_data_id.label("data_id"),
                    FnScenarioData.receipt_number.label("Receipt Number"),
                    FnScenarioData.business_unit.label("Business Unit"),
                    FnScenarioData.account_type.label("Account Type"),
                    FnScenarioData.account_subtype.label("Account SubType"),
                    FnScenarioData.project_name.label("Project Name"),
                    case(
                        (FnScenarioData.amount_type == 1, "Actual"),
                        (FnScenarioData.amount_type == 0, "Projected"),
                        else_="Unknown",
                    ).label("Amount Type"),
                    (
                        (
                            FnScenarioData.amount
                            * (FnScenarioData.change_value / 100 + 1)
                        ).label("Amount")
                    ),
                    FnScenarioData.amount.label("base value"),
                    FnScenarioData.change_value.label("changePrecentage"),
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
            if value not in ["all", "All", "ALL"]:
                query = query.filter(FnScenarioData.business_unit == value)

            user_data = receive_query(query.all())
            logger.info(
                f"got user data for  {len(user_data)} time took {perf_counter() - start}"
            )
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error fetching scenario form: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
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
    scenarioid = None
    try:
        logger.info(f"creating form")

        if session is None:
            session = Session()
            created_session = True
        scenario_name_list = fetch_scenario(formid=formid, userid=userid)
        scenario_name_list = (
            {item["scenario_name"] for item in scenario_name_list}
            if len(scenario_name_list) > 0
            else []
        )
        logger.info(scenario_name_list)
        if not scenario_name in scenario_name_list:
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
            raise Exception("Scenario already exits")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error saving form: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
        raise e
    finally:
        created_session and session.close()
    return scenarioid, status


def create_user_data_scenario(df, scenarioid, session=None, created_session=False):
    try:
        if session is None:
            session = Session()
            created_session = True

        logger.info(f"Updating user data")
        data = df.to_dict(orient="records")
        start = perf_counter()
        session.bulk_insert_mappings(FnScenarioData, data)
        session.commit()
        logger.info(f"time taken by save scenario is {perf_counter() - start}")
        logger.info(f"User data saved with ID: {scenarioid}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error saving user form data: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        created_session and session.close()
    return


def get_user_scenario(scenarioid, session=None, created_session=False):
    try:
        if session is None:
            session = Session()
            created_session = True

        logger.info(f"fetching user data")
        start = perf_counter()

        scenario_data = (
            session.query(
                FnScenarioData.date,
                FnScenarioData.receipt_number,
                FnScenarioData.business_unit,
                FnScenarioData.account_type,
                FnScenarioData.account_subtype,
                FnScenarioData.project_name,
                FnScenarioData.amount_type,
                FnScenarioData.amount,
                FnScenarioData.change_value,
            )
            .filter(FnScenarioData.fn_scenario_id == scenarioid)
            .all()
        )
        scenario_data = [row._asdict() for row in scenario_data]
        logger.info(f"scenario data {len(scenario_data)}")
        logger.info(f"time taken by save scenario is {perf_counter() - start}")
        logger.info(f"User data fetch with ID: {scenarioid} ")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error saving user form data: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        created_session and session.close()
    return scenario_data


def get_user_scenario_new(scenarioid, formid, session=None, created_session=False):
    try:
        if session is None:
            session = Session()
            created_session = True

        logger.info(f"fetching user data")
        start = perf_counter()

        scenario_data = receive_query(
            session.query(
                FnScenarioData.fn_scenario_data_id.label("data_id"),
                FnScenarioData.receipt_number.label("Receipt Number"),
                FnScenarioData.business_unit.label("Business Unit"),
                FnScenarioData.account_type.label("Account Type"),
                FnScenarioData.account_subtype.label("Account SubType"),
                FnScenarioData.project_name.label("Project Name"),
                case(
                    (FnScenarioData.amount_type == 1, "Actual"),
                    (FnScenarioData.amount_type == 0, "Projected"),
                    else_="Unknown",
                ).label("Amount Type"),
                (
                    (
                        FnScenarioData.amount * (FnScenarioData.change_value / 100 + 1)
                    ).label("Amount")
                ),
                FnScenarioData.amount.label("base value"),
                FnScenarioData.change_value.label("changePrecentage"),
            )
            .join(FnScenario)
            .filter(
                FnScenarioData.fn_scenario_id == scenarioid,
                FnScenarioData.is_active == True,
                FnScenario.fn_form_id == formid,
            )
            .all()
        )

        logger.info(f"scenario data {len(scenario_data)}")
        logger.info(f"time taken by fetching scenario is {perf_counter() - start}")
        logger.info(f"User data fetch with ID: {scenarioid} ")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error saving user form data: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        created_session and session.close()
    return scenario_data


def update_scenario(
    data, filters_list, userid, scenarioid, session=None, created_session=False
):
    updated_data_list = []

    try:
        if session is None:
            session = Session()
            created_session = True

        logger.info("Fetching user data")
        start = perf_counter()
        updated_data_list = []
        for filters, update in filters_list:
            logger.info(f"Creating Filters")

            filter_conditions = [
                getattr(FnScenarioData, column).ilike(f"{column_value}")
                for column, column_value in filters.items()
            ]
            logger.info(filter_conditions)
            logger.info(f"Filters Done")

            logger.info(f"Creating Dynamic Filters")

            dynamic_filter_condition = and_(
                *filter_conditions,
                FnScenarioData.created_by == userid,
                FnScenarioData.fn_scenario_id == scenarioid,
                FnScenarioData.is_active == True,
            )
            logger.info(dynamic_filter_condition)
            logger.info(f"Creating Filters Dynamic Done")

            logger.info(f"Starting Updating")
            updated_data = (
                session.query(FnScenarioData)
                .filter(dynamic_filter_condition)
                .update(update, synchronize_session="fetch")
            )

            session.commit()
            logger.info(f"Updation done")

            logger.info(f"Number of rows updated: {updated_data}")

            logger.info(f"Fetchning data")
            updated_data_query = (
                session.query(
                    FnScenarioData.fn_scenario_data_id.label("data_id"),
                    FnScenarioData.receipt_number.label("Receipt Number"),
                    FnScenarioData.business_unit.label("Business Unit"),
                    FnScenarioData.account_type.label("Account Type"),
                    FnScenarioData.account_subtype.label("Account SubType"),
                    FnScenarioData.project_name.label("Project Name"),
                    case(
                        (FnScenarioData.amount_type == 1, "Actual"),
                        (FnScenarioData.amount_type == 0, "Projected"),
                        else_="Unknown",
                    ).label("Amount Type"),
                    (
                        (
                            FnScenarioData.amount
                            * (FnScenarioData.change_value / 100 + 1)
                        ).label("Amount")
                    ),
                    FnScenarioData.amount.label("base value"),
                    FnScenarioData.change_value.label("changePrecentage"),
                )
                .filter(dynamic_filter_condition)
                .all()
            )

            updated_data_list.extend(updated_data_query)
        updated_data_list = receive_query(updated_data_list)
        logger.info(f"Scenario data {len(updated_data_list)}")
        logger.info(f"Time taken by fetching scenario is {perf_counter() - start}")
        logger.info("User data fetch with ID:")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error saving user form data: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        created_session and session.close()
    return updated_data_list


def scenario_status_update(
    userid, scenarioid, formid, status, session=None, created_session=False
):
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
        logger.exception(f"Error in SQL: {e}")
    finally:
        created_session and session.close()
    return stmt


def scenario_data_status_update(
    userid, scenarioid, formid, status, session=None, created_session=False
):
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
        logger.exception(f"Error updating status : {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        created_session and session.close()
    return stmt

def save_scenario(userid, scenarioid, formid, session=None, created_session=False):
    try:
        logger.info("save_scenario")
        if session is None:
            session = Session()
            created_session = True
        stmt = {"Scenario Saved":"Scenario Saved","scenarioid":scenarioid}
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error updating status : {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        created_session and session.close()
    return stmt

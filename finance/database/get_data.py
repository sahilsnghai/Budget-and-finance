from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
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
            
            user_data = receive_query(session.query(
                FnUserData.fn_user_data_id.label("user_data_id"),
                FnUserData.date.label("Date"),
                FnUserData.receipt_number.label("Receipt Number"),
                FnUserData.business_unit.label("Business Unit"),
                FnUserData.account_type.label("Account Type"),
                FnUserData.account_subtype.label("Account SubType"),
                FnUserData.project_name.label("Project Name"),
                FnUserData.amount_type.label("Amount Type"),
                FnUserData.amount.label("Amount")
            ).filter(
                FnUserData.fn_form_id == formid,
                FnUserData.created_by == userid
            ).all()
            )
            
            logger.info(f"User data saved with ID : {formid} and len is {len(user_data)} ")
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
            form_names = {
                form_name.fn_form_id: form_name.form_name for form_name in form_names
            }
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
                session.query(FnScenario.fn_scenario_id, FnScenario.scenario_name)
                .filter(
                    FnScenario.fn_form_id == formid,
                    FnScenario.created_by == userid,
                    FnScenario.is_active == True,
                )
                .all()
            )
            scenario_names = {
                scenario.fn_scenario_id: scenario.scenario_name
                for scenario in scenario_names
            }
            logger.info(f"scenario_name for formid {formid} : {scenario_names}")
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
            user_sql = (
                session.query(
                    FnUserData.date,
                    FnUserData.receipt_number,
                    FnUserData.business_unit,
                    FnUserData.account_type,
                    FnUserData.account_subtype,
                    FnUserData.project_name,
                    FnUserData.amount_type,
                    FnUserData.amount,
                )
                .filter(
                    FnUserData.fn_form_id == formid,
                    FnUserData.created_by == userid,
                    FnUserData.is_active == True,
                )
                .all()
            )
            user_data = [row._asdict() for row in user_sql]
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


def filter_column(formid, userid, value):
    user_data = None
    try:
        logger.info(f"getting user data for form id {formid}")
        with Session() as session:
            start = perf_counter()
            query = session.query(
                FnUserData.date,
                FnUserData.receipt_number,
                FnUserData.business_unit,
                FnUserData.account_type,
                FnUserData.account_subtype,
                FnUserData.project_name,
                FnUserData.amount_type,
                FnUserData.amount,
            ).filter(
                FnUserData.fn_form_id == formid,
                FnUserData.created_by == userid,
                FnUserData.is_active == True,
            )
            if value not in ['all',"All","ALL"]:
                query = query.filter(FnUserData.business_unit == value)
            
            user_data = [row._asdict() for row in query.all()]
            logger.info(f"filter column {len(user_data)}")
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

        if not scenario_name in fetch_scenario(formid=formid, userid=userid).values():
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
    return scenarioid


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
        ).filter(FnScenarioData.fn_scenario_id == scenarioid ).all())
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
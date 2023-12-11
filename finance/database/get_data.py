from sqlalchemy.exc import SQLAlchemyError
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


def create_user_data(df, formid):
    user_data_instance = None
    try:
        logger.info(f"Updating user data")
        df = df.dropna()
        with Session() as session:
            logger.info(f" aafter session{len(df)}")
            data = df.to_dict(orient="records")
            logger.info(f" aafter session2 {len(data)}")
            session.bulk_insert_mappings(FnUserData, data)
            session.commit()
            logger.info(f"User data saved with ID: {formid} ")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error saving user form data: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        session.close()


def fetch_from(userid, orgid):
    form_names = None
    try:
        logger.info(f"Fetching forms for user {userid}")
        with Session() as session:
            form_names = (
                session.query(FnForm.form_name, FnForm.fn_form_id)
                .filter(FnForm.lum_user_id == userid, FnForm.lum_org_id == orgid,
                        FnForm.is_active == 1)
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
        logger.info(f"fetch scenario for form id {formid} {userid}")
        with Session() as session:
            scenario_names = (
                session.query(FnScenario.fn_scenario_id, FnScenario.scenario_name)
                .filter(FnScenario.fn_form_id == formid, 
                        FnScenario.created_by == userid ,
                        FnScenario.is_active == 1).all()
            )
            
            scenario_names = {scenario.fn_scenario_id :scenario.scenario_name for scenario in scenario_names}
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

def get_user_data(formid, userid):
    user_data = None
    try:
        logger.info(f"getting user data for form id {formid}")
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
                .filter(FnUserData.fn_form_id == formid, FnUserData.created_by == userid, FnUserData.is_active == 1)
                .all()
            )
            user_data = [row._asdict() for row in user_sql]
            logger.info(f"got user data for  {len(user_data)} time took {perf_counter() - start}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error fetching scenario form: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        session.close()
    return user_data


def filter_column(formid, userid, value):
    user_data = None
    try:
        logger.info(f"getting user data for form id {formid}")
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
                .filter(FnUserData.fn_form_id == formid, FnUserData.created_by == userid,
                        FnUserData.business_unit == value, FnUserData==1)
                .all()
            )
            user_data = [row._asdict() for row in user_sql]
            logger.info(f"got user data for  {len(user_data)} time took {perf_counter() - start}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error fetching scenario form: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        session.close()
    return user_data


def create_scenario(scenario_name, scenario_decription, formid, userid):
    scenarioid = None
    try:
        logger.info(f"creating form")
        if not scenario_name in fetch_scenario(formid=formid, userid=userid).values():
            with Session() as session:
                scenario_instance = FnScenario(
                    fn_form_id=formid,
                    scenario_name=scenario_name,
                    scenario_description=scenario_decription,
                    created_by = userid,
                    modified_by = userid
                )
                session.add(scenario_instance)
                session.commit()
                logger.info(f"scenario saved with ID: {scenario_instance.fn_scenario_id}")
                scenarioid = scenario_instance.fn_scenario_id
        else:
            logger.info(f"found similar. scenario_name for {userid}")
    except SQLAlchemyError as e:
        logger.exception(f"Error saving form: {e}")
    except Exception as e:
        logger.exception(f"Error in SQL: {e}")
    finally:
        session.close()
    return scenarioid

def create_user_data_scenario(df, scenarioid):
    save = False
    try:
        logger.info(f"Updating user data")
        with Session() as session:
            data = df.to_dict(orient="records")
            start = perf_counter()
            session.bulk_insert_mappings(FnScenarioData, data)
            session.commit()
            logger.info(f"time taken by save scenario is {perf_counter() - start}")
            logger.info(f"User data saved with ID: {scenarioid}")
            save = True
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error saving user form data: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        session.close()
    return 
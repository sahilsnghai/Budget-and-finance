
from sqlalchemy.exc import SQLAlchemyError
from .models import FnForm,FnUserData ,FnScenario, FnScenarioData
from djangoproject.main_logger import set_up_logging
from .db import Session

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
        with Session() as session:
            data = df.to_dict(orient='records')
            session.bulk_insert_mappings(FnUserData, data)  
            user_data_instance = FnUserData(fn_form_id=formid)  
            session.add(user_data_instance)
            session.commit()
            logger.info(f"User data saved with ID: {user_data_instance.fn_user_data_id}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error saving user form data: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        session.close()
    return user_data_instance


def fetch_from(userid, orgid):
    form_names = None
    try:
        logger.info(f"Fetching forms for user {userid}")
        with Session() as session:
            form_names = session.query(FnForm.form_name, FnForm.fn_form_id).filter(
                FnForm.lum_user_id == userid, FnForm.lum_org_id == orgid).all()
            logger.info(f"{form_names=}")
            form_names = {form_name.fn_form_id : form_name.form_name for form_name in form_names}
            logger.info(f"Form_name for user {userid} : {form_names}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error fetching form: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        session.close()
    return form_names

def fetch_scenario(formid):
    scenario_name = None
    try:
        logger.info(f"fetch scenario for form id {formid}")
        with Session() as session:
            scenario_names = session.query(FnScenario.scenario_name).filter(
                FnScenario.fn_form_id == formid).all()
            scenario_names = [scenario.form_name for scenario in scenario_names]
            logger.info(f"scenario_name for formid {formid} : {scenario_name}")
    except SQLAlchemyError as e:
        session.rollback()
        logger.exception(f"Error fetching scenario form: {e}")
    except Exception as e:
        session.rollback()
        logger.exception(f"Error in SQL: {e}")
    finally:
        session.close()
    return scenario_names

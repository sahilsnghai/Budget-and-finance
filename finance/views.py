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

"""views"""

from time import perf_counter
from lumenore_apps import Constants, set_up_logging
from rest_framework import response, views, exceptions
from requests import post
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from .utils import create_response, format_df, create_filter, COLUMNS
from django.http import HttpResponseRedirect
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_405_METHOD_NOT_ALLOWED
)
from .database.get_data import (
    create_form,
    create_user_data,
    fetch_from,
    fetch_scenario,
    get_user_data,
    filter_column,
    create_scenario,
    create_user_data_scenario,
    scenario_data_status_update,
    scenario_status_update,
    get_user_scenario_new,
    update_scenario_percentage,
    save_scenario,
    update_change_value,
    update_amount_type,
    get_secret,
    create_engine_and_session,
    Session,
)
import pandas as pd
import asyncio


constants = Constants()
logger = set_up_logging()
Response = response.Response

class BaseAPIView(views.APIView):
    '''BaseAPIView _summary_

    Args:
        views (_type_):
    '''
    def handle_exception(self, exc):
        logger.info(f"Exception in {self.__class__.__name__} -> {exc}")

        status_code = HTTP_500_INTERNAL_SERVER_ERROR

        if isinstance(exc, exceptions.MethodNotAllowed):
            status_code = HTTP_405_METHOD_NOT_ALLOWED

        meta = {
            "error_message": str(exc),
            "error": True,
            "status_code": status_code,
        }

        create_response(None, **meta)

        return Response(constants.STATUS200, status=meta["status_code"])


class CreateHierarchy(BaseAPIView):
    '''CreateHierarchy _summary_

    Args:
        BaseAPIView (_type_):
    '''
    def post(self, req, format=None):
        try:
            files = req.FILES.getlist("file")
            userid = req.POST["userid"]
            orgid = req.POST["organizationId"]
        except Exception as e:
            logger.info(f"KEY NOT FOUND {e}")
            return Response(
                {"KeyError": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
            )
        data = None
        try:
            start = perf_counter()
            with ThreadPoolExecutor(max_workers=len(files)) as executor:
                futures = [executor.submit(asyncio.run, self.save_matrix(
                df=pd.read_excel(file), userid=userid, orgid=orgid, filename=file.name))
                for file in files]
            wait(futures)
            data = [future.result() for future in futures]
            logger.info(f"time by hierarchy {perf_counter() - start}")
            meta = {"status_code": HTTP_200_OK}
        except (ValueError, KeyError) as e:
            logger.exception(e)
            raise RuntimeError("Error in request")
        except Exception as e:
            logger.exception(e)
            raise e
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["status_code"])

    def put(self, req, format=None):
        return CreateScenario().put(req=req)

    def delete(self, req, format=None):
        return CreateScenario().delete(req=req)

    @staticmethod
    async def save_matrix(df, filename, **kwargs):
        try:
            async_session = create_engine_and_session()
            with async_session() as session:
                if list(df.columns.to_list()) != list(COLUMNS.keys()):
                    raise RuntimeError("Invalid Column Names.")
                formid = await create_form(filename, kwargs.get("userid"), kwargs.get("orgid"), session=session)
                if formid is not None:
                    logger.info(f"created form wih id -> {formid}")
                    df = await format_df(df, formid=formid, userid=kwargs.get("userid"))
                    await create_user_data(df, formid, session=session)
                else:
                    logger.info(f"Could not create form wih id -> {formid}")

        except Exception as e:
            logger.exception(e)
            raise e
        return {"formid": formid, "filename": filename.split('.')[0]}


class CreateScenario(BaseAPIView):
    '''CreateScenario _summary_

    Args:
        BaseAPIView (_type_):
    '''
    def post(self, req, format=None):
        try:
            data = req.data["data"]
            scenario_name = data["scenario_name"]
            userid = data["userid"]
            scenario_decription = data.get("scenario_decription")
            formid = data["formid"]
        except Exception as e:
            logger.info(f"KEY NOT FOUND {e}")
            return Response(
                {"KeyError": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
            )
        data = None
        with Session() as session:
            try:
                    start = perf_counter()
                    scenarioid, status = create_scenario(
                        scenario_name, scenario_decription, formid, userid, session
                    )

                    if scenarioid is None:
                        raise ValueError(f"Could not able to create {scenario_name}.")

                    dataframe = get_user_data(
                        formid=formid,
                        userid=userid,
                        scenarioid=scenarioid,
                        migrate=True,
                        session=session,
                    )
                    logger.info(
                        f"time taken while saving scenario meta and fetching user data {perf_counter() - start}"
                    )

                    try:
                        logger.info(f"{dataframe[0]}")
                    except IndexError as e:
                        logger.info("got Indix error check log 211 get_data userid and formid should match")
                        raise IndexError("Couldn't able to fetch data. Please refresh")

                    create_user_data_scenario(
                        dataframe=dataframe, scenarioid=scenarioid, session=session
                    )
                    logger.info(f"time taken to migrate {perf_counter() - start}")
                    '''# user_scenario_data = get_user_scenario_new(
                        scenarioid=scenarioid, formid=formid, session=session)'''
                    logger.info(f"created scenario with id {scenarioid}")
                    data = {
                        "scenarioid": scenarioid,
                        "scenario_name": scenario_name,
                        "scenario_decription": scenario_decription,
                        "scenario_status": status,
                    }
                    meta = {"status_code": HTTP_200_OK}
            except Exception as e:
                session.rollback()
                logger.exception(e)
                raise e
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["status_code"])

    def put(self, req, format=None):
        try:
            data = req.data["data"]
            userid = data["userid"]
            scenarioid = data["scenarioid"]
            status = data["status"]
            formid = data["formid"]
        except Exception as e:
            logger.info(f"KEY NOT FOUND {e}")
            return Response(
                {"KeyError": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
            )
        try:
            data = scenario_status_update(
                userid=userid, scenarioid=scenarioid, formid=formid, status=status
            )
            meta = {"status_code": HTTP_200_OK}
        except Exception as e:
            logger.info(f"Exception in creating hierarchy -> {e}")
            raise e
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["status_code"])

    def delete(self, req, format=None):
        try:
            data = req.data["data"]
            userid = data["userid"]
            scenarioid = data["scenarioid"]
            status = data["status"]
            formid = data["formid"]
        except Exception as e:
            logger.info(f"KEY NOT FOUND {e}")
            return Response(
                {"KeyError": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
            )
        try:
            logger.info(f"{status} {type(status)}")
            data = scenario_data_status_update(
                userid, scenarioid, formid, status, session=None, created_session=False
            )
            meta = {"status_code": HTTP_200_OK}
        except Exception as e:
            logger.info(f"Exception in creating hierarchy -> {e}")
            raise e
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["status_code"])


class UpdateChangePrecentage(BaseAPIView):
    '''UpdateChangePrecentage _summary_

    Args:
        BaseAPIView (_type_):
    '''
    def post(self, req, format=None):
        data = req.data["data"]
        datalist = data["datalist"]
        userid = data["userid"]
        scenarioid = data["scenarioid"]

        try:
            with ThreadPoolExecutor(max_workers=len(datalist)) as executor:
                futures = [executor.submit(update_scenario_percentage,
                            data, create_filter(row), userid=userid, scenarioid=scenarioid
                            ) for row in datalist]

            data = []
            for future in as_completed(futures):
                data.extend(future.result())
            logger.info("Calculation done")
            meta = {"status_code": HTTP_200_OK}
            logger.info(f"update percentage data len {len(data)}")
        except (ValueError, KeyError) as e:
            logger.exception(e)
            raise IndexError("Error in request")
        except Exception as e:
            logger.exception(e)
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["status_code"])


class SavesScenario(BaseAPIView):
    '''SavesScenario _summary_

    Args:
        BaseAPIView (_type_):
    '''
    def post(self, req, format=None):
        try:
            try:
                data = req.data["data"]

            except Exception as e:
                logger.info(f"KEY NOT FOUND {e}")
                return Response(
                    {"Key Error": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
                )
            data = save_scenario(data=data)
            meta = {"status_code": HTTP_200_OK}
        except Exception as e:
            logger.exception(e)
            raise e
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["status_code"])


class FetchFrom(BaseAPIView):
    '''FetchFrom _summary_

    Args:
        BaseAPIView (_type_):
    '''
    def post(self, req, format=None):
        data = None
        try:
            userid = req.data["data"]["userid"]
            orgid = req.data["data"]["organizationId"]
            logger.info(f"{userid=} {orgid=}")
            data = fetch_from(userid=userid, orgid=orgid)
            meta = {"status_code": HTTP_200_OK}
        except Exception as e:
            logger.exception(e)
            raise e
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["status_code"])


class FetchScenario(BaseAPIView):
    '''FetchScenario _summary_

    Args:
        BaseAPIView (_type_):
    '''
    def post(self, req, format=None):
        scenario_names = []

        try:
            formid = req.data["data"]["formid"]
            userid = req.data["data"]["userid"]
            scenario_names = fetch_scenario(formid=formid, userid=userid)
            data, meta = scenario_names, {"status_code": HTTP_200_OK}
        except Exception as e:
            logger.exception(e)
            raise e
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["status_code"])


class GetData(BaseAPIView):
    '''GetData _summary_

    Args:
        BaseAPIView (_type_):
    '''
    def post(self, req, format=None):
        data = {}
        try:
            logger.info(f"{req.data=}")
            formid = req.data["data"]["formid"]
            userid = req.data["data"]["userid"]
            start = perf_counter()
            data = get_user_data(formid=formid, userid=userid)
            logger.info(
                f"time taken while fetching data for  {userid} is {perf_counter()-start} "
            )
            meta = {"status_code": HTTP_200_OK}
        except Exception as e:
            logger.exception(e)
            raise e
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["status_code"])


class FilterColumn(BaseAPIView):
    '''FilterColumn _summary_

    Args:
        BaseAPIView (_type_):
    '''
    def post(self, req, format=None):
        data = {}
        try:
            logger.info(f"{req.data=}")
            data = req.data["data"]
            formid = data["formid"]
            userid = data["userid"]
            scenarioid = data["scenarioid"]
            business_unit = data.get("unit")
            year = data.get("year")
            start = perf_counter()
            data = filter_column(
                scenarioid=scenarioid,
                formid=formid,
                userid=userid,
                business_unit=business_unit,
                year=year,
            )
            data = {
                "column_name": data[0].keys() if len(data) > 1 else [],
                "row_names": data,
            }
            logger.info(
                f"time taken while fetching data for  {userid} is {perf_counter()-start}"
            )
            meta = {"status_code": HTTP_200_OK}
        except Exception as e:
            logger.exception(e)
            raise e
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["status_code"])


class GetScenario(BaseAPIView):
    '''GetScenario _summary_

    Args:
        BaseAPIView (_type_):
    '''
    def post(self, req, format=None):
        data = {}
        try:
            logger.info(f"{req.data=}")
            userid = req.data["data"]["userid"]
            scenarioid = req.data["data"]["scenarioid"]
            formid = req.data["data"]["formid"]
            logger.info(f"{formid=} {scenarioid=} {userid=}")
            start = perf_counter()
            data = get_user_scenario_new(scenarioid, formid=formid, session=None)
            data = {
                "formid": formid,
                "scenarioid": scenarioid,
                "column_name": data[0].keys() if len(data) > 1 else [],
                "row_names": data,
            }
            logger.info(
                f"time taken after fetching and for {userid} is {perf_counter()-start} "
            )
            meta = {"status_code": HTTP_200_OK}
        except Exception as e:
            logger.exception(e)
            raise e
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["status_code"])


class UpdateBudget(BaseAPIView):
    '''UpdateBudget _summary_

    Args:
        BaseAPIView (_type_):
    '''
    def post(self, req, format=None):
        data = req.data["data"]
        amount_type = data["amount_type"]
        date = data["date"]
        userid = data["userid"]
        scenarioid = data["scenarioid"]

        try:
            data = update_amount_type(
                date, amount_type, userid=userid, scenarioid=scenarioid
            )
            logger.info("Status update")
            meta = {"status_code": HTTP_200_OK}
            logger.info(f"update percentage data len {data}")
        except Exception as e:
            logger.exception(e)
            raise e
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["status_code"])


class UpdateChangeValue(BaseAPIView):
    '''UpdateChangeValue _summary_

    Args:
        BaseAPIView (_type_):
    '''
    def post(self, req, format=None):
        data = req.data["data"]
        datalist = data["datalist"]
        userid = data["userid"]
        scenarioid = data["scenarioid"]

        try:
            with ThreadPoolExecutor(max_workers=len(datalist)) as executor:
                futures = [executor.submit(update_change_value,
                            data, create_filter(row), userid=userid, scenarioid=scenarioid
                            ) for row in datalist]
            data = 0
            for future in as_completed(futures):
                data += future.result()
            logger.info("Calculation done")
            meta = {"status_code": HTTP_200_OK}
            logger.info(f"update value row data  {data}")
        except ValueError as e:
            logger.exception(e)
            raise RuntimeError("Incorrect request")
        except Exception as e:
            logger.exception(e)
            raise e
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["status_code"])


class TokenAPIView(BaseAPIView):
    '''TokenAPIView _summary_

    Args:
        BaseAPIView (_type_):
    '''
    def get(self, req):

        try:
            try:
                orgid = req.GET["organizationId"]
                email = req.GET["email"]
            except KeyError as e:
                logger.info(f"{req.GET=}")
                return Response(
                    {"KeyError": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
                )
            SECRET_CLIENT, SECRET_CLIENTID =  get_secret(orgid=orgid)

            if SECRET_CLIENT == None or SECRET_CLIENTID == None:
                raise ValueError(f"Invalid Organization Id: Organization {orgid} not found")

            payload = {
                "clientSecret": SECRET_CLIENT,
                "clientId": SECRET_CLIENTID,
                "email": email }

            logger.info(f"{payload=}")

            resp = post(
                constants.get_config("parameters", "identityUrl") + "/jwt/generate-jwt",
                headers= {
                'Content-Type': 'application/json',
                "version": req.headers.get('version')
                },
                json={"data": payload},
            )
            token = resp.json()["data"]

            logger.info(f"{resp=} && {token=}")

            response = post(
                constants.get_config("parameters", "identityUrl") + "/jwt/sso-lumenore",
                headers={"Content-Type": "application/x-www-form-urlencoded", "version": req.headers.get('version')},
                data={
                    "jwt": token,
                    "return_to": constants.get_config("parameters", "financeAppRedirectUrl"),
                    "clientId": SECRET_CLIENTID,
                },
            )

            if response.status_code == 200:
                redirect_url = response.text.strip('"')
            else:
                logger.exception(f"Error: {response.status_code} - {response.text}")
                redirect_url = constants.get_config("parameters", "financeAppRedirectUrl")

        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            redirect_url = constants.get_config("parameters", "financeAppRedirectUrl")
        logger.info(redirect_url)

        return HttpResponseRedirect(redirect_to=redirect_url)

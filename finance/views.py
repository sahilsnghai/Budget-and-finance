from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.views import APIView
from .utils import create_response, format_df, create_filter
from djangoproject.constants import Constants
from djangoproject.main_logger import set_up_logging
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
    Session,
)
from time import perf_counter
import pandas as pd

from requests import post
from django.conf import settings
from django.http import HttpResponseRedirect

constants = Constants()
logger = set_up_logging()


class CreateHierarchy(APIView):
    def post(self, req, format=None):
        try:
            file = req.FILES["file"]
            userid = req.POST["userid"]
            orgid = req.POST["organizationId"]
        except Exception as e:
            logger.info(f"KEY NOT FOUND {e}")
            return Response(
                {"Key Error": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
            )
        data = None
        try:
            start = perf_counter()
            data = self.save_matrix(
                df=pd.read_excel(file), userid=userid, orgid=orgid, filename=file.name
            )
            logger.info(f"time by hierarchy {perf_counter() - start}")
            meta = {"code": HTTP_200_OK}
        except Exception as e:
            logger.info(f"Exception in creating hierarchy -> {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["code"])

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
                {"Key Error": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
            )
        try:
            data = scenario_status_update(
                userid=userid, scenarioid=scenarioid, formid=formid, status=status
            )
            meta = {"code": HTTP_200_OK}
        except Exception as e:
            logger.info(f"Exception in creating hierarchy -> {e}")
            data = {}
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["code"])

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
                {"Key Error": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
            )
        try:
            logger.info(f"{status} {type(status)}")
            data = scenario_data_status_update(
                userid, scenarioid, formid, status, session=None, created_session=False
            )
            meta = {"code": HTTP_200_OK}
        except Exception as e:
            logger.info(f"Exception in creating hierarchy -> {e}")
            data = {}
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["code"])

    @staticmethod
    def save_matrix(df, filename, **kwargs):
        try:
            formid = create_form(filename, kwargs.get("userid"), kwargs.get("orgid"))
            if formid is not None:
                logger.info(f"created form wih id -> {formid}")
                df = format_df(df, formid=formid, userid=kwargs.get("userid"))
                create_user_data(df, formid, userid=kwargs.get("userid"))
            else:
                logger.info(f"Could not create form wih id -> {formid}")

        except Exception as e:
            logger.exception(e)
            raise e
        return {"formid": formid}


class CreateScenario(APIView):
    def post(self, req, format=None):
        try:
            data = req.data["data"]
            scenario_name = data["scenario_name"]
            userid = data["userid"]
            scenario_decription = data["scenario_decription"]
            formid = data["formid"]
        except Exception as e:
            logger.info(f"KEY NOT FOUND {e}")
            return Response(
                {"Key Error": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
            )
        data = None
        try:
            with Session() as session:
                start = perf_counter()
                scenarioid, status = create_scenario(
                    scenario_name, scenario_decription, formid, userid, session
                )
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

                logger.info(f"{dataframe[0]}")

                create_user_data_scenario(
                    dataframe=dataframe, scenarioid=scenarioid, session=session
                )
                logger.info(f"time taken to migrate {perf_counter() - start}")
                # user_scenario_data = get_user_scenario_new(scenarioid=scenarioid, formid=formid, session=session)
                logger.info(f"created scenario with id {scenarioid}")
                data = {
                    "scenarioid": scenarioid,
                    "scenario_name": scenario_name,
                    "scenario_decription": scenario_decription,
                    "scenario_status": status,
                }
                meta = {"code": HTTP_200_OK}
        except Exception as e:
            logger.info(f"Exception in creating hierarchy -> {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["code"])


class UpdateChangePrecentage(APIView):
    def post(self, req, format=None):
        data = req.data["data"]
        datalist = data["datalist"]
        userid = data["userid"]
        scenarioid = data["scenarioid"]

        try:
            filters = create_filter(datalist=datalist)
            data = update_scenario_percentage(
                data, filters, userid=userid, scenarioid=scenarioid
            )
            logger.info(f"Calculation done")
            meta = {"code": HTTP_200_OK}
            logger.info(f"update percentage data len {len(data)}")
        except Exception as e:
            logger.info(f"Exception in Alter Data -> {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
            data = None
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["code"])


class SavesScenario(APIView):
    def post(self, req, format=None):
        data = req.data["data"]
        scenarioid = data["scenarioid"]
        userid = data["userid"]
        formid = data["formid"]
        try:
            data = save_scenario(formid=formid, scenarioid=scenarioid, userid=userid)
            meta = {"code": HTTP_200_OK}
        except Exception as e:
            logger.info(f"Exception in saving Scenario -> {e}")
            data = None
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["code"])


class FetchFrom(APIView):
    def post(self, req, format=None):
        data = None
        try:
            userid = req.data["data"]["userid"]
            orgid = req.data["data"]["organizationId"]
            logger.info(f"{userid=} {orgid=}")
            data = fetch_from(userid=userid, orgid=orgid)
            meta = {"code": HTTP_200_OK}
        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["code"])


class FetchScenario(APIView):
    def post(self, req, format=None):
        scenario_names = []

        try:
            formid = req.data["data"]["formid"]
            userid = req.data["data"]["userid"]
            scenario_names = fetch_scenario(formid=formid, userid=userid)
            data, meta = scenario_names, {"code": HTTP_200_OK}
        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            data = None
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["code"])


class GetData(APIView):
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
            meta = {"code": HTTP_200_OK}
        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["code"])


class filterColumn(APIView):
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
            meta = {"code": HTTP_200_OK}
        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["code"])


class GetScenario(APIView):
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
            meta = {"code": HTTP_200_OK}
        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["code"])


class UpdateBudget(APIView):
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
            logger.info(f"Calculation done")
            meta = {"code": HTTP_200_OK}
            logger.info(f"update percentage data len {data}")
        except Exception as e:
            logger.info(f"Exception in Alter Data -> {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
            data = None
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["code"])


class UpdateChangeValue(APIView):
    def post(self, req, format=None):
        data = req.data["data"]
        datalist = data["datalist"]
        userid = data["userid"]
        scenarioid = data["scenarioid"]

        try:
            filters = create_filter(datalist=datalist)
            data = update_change_value(
                data, filters, userid=userid, scenarioid=scenarioid
            )
            logger.info(f"Calculation done")
            meta = {"code": HTTP_200_OK}
            logger.info(f"update percentage data len {data}")
        except Exception as e:
            logger.info(f"Exception in Alter Data -> {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
            data = None
        create_response(data, **meta)
        return Response(constants.STATUS200, status=meta["code"])


class TokenAPIView(APIView):
    def get(self, req):
        try:
            orgid = req.GET["organizationId"]
            email = req.GET["email"]
        except KeyError as e:
            logger.info(f"{req.GET=}")
            return Response(
                {"Key Error": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
            )
        try:
            payload = {
                "clientSecret": settings.SECRET_CLIENT, 
                "clientId": settings.SECRET_CLIENTID, 
                "email": email }
            
            logger.info(f"{payload=}")
            
            url = constants.get_config("parameters", "identityUrl") + "/jwt/generate-jwt"
            logger.info(f"{url=}")
            resp = post(
                url,
                headers= {
                'Content-Type': 'application/json',
                },
                json={"data": payload},
            )
            token = resp.json()["data"]
            
            logger.info(f"{resp=} {token=}")
            
            url = constants.get_config("parameters", "identityUrl") + "/jwt/sso-lumenore"
            logger.info(f"{url=}")
            
            response = post(
                url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={
                    "jwt": token,
                    "return_to": constants.get_config("parameters", "financeAppRedirectUrl") + "/",
                    "clientId": settings.SECRET_CLIENTID,
                },
            )

            if response.status_code == 200:
                redirect_url = response.text.strip('"')
                logger.info(redirect_url)
            else:
                logger.exception(f"Error: {response.status_code} - {response.text}")

            meta = {"code": HTTP_200_OK}
        except Exception as e:
            logger.info(f"Exception in SSO -> {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
            redirect_url = constants.get_config("parameters", "financeAppRedirectUrl")
        return HttpResponseRedirect(redirect_to=redirect_url)
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.views import APIView
from .utils import create_response, data_formatter, format_df, alter_data, create_filter
from djangoproject.constants import Constants
from djangoproject.main_logger import set_up_logging
from json import loads
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
    update_scenario,
    save_scenario,
    Session
)
from time import perf_counter
from pathlib import Path
import pandas as pd


constants = Constants()
logger = set_up_logging()

BASE_DIR = Path(__file__).resolve().parent.parent


class CreateHierarchy(APIView):
    def post(self, req, format=None):
        try:
            file = req.FILES["file"]
            userid = req.POST["userid"]
            orgid = req.POST["organizationId"]
        except Exception as e:
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
            meta = {}
        except Exception as e:
            logger.info(f"Exception in creating hierarchy -> {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)
    
    def put(self, req, format=None):
        try:
            data = req.data["data"]
            userid = data["userid"]
            scenarioid = data["scenarioid"]
            status = data["status"]
            formid = data["formid"]
        except Exception as e:
        
            return Response(
                {"Key Error": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
            )
        try:
            data = scenario_status_update(userid=userid, scenarioid=scenarioid, formid=formid, status=status)
            meta={}
        except Exception as e:
            logger.info(f"Exception in creating hierarchy -> {e}")
            data = {}
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)
        

    def delete(self, req, format=None):
        try:
            data = req.data["data"]
            userid = data["userid"]
            scenarioid = data["scenarioid"]
            status = data["status"]
            formid = data["formid"]
        except Exception as e:
        
            return Response(
                {"Key Error": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
            )
        try:
            logger.info(F"{status} {type(status)}")
            data = scenario_data_status_update(userid, scenarioid, formid, status, session=None, created_session=False)
            meta={}
        except Exception as e:
            logger.info(f"Exception in creating hierarchy -> {e}")
            data = {}
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)

    @staticmethod
    def save_matrix(df, filename, **kwargs):
        try:
            formid = create_form(filename, kwargs.get("userid"), kwargs.get("orgid"))
            if formid is not None:
                logger.info(f"created form wih id -> {formid}")
                df = format_df(df, formid=formid, userid=kwargs.get("userid"))
                user_data = create_user_data(df, formid, userid=kwargs.get("userid"))
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
            return Response(
                {"Key Error": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
            )
        data = None
        try:
             with Session() as session:
                start = perf_counter()
                scenarioid, status = create_scenario(scenario_name, scenario_decription, formid, userid, session)
                dataframe = get_user_data(formid=formid, userid=userid, session=session)
                logger.info(f"time taken while saving scenario meta and fetching user data {perf_counter() - start}")

                data = format_df(pd.DataFrame(dataframe), scenarioid=scenarioid, userid=userid)
                logger.info(f"time taken while saving scenario meta and fetching user data {perf_counter() - start}")
                create_user_data_scenario(df=data, scenarioid=scenarioid, session=session)
                # user_scenario_data = get_user_scenario_new(scenarioid=scenarioid, formid=formid, session=session)
                logger.info(f"created scenario with id {scenarioid}")
                data = {"scenarioid":scenarioid, "scenario_name":scenario_name, "scenario_decription":scenario_decription, "scenario_status":status}
                meta = {}
        except Exception as e:
            logger.info(f"Exception in creating hierarchy -> {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)
    
            
        


class UpdateChangeValue(APIView):
    def post(self, req, format=None):
        data = req.data["data"]
        datalist = data["datalist"]
        userid= data["userid"]
        scenarioid= data["scenarioid"]
        
        try:
            filters = create_filter(datalist=datalist)
            data = update_scenario(data, filters, userid=userid, scenarioid=scenarioid)
            logger.info(f"Calculation done")
            meta =  {}
            logger.info(f"alter data len {len(data)}")
        except Exception as e:
            logger.info(f"Exception in Alter Data -> {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
            data = None
        create_response(data, **meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)



class AlterData(APIView):
    def post(self, req, format=None):
        data = req.data["data"]
        datalist = data["datalist"]
        userid= data["userid"]
        formid= data["formid"]
        dataframe = get_user_data(userid=userid, formid=formid)
        df = pd.DataFrame(dataframe)
        
        try:
            modified_dfs = alter_data(df, datalist=datalist)
            logger.info(f"Calculation done")
            result_df = pd.concat(modified_dfs, ignore_index=True)
            data, meta = loads(result_df.drop(columns=["Date"]).to_json(orient="records")),{}
            logger.info(f"alter data len {len(data)}")
        except Exception as e:
            logger.info(f"Exception in Alter Data -> {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
            data = None
        create_response(data, **meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)


class SavesScenario(APIView):
    def post(self, req, format=None):
        data = req.data["data"]
        scenarioid = data["scenarioid"]
        userid = data["userid"]
        formid = data["formid"]
        try:
            data = save_scenario(formid=formid, scenarioid=scenarioid,userid=userid)
            meta ={}
        except Exception as e:
            logger.info(f"Exception in saving Scenario -> {e}")
            data = None
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data,**meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)


class FetchFrom(APIView):
    def post(self, req, format=None):
        data = None
        try:
            userid = req.data["data"]["userid"]
            orgid = req.data["data"]["organizationId"]
            logger.info(f"{userid=} {orgid=}")
            data = fetch_from(userid=userid, orgid=orgid)
            meta = {}
        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)


class FetchScenario(APIView):
    def post(self, req, format=None):
        scenario_names = []

        try:
            formid = req.data["data"]["formid"]
            userid = req.data["data"]["userid"]
            scenario_names = fetch_scenario(formid=formid,userid=userid)
            data, meta =  scenario_names, {}
        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            data = None
            meta = {
                "error": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)


class GetData(APIView):
    def post(self, req, format=None):
        data = {}
        try:
            logger.info(f"{req.data=}")
            formid = req.data["data"]["formid"]
            userid = req.data["data"]["userid"]
            start = perf_counter()
            data = get_user_data(formid=formid, userid=userid)
            logger.info(f"time taken while fetching data for  {userid} is {perf_counter()-start} ")
            meta = {}
        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)
    

class filterColumn(APIView):
    def post(self, req, format=None):
        data = {}
        try:
            logger.info(f"{req.data=}")
            formid = req.data["data"]["formid"]
            userid = req.data["data"]["userid"]
            scenarioid = req.data["data"]["scenarioid"]
            unit_value = req.data["data"]["unit"]
            start = perf_counter()
            data = filter_column(scenarioid=scenarioid,formid=formid, userid=userid,value=unit_value)
            data = { 
                "column_name": data[0].keys(),
                "row_names":data
            }
            logger.info(f"time taken while fetching data for  {userid} is {perf_counter()-start}")
            meta = {}
        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)


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
                "scenarioid":scenarioid,
                "column_name": data[0].keys(),
                "row_names":data
            }            
            logger.info(f"time taken after fetching and for {userid} is {perf_counter()-start} ")
            meta = {}
        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            meta = {
                "error_message": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)
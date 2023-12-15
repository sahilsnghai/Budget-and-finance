from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.views import APIView
from .utils import create_response, data_formatter, format_df, alter_data, alter_data_df
from djangoproject.constants import Constants
from djangoproject.main_logger import set_up_logging
from threading import Thread
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
    get_user_scenario,
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
                "Error": str(e),
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
        return {
            "column_name":user_data[0].keys(),
            "row_names":user_data
            } 

    @staticmethod
    def create_hierarchy(df, **kwargs):
        """
        input -> execl-file.xlsx
        output  ->
        {
            "column_name": [
                "Class / LOB",
                "Entity (Line): Name (Grouped)",
                "Account Type",
                "Account",
                "Project Name: Name",
                "base value"
            ],
            "row_names": [
                {

                    "Class / LOB": "IBG",
                    "Entity (Line): Name (Grouped)": "DEPL O&M Limited",
                    "Account Type": "1. Income",
                    "Account": "Base Revenue",
                    "Project Name: Name": "BSNL: Fibre AMC",
                    "base value": -392894.021144732,
                    "total: -315955.766192733,
                    "January":981221,
                    "Febaruy":7982398
                }
            ]
        }
        """
        pass
        # start = perf_counter()
        
        # data = CreateHierarchy.save_matrix(df)
        
        # data = saved_user_data.join()
        # logger.info("got data")
        # logger.info(f"{data=}")

        # logger.info(f"time by read excel {perf_counter() - start}")
        # df = df.groupby([df.columns[0]] + df.columns[1:-1].tolist(), as_index=False)[
        #     df.columns[-1]
        # ].sum()
        # logger.info(f"df.columns {df.columns}")
        # df["date_str"] = pd.to_datetime(df[df.columns[0]]).dt.strftime("%B")
        # df["month"] = df.groupby(list(df.columns[:-1]))[[df.columns[-2]]].transform(
        #     "sum"
        # )
        # df["month"] = df.apply(lambda x: {x["date_str"]: x["month"]}, axis=1)
        # logger.info(f"time by formatting {perf_counter() - start}")

        # months = df["date_str"].unique().tolist()
        # df = df.drop(columns="date_str")
        # columns = df.columns[:-1].to_list() + months
        # row_names = loads(df[df.columns[:]].to_json(orient="records"))
        # logger.info(f"time by months, rows and columns {perf_counter() - start}")

        # for item in row_names:
        #     if isinstance(item.get("month"), dict):
        #         item.update(item.pop("month"))
        # logger.info(f"time by for loop {perf_counter() - start}")
        # logger.info(f"len of rows {len(row_names)}")
        # return data


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
                "Error": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
            data = None
        create_response(data, **meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)


class SavesScenario(APIView):
    def post(self, req, format=None):
        data = req.data["data"]
        scenario_name = data["scenario_name"]
        userid = data["userid"]
        scenario_decription = data["scenario_decription"]
        formid = data["formid"]
        datalist = data["datalist"]
        try:
            with Session() as session:
                start= perf_counter()
                scenarioid = create_scenario(scenario_name, scenario_decription, formid, userid, session)
                dataframe = get_user_data(formid=formid, userid=userid, session=session)
                logger.info(f"time taken while saving scenario meta and fetching user data {perf_counter() - start}")
                df = data_formatter(dataframe, False)
                df = alter_data_df(df, scenarioid, datalist=datalist)
                df = format_df(df, scenarioid=scenarioid,userid=userid)
                logger.info(f"time taken while alterations {perf_counter() - start}")
                data = create_user_data_scenario(df, scenarioid=scenarioid, session=session)
                logger.info(f"time taken saving complete data with change  {perf_counter() - start}")
                logger.info(f"{scenarioid=}")
                data = {"scenarioid":scenarioid}
                meta ={}
        except Exception as e:
            logger.info(f"Exception in saving Scenario -> {e}")
            data = None
            meta = {
                "Error": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data,**meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)


class FetchFrom(APIView):
    def post(self, req, format=None):
        data = None
        try:
            logger.info(f"{req.data}")
            userid = req.data["data"]["userid"]
            orgid = req.data["data"]["organizationId"]
            logger.info(f"{userid=} {orgid=}")
            data = fetch_from(userid=userid, orgid=orgid)
            meta = {}
        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            meta = {
                "Error": str(e),
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
            data = data_formatter(data)
            logger.info(f"time taken after fetching and for pandas in GetData {userid} is {perf_counter()-start} ")
            meta = {}
        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            meta = {
                "Error": str(e),
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
            unit_value = req.data["data"]["unit"]
            start = perf_counter()
            data = filter_column(formid=formid, userid=userid,value=unit_value)
            logger.info(f"time taken while fetching data for  {userid} is {perf_counter()-start}")
            meta = {}
        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            meta = {
                "Error": str(e),
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
            start = perf_counter()
            data = get_user_scenario(scenarioid, session=None, created_session=False)
            logger.info(f"time taken while fetching data for  {userid} is {perf_counter()-start}")
            data = data_formatter(data)
            logger.info(f"time taken after fetching and for pandas in GetData {userid} is {perf_counter()-start} ")
            meta = {}
        except Exception as e:
            logger.exception(f"exception while fetching form names:  {e}")
            meta = {
                "Error": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        create_response(data, **meta)
        return Response(constants.STATUS200, status=HTTP_200_OK)
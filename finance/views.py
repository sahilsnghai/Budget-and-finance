from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.views import APIView
from .utils import create_response
from djangoproject.constants import Constants
from djangoproject.main_logger import set_up_logging
from threading import Thread
from json import loads
# from .utils import create_form, create_user_data
import pandas as pd
from time import perf_counter


constants = Constants()
logger = set_up_logging()


BASE_DIR = "/home/ssjain/Desktop/lumenore/django-project/djangoproject/finance"


class CreateHierarchy(APIView):
    def post(self, req, format=None):
        try:
            file = req.FILES["file"]
            userid = req.POST.get("userid")
            orgid = req.POST.get("organizationId")
        except Exception as e:
            return Response(
                {"Key Error": f"key {e} not found"}, status=HTTP_400_BAD_REQUEST
            )
        data = None
        try:
            start = perf_counter()
            data = self.create_hierarchy(file, userid=userid, orgid=orgid)
            logger.info(f"time by hierarchy {perf_counter() - start}")
            data = {"data": data}
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
    def save_matrix(df, filename, table_name="example_table", **kwargs):
        try:
            # formid = create_form(filename, kwargs.get("userid"), kwargs.get("orgid"))
            # create_user_data(df, formid)
            pass
        except Exception as e:
            logger.exception(e)

        pass

    @staticmethod
    def create_hierarchy(file, **kawrgs):
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
                },
                {

                    "Class / LOB": "AI/ML",
                    "Entity (Line): Name (Grouped)": "National Health Mission",
                    "Account Type": "1. Income",
                    "Account": "Growth revenue",
                    "Project Name: Name": "NHM: Product Development",
                    "base value": -315955.766192733
                    "forecast value": -315955.766192733,
                    "month data":[
                        {"January":981221},
                        {"Febaruy":7982398}
                        ]
                },
            ]
        }
        """
        start = perf_counter()
        df = pd.read_excel(file)
        Thread(
            target=CreateHierarchy.save_matrix,
            daemon=True,
            args=(df, file.name),
            kwargs=kawrgs,
        ).start()
        logger.info(f"time by read excel {perf_counter() - start}")

        df = df.groupby(df.columns[:-1].tolist(), as_index=False)[df.columns[-1]].sum()
        df["date_str"] = pd.to_datetime(df[df.columns[0]]).dt.strftime("%B")
        df["month"] = df.groupby(list(df.columns[:-1]))[[df.columns[-2]]].transform("sum")
        df["month"] = df.apply(lambda x: {x["date_str"]: x["month"]}, axis=1)
        logger.info(f"time by formatting {perf_counter() - start}")

        months = df["date_str"].unique().tolist()
        df = df.drop(columns="date_str")
        columns = df.columns[1:-1].to_list() + months
        row_names = loads(df[df.columns[1:]].to_json(orient="records"))
        logger.info(f"time by months, rows and columns {perf_counter() - start}")

        for item in row_names:
            if isinstance(item.get("month"), dict):
                item.update(item.pop("month"))
        logger.info(f"time by for loop {perf_counter() - start}")

        return {
            "column_names": columns,
            "row_names": row_names,
        }


class SavesScenario(APIView):
    def post(self, req, format=None):
        data = req.data["data"]
        try:
            pass
        except Exception as e:
            logger.info(f"Exception in creating hierarchy -> {e}")

        return Response(constants.STATUS200, status=HTTP_200_OK)

    @staticmethod
    def save_scenario(data):
        return {"save": "done"}


class FetchFrom(APIView):
    def post(self, req, format=None):
        pass


class FetchScenario(APIView):
    def post(self, req, format=None):
        pass


class GetData(APIView):
    def post(self, req, format=None):
        pass

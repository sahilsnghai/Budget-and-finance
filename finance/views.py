from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.views import APIView
from .utils import create_response, get_connection
from djangoproject.constants import Constants
from djangoproject.main_logger import set_up_logging
from threading import Thread
from django.db import models
from json import loads, dumps
from rest_framework.parsers import MultiPartParser
import pandas as pd


constants = Constants()
logger = set_up_logging()


BASE_DIR = "/home/ssjain/Desktop/lumenore/django-project/djangoproject/finance"


class CreateHierarchy(APIView):
    def post(self, req, format=None):
        try:
            file = req.FILES["file"]
        except:
            file = req.data["file"]
        data = None
        try:
            data = self.create_hierarchy(file)
            data = {"data": data}
            meta = {}
        except Exception as e:
            logger.info(f"Exception in creating hierarchy -> {e}")
            meta = {
                "Error": str(e),
                "error": True,
                "code": HTTP_500_INTERNAL_SERVER_ERROR,
            }
        print("done")
        create_response(data, **meta)

        return Response(constants.STATUS200, status=HTTP_200_OK)

    @staticmethod
    def save_matrix(df, table_name="example_table"):
        pass

    @staticmethod
    def create_hierarchy(file):
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
        df = pd.read_excel(file)

        Thread(target=CreateHierarchy.save_matrix, daemon=True, args=(df,)).start()
        df = df.rename(columns={df.columns[-1]: "base value"})
        df["date_str"] = pd.to_datetime(df['Date']).dt.strftime("%B")
        df["month"] = df.groupby(list(df.columns[:-2]))[["base value"]].transform("sum")
        df['month'] = df.apply(lambda x: {x['date_str']: x['month']}, axis=1)
        
        df = df.drop(columns="date_str")
        columns = df.columns[1:].to_list()
        row_names = loads(df[df.columns[1:]].to_json(orient="records"))

        for item in row_names:
            if isinstance(item.get("month"), dict):
                item.update(item.pop("month"))

        return {
            "column_name": columns,
            "row_names" : row_names,
        }


class SavesSenario(APIView):
    def post(self, req, format=None):
        data = req.data["data"]
        try:
            if not isinstance(data, dict):
                return Response(
                    {"Error": "Incorrect Payload"}, status=HTTP_400_BAD_REQUEST
                )
            hierarchy = self.save_scenario(data)
            create_response(hierarchy)
        except Exception as e:
            logger.info(f"Exception in creating hierarchy -> {e}")

        return Response(constants.STATUS200, status=HTTP_200_OK)

    @staticmethod
    def save_scenario(data):
        return {"save": "done"}

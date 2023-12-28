from djangoproject.constants import Constants
from rest_framework.status import HTTP_200_OK
from json import loads
from djangoproject.main_logger import set_up_logging
from .database.db import engine

import pandas as pd

constants = Constants()
logger = set_up_logging()


COLUMNS = {
    "Date": "date",
    "Receipt Number": "receipt_number",
    "Business Unit": "business_unit",
    "Account Type": "account_type",
    "Account SubType": "account_subtype",
    "Project Name": "project_name",
    "Customer Name": "customer_name",
    "Amount Type": "amount_type",
    "Amount": "amount",
}


def create_response(data, code=HTTP_200_OK, error=False, **kwags):
    logger.info(f"kwags = {kwags}")
    constants.STATUS200["error"] = error

    logger.info(f"Checking error message {kwags.get('error_message', None)}")
    if kwags.get("error_message", None) and error:
        constants.STATUS200["error_message"] = kwags.get("error_message")
    else:
        constants.STATUS200.pop("error_message", None)
    constants.STATUS200["status"]["code"] = code
    constants.STATUS200["data"] = data
    logger.info(f"Session Status : {engine.pool.status()}")
    engine.pool.dispose()


def format_df(df, *args, **kwargs):
    logger.info(f"Before renaming: {df.columns}")
    df = df.rename(columns=COLUMNS)
    if common_columns := set(["data_id", "base value"]).intersection(df.columns):
        logger.info(common_columns)
        df = df.drop(columns=common_columns)
    logger.info(f"updated columns :\n{df.columns}")
    df["amount_type"] = df["amount_type"].replace(
        {"Actual": 1, "Projected": 0, "Budgeting": 0, "Budget": 0}
    )
    logger.info(f"{kwargs=}")
    df["created_by"] = df["modified_by"] = kwargs.get("userid", None)
    if formid := kwargs.get("formid", None):
        df["fn_form_id"] = formid
    elif scenarioid := kwargs.get("scenarioid", None):
        logger.info(f"working on {scenarioid}")
        df["fn_scenario_id"] = scenarioid
    logger.info(f"{len(df)}")
    return df


def create_filter(datalist):
    logger.info(f"Creating filters.")
    filters_list = []
    changes_list = []
    change_value = {}

    for row in datalist:
        filters = {}
        if row.get("changePrecentage") is not None:
            change_value = {"changePrecentage": (row["changePrecentage"] / 100) + 1}
        elif row.get("changeValue") is not None:
            change_value = {
                "changeValue": row["changeValue"],
                "date": row["date"],
                "dateformat": row.get("dateformat", "%Y%m"),
            }

        if row.get("amount_type") is not None:
            filters.update({"amount_type": row["amount_type"]})

        row["columns"] = [COLUMNS[column] for column in row["columns"]]

        filters.update(zip(row["columns"], row["rows"]))

        filters_list.append(filters)
        changes_list.append(change_value)

    logger.info(filters_list)
    logger.info(changes_list)
    logger.info(f"Filters created.")

    return zip(filters_list, changes_list)

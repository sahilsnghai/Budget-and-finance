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
    "Amount Type": "amount_type",
    "Amount": "amount",
}

def create_response(data, code =HTTP_200_OK, error=False, **kwags):
    constants.STATUS200["error"] = error
    constants.STATUS200["status"]["code"] = code
    constants.STATUS200["data"] = data
    logger.info(f"Session Status : {engine.pool.status()}")


def data_formatter(data, load=True):
    df = pd.DataFrame(data)
    print(data[0])
    df["amount_type"] = df["amount_type"].map({1: "Actual", 0: "Projected"})
    columns = {value : key for key, value in COLUMNS.items()}
    df = df.rename(columns=columns)
    data = loads(df.to_json(orient="records")) if load else df
    return data


def format_df(df,*args, **kwargs):

    df = df.rename(
        columns=COLUMNS)
    
    df["amount_type"] = df["amount_type"].replace(
        {"Actual": 1, "Projected": 0, "Budgeting": 0, "Budget": 0})
    logger.info(f"{kwargs=}")
    if formid := kwargs.get("formid",None):
        df["fn_form_id"] = formid
        df["created_by"] = df["modified_by"] = kwargs.get("userid",None)
    elif scenarioid := kwargs.get("scenarioid",None):
        logger.info(f"working on {scenarioid}")
        df["fn_scenario_id"] = scenarioid
        df["created_by"] = df["modified_by"] = kwargs.get("userid",None)
    
    logger.info(f"{len(df)}")

    return df

def alter_data(df, datalist):
    modified_dfs = []
    for data in datalist:
        columns_to_group = data["columns"]
        rows_to_increase = tuple(data["rows"])
        change_percentage = data["changePrecentage"] / 100 + 1

        grouped_df = df.groupby(columns_to_group)
        selected_group = grouped_df.get_group(rows_to_increase)
        selected_group_copy = selected_group.copy()
        
        amount_column = df.columns[-1]
        selected_group_copy[amount_column] *= change_percentage
        modified_dfs.append(selected_group_copy)
    return modified_dfs


def alter_data_df(df, scenarioid, datalist):    
    for data in datalist:
        columns_to_group = data["columns"]
        rows_to_increase = tuple(data["rows"])
        change_percentage = data["changePrecentage"] / 100 + 1
        grouped_df = df.groupby(columns_to_group)
        selected_group = grouped_df.get_group(rows_to_increase)

        amount_column = df.columns[-1]
        df.loc[selected_group.index, "change_value"] = change_percentage
        df.loc[selected_group.index, amount_column] *= change_percentage
    df["change_value"].fillna(1, inplace=True)
    return df
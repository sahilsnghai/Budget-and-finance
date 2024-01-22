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

"""utils"""

from lumenore_apps.constants import Constants
from rest_framework.status import HTTP_200_OK
from lumenore_apps.main_logger import set_up_logging


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


def create_response(data, status_code=HTTP_200_OK, error=False, **kwags):
    '''create_response universal response format

    Args:
        data (response data):
        status_code (HTTP status_code, optional): Defaults to HTTP_200_OK.
        error (bool, optional): Defaults to False.
    '''
    logger.info(f"kwags = {kwags}")
    constants.STATUS200["error"] = error

    logger.info(f"Checking error message {kwags.get('error_message', None)}")
    if kwags.get("error_message", None) and error:
        constants.STATUS200["error_message"] = kwags.get("error_message")
    else:
        constants.STATUS200.pop("error_message", None)
    constants.STATUS200["status"]["code"] = status_code
    constants.STATUS200["data"] = data
    logger.info(f" {constants.engine.dispose()} ")
    logger.info(f" {constants.engine.pool.status()} ")
    logger.info(f"{'':->100}")


async def format_df(df, **kwargs):
    '''format_df to format data

    Args:
        df (dataframe):

    Returns:
        format data: datadrame
    '''
    logger.info(f"Before renaming: {df.columns}")
    df = df.rename(columns=COLUMNS)
    df["amount_type"] = df["amount_type"].replace(
        {"Actual": 1, "Projected": 0, "Budgeting": 0, "Budget": 0}
    )
    logger.info(f"{kwargs=}")
    df["created_by"] = df["modified_by"] = kwargs.get("userid", None)
    df["fn_form_id"] = kwargs.get("formid", None)
    logger.info(f"{len(df)}")
    return df


def create_filter(datalist):
    '''create_filter to filter out data which needs to be updated

    Args:
        datalist (list(dicts)):

    Returns:
        zip object: {filters: values}
    '''
    row = datalist
    logger.info("Creating filters.")
    change_value = {}

    filters = {}
    if row.get("changePrecentage") is not None:
        logger.info(f"{row['changePrecentage']=}")
        change_value = {
            "changePrecentage": row.get("changePrecentage")
            if row.get("changePrecentage") in [0, -100]
            else (row["changePrecentage"] / 100) + 1
        }
        logger.info(f"{change_value=}")
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

    logger.info("Filters created.")

    return (filters, change_value)

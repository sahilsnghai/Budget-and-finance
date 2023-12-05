from djangoproject.constants import Constants
from rest_framework.status import HTTP_200_OK
import MySQLdb


constants = Constants()


def create_response(data, code =HTTP_200_OK, error=False, **kwags):
    constants.STATUS200["error"] = error
    constants.STATUS200["status"]["code"] = code
    constants.STATUS200["data"] = data


def get_connection(org='financeApp'):
    connection = MySQLdb.connect(
        **constants.get_conn_info(org=org)
    )
    return connection

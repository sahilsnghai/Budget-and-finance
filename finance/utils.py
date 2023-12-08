from djangoproject.constants import Constants
from rest_framework.status import HTTP_200_OK

constants = Constants()

def create_response(data, code =HTTP_200_OK, error=False, **kwags):
    constants.STATUS200["error"] = error
    constants.STATUS200["status"]["code"] = code
    constants.STATUS200["data"] = data
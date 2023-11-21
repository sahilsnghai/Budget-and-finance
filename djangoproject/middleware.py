from djangoproject.main_logger import set_up_logging
from djangoproject.constants import Constants
from django.http import HttpResponse, HttpResponseForbidden
from requests import get
import jwt

logger = set_up_logging()
constants = Constants()


def task_middleware(get_response):
    def middleware(req):
        
        print(f"{req.headers=}")

        # if process_req(req=req):
        response = get_response(req)
        # else:
            # response = HttpResponseForbidden(req)
        return response

    return middleware


def process_req(req):
    """

    Parameters
    ----------
    req
    resp
    """
    try:
        token = get_token(req.headers["Authorization"])
        constants.HEADERS["Authorization"] = token
        if token and not _token_is_valid(token, req):
            raise HttpResponse("Authentication required", status=401)
        auth = True
    except Exception as e:
        logger.info(f"Authentication failed due to {e}")
        auth = False
    return auth


def _token_is_valid(token, req):
    """

    Parameters
    ----------
    req

    """
    try:
        token = token.split()
        decoded_token = jwt.decode(
            token[1],
            key=token[0],
            algorithms="HS256",
            options={"verify_signature": False},
        )
        constants.time_zone = req.headers.get("TIMEZONE", "US/Eastern")
        req.context = decoded_token["userVo"]
        logger.info(decoded_token)
        auth = True

    except Exception as ex:
        logger.exception(f"Token could not be validated:\t{ex}")
        auth = False
    return auth


def get_token(token, version=None):
    """this function is to retrive token from identity service"""
    try:
        token = token.split()
        url = (
            constants.get_config("parameters", "identity-url")
            + f"/identity/userData-token?token={token[1]}"
        )
        headers = {"version": "qa", "Authorization": f"{token[0]} {token[1]}"}
        response = get(url, headers=headers).json()["data"]
        response = f'{token[0]} {response}' or token
        logger.info(f"{response=}")
    except Exception as e:
        logger.exception(f"error in getting bigget token {e}")
        response = token
    return response

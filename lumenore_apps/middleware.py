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

"""middleware"""

from lumenore_apps.main_logger import set_up_logging
from lumenore_apps.constants import Constants
from django.http import JsonResponse, HttpResponse
from rest_framework.status import HTTP_401_UNAUTHORIZED

from rest_framework.views import APIView
from requests import get
import jwt

logger = set_up_logging()
constants = Constants()


EXCLUDED_PATHS = [
    '/finance/sso',
    '/finance/login/',
    '/health/'
]

class GetHealth(APIView):
    '''GetHealth

    Args:
        APIView (_type_):
    '''
    def get (self, req):
        return HttpResponse(status=200)

def middleware(get_response):
    '''middleware

    Args:
        get_response (_type_):
    '''
    def app_middleware(req):
        '''app_middleware

        Args:
            req (_type_):

        Returns:
            _type_:
        '''
        logger.info(f"{'-'*100} \n{req.build_absolute_uri()} \n")
        validity = True if req.path in EXCLUDED_PATHS else process_req(req=req)
        logger.info(f"{validity=}")

        if validity :
            response = get_response(req)
        else:
            response = JsonResponse({"Authorization": "Authorization Failed"}, status=HTTP_401_UNAUTHORIZED)
        return response

    return app_middleware


def process_req(req):
    """

    Parameters
    ----------
    req
    resp
    """
    try:
        token = req.headers.get("Authorization")
        logger.info(f"{token=}")
        if token and not _token_is_valid(token, req):
            raise PermissionError("Unauthentication")
        auth = True
    except Exception as e:
        logger.exception(f"Authentication failed due to {e}")
        auth = False
    return auth


def _token_is_valid(token, req):
    """

    Parameters
    ----------
    req

    """
    auth = False
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
        logger.info(f"{req.context=}")
        if req.context:
            auth = True
    except Exception as ex:
        logger.exception(f"Token could not be validated: {ex}")
        auth = False
    return auth


def get_token(token):
    """this function is to retrive token from identity service"""
    try:
        token = token.split()
        url = (
            constants.get_config("parameters", "identity-url")
            + f"/identity/userData-token?token={token[1]}"
        )
        headers = {"version": "qa", "Authorization": f"{token[0]} {token[1]}"}
        response = get(url, headers=headers).json()["data"]
        response = f'{token[0]} {response}' if response else token
    except Exception as e:
        token = jwt.decode(token)
        logger.exception(f"error in getting bigget token {e}")
        response = token
    return response

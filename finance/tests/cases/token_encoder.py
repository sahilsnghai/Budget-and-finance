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

"""Generate token using pyjwt or get from api"""

import jwt


def get_token(payload: dict):
    """This function generate the jwt token which can then be used to test apis"""

    encoded = jwt.encode(payload=payload, key="Bearer", algorithm="HS256")
    return encoded


def get_header(user_id, email, org_id):
    """returns header"""

    token = get_token(
        {
            "userVo": {
                "id": user_id,
                "email": email,
                "organizationId": org_id,
                "organization": {
                    "name": "Salesforcedemo",
                    "isWarningOnSharing": True,
                    "active": False,
                },
                "roles": [
                    {
                        "roleId": 529,
                        "roleName": "this is is",
                        "accessType": "Admin",
                        "role": None,
                        "userType": None,
                    }
                ],
            }
        }
    )
    return {
        "content-type": "application/json",
        "version": "rsh",
        "authorization": f"Bearer {token}",
        "test": "True",
    }

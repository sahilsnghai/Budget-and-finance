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

"""test_endpoint"""

import pytest
import secrets
from rest_framework.test import APIClient
from unittest.mock import patch, Mock, MagicMock
from django.urls import reverse
from urllib.parse import parse_qs, urlparse
from .cases.cases import (
    get_header,
    userid,
    scenarioid,
    formid,
    organizationId,
    email,
    get_token,
)

Account_Type = "Account Type"

@pytest.fixture
def client():
    """client

    Returns:
        _type_:
    """
    return APIClient()


@patch("finance.database.get_data.Session")
def test_form_status(mock_session, client: APIClient):
    """Change Form Status

    Args:
        client (APIClient): for request and response
    """
    mock_session_instance = MagicMock()
    mock_session_instance.query.return_value.filter.return_value.update.return_value = 1
    mock_session.return_value = mock_session_instance
    payload = {
        "data": {
            "userid": userid,
            "scenarioid": scenarioid,
            "formid": formid,
            "status": True,
        }
    }
    response = client.put(
        reverse("create-form"),
        headers=get_header(user_id=userid, org_id=organizationId, email=email),
        data=payload,
    )
    assert response.status_code == 200
    assert response.json()["data"] == 1


@patch("finance.database.get_data.FnScenario")
@patch("finance.database.get_data.fetch_scenario")
@patch("finance.views.get_user_data")
@patch("finance.views.Session")
def test_crud_scenario(mock_session, mock_get_user_data,mock_fetch_scenario,mock_fn_scenario,client: APIClient):
    '''test_crud_scenario _summary_

    Args:
        mock_session (Mock): Mock()
        mock_get_user_data (Mock): Mock()
        mock_fetch_scenario (Mock): Mock()
        mock_fn_scenario (Mock): Mock()
        client (APIClient): APIClient
    '''
    mock_session_instance = MagicMock()
    mock_session_instance.query.return_value.filter.return_value.update.return_value = None
    mock_session.side_effect = [mock_session_instance,mock_session_instance]
    mock_fetch_scenario.return_value= [{"scenario_name":"xyz"}]
    mock_get_user_data.return_value = [{},{},{}]
    mock_scenario_instance = mock_fn_scenario.return_value
    mock_scenario_instance.fn_scenario_id = 1234
    mock_scenario_instance.is_active = True

    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
        "data": {
            "scenario_name": "Test",
            "scenario_decription": "scenario_decription",
            "formid": formid,
            "userid": userid,
        }
    }
    response = client.post(
        reverse("create-scenario"),
        headers=headers,
        data=create_payload,
    )

    body = response.json()

    assert response.status_code == 200
    assert body["data"]["scenario_status"] == True

    scenarioid = body["data"]["scenarioid"]

    save_payload = {
        "data": {
            "scenarioid": scenarioid,
            "formid": formid,
            "userid": userid,
            "scenario_name": "TEST",
            "scenario_description": "TEST",
        }
    }
    response = client.post(
        reverse("save-scenario"),
        headers=headers,
        data=save_payload,
    )

    assert response.status_code == 200

    create_payload = {
        "data": {
            "scenario_name": "xyz",
            "scenario_decription": "scenario_decription",
            "formid": formid,
            "userid": userid,
        }
    }
    response = client.post(
        reverse("create-scenario"),
        headers=headers,
        data=create_payload,
    )
    assert response.status_code == 500
    assert response.json()["error_message"] == "Scenario already exists"

    delete_payload = {
        "data": {
            "userid": userid,
            "scenarioid": scenarioid,
            "formid": formid,
            "status": False,
        }
    }
    response = client.delete(
        reverse("create-form"),
        headers=headers,
        data=delete_payload,
    )

    assert response.status_code == 200

    put_payload = {
        "data": {
            "userid": userid,
            "scenarioid": scenarioid,
            "status": True,
            "formid": formid,
        }
    }
    response = client.put(
        reverse('create-scenario'),
        headers=headers,
        data=put_payload,
    )

    assert response.status_code == 200


@patch("finance.views.fetch_from")
@patch("finance.views.Session")
def test_filter_form(mock_session, mock_filter_form, client: APIClient):
    """fetch filter form

    Args:
        client (APIClient): for request and response
    """
    mock_session.return_value = None
    mock_filter_form.return_value = [{}]
    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {"data": {"userid": userid, "organizationId": organizationId}}
    response = client.post(
        reverse("filter-form"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()

    assert response.status_code == 200
    assert len(body["data"]) != 0


@patch("finance.views.fetch_scenario")
@patch("finance.views.Session")
def test_filter_scenario(mock_session, mock_filter_scenario, client: APIClient):
    """fetch filter form

    Args:
        client (APIClient): for request and response
    """
    mock_session.return_value = None
    mock_filter_scenario.return_value = [{}]
    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
        "data": {"userid": userid, "formid": formid, "organizationId": organizationId}
    }
    response = client.post(
        reverse("filter-scenario"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()

    assert response.status_code == 200
    assert len(body["data"]) != 0


@patch("finance.views.get_user_data")
@patch("finance.views.Session")
def test_get_data(mock_session, mock_user_data, client: APIClient):
    """fetch filter form

    Args:
        client (APIClient): for request and response
    """
    mock_session.return_value = None
    mock_user_data.return_value = [{}]
    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {"data": {"userid": userid, "formid": formid}}
    response = client.post(
        reverse("get-data"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()

    assert response.status_code == 200
    assert len(body["data"]) != 0


@patch("finance.views.filter_column")
@patch("finance.views.Session")
def test_filter_column(mock_session, mock_filter_column, client: APIClient):
    """fetch filter form

    Args:
        client (APIClient): for request and response
    """
    mock_session.return_value = None
    mock_filter_column.return_value = [{}]
    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
        "data": {
            "userid": userid,
            "formid": formid,
            "scenarioid": scenarioid,
            "year": 2023,
            "unit": "Business Unit 3",
        }
    }
    response = client.post(
        reverse("filter-column"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()

    assert response.status_code == 200
    assert len(body["data"]) != 0


@patch("finance.views.get_user_scenario_new")
@patch("finance.views.Session")
def test_get_scenario(mock_session, mock_get_user_scenario_new, client: APIClient):
    """fetch filter form

    Args:
        client (APIClient): for request and response
    """
    mock_session.return_value = None
    mock_get_user_scenario_new.return_value = [{}]
    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
        "data": {"userid": userid, "scenarioid": scenarioid, "formid": formid}
    }
    response = client.post(
        reverse("get-scenario"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()

    assert response.status_code == 200
    assert len(body["data"]) != 0


@patch("finance.views.update_scenario_percentage")
@patch("finance.views.Session")
def test_update_scenario(
    mock_session, mock_update_scenario_percentage, client: APIClient
):
    """fetch filter form

    Args:
        client (APIClient): for request and response
    """
    mock_session.return_value = None
    mock_update_scenario_percentage.return_value = [{}]
    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
        "data": {
            "userid": userid,
            "formid": formid,
            "datalist": [
                {"columns": ["Account Type"], "rows": ["COGS"], "changePrecentage": 75}
            ],
            "scenarioid": scenarioid,
            "date": 2022,
        }
    }
    response = client.post(
        reverse("update-scenario"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()

    assert response.status_code == 200
    assert len(body["data"]) != 0

@patch("finance.database.get_data.create_engine_and_session")
@patch("finance.database.get_data.receive_query")
@patch("finance.views.post")
def test_get_secret(
    mock_token_post,
    mock_receive_query,
    mock_create_session,
    client: APIClient,
):
    """Change Form Status

    Args:
        client (APIClient): for request and response
    """
    payload = {"email": email, "organizationId": organizationId, "userid": userid}
    token = get_token(payload)

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.side_effect = [{"data": token}]
    mock_response.text = f"https://qa.lumenore.com/apps/?token={token}"
    mock_token_post.return_value = mock_response

    mock_session = MagicMock()
    mock_session.return_value.query.return_value.filter_retrun_value.all_return_value = 1
    mock_create_session.return_value = mock_session


    mock_receive_query.return_value =[ {"SECRET_CLIENT": "fRNfqXi/*-!G_tDsvz", "SECRET_CLIENTID": "salesforcedemo"}]
    params = {"organizationId": 247, "email": "ssjain@lumenore.com"}
    response = client.get(reverse("sso"), params)
    assert response.status_code == 302
    query_params = parse_qs(urlparse(response.url).query)
    assert query_params["token"][0] == token

    params = {"organizationId": 1111, "email": "ssjain@lumenore.com"}
    response = client.get(reverse("sso"), params)
    assert response.status_code == 302

    params = {"organizationId": 1111}
    response = client.get(reverse("sso"), params)

    assert response.status_code == 302

@patch("finance.database.get_data.receive_query")
@patch("finance.database.get_data.Session")
def test_update_value(mock_session, mock_receive_query,  client: APIClient):
    '''test_update_value _summary_

    Args:
        mock_session (_type_): _description_
        mock_update_value (_type_): _description_
        client (APIClient): _description_
    '''
    mock_receive_query.return_value = [{"change_value":100.0}]

    mock_session_instance = MagicMock()
    mock_session_instance.query.return_value.filter.return_value.update.return_value = 4
    mock_session.return_value = mock_session_instance

    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
    "data": {
        "userid": userid,
        "formid": formid,
        "datalist": [
                    {
                        "columns": [
                            "Account Type",
                            "Account SubType",
                            "Project Name",
                            "Customer Name"
                        ],
                        "rows": [
                            "Revenue",
                            "Base Revenue",
                            "Delta",
                            "Customer 2"
                        ],
                        "changeValue": "100000",
                        "amount_type": 0,
                        "date": 202307
                    }
                ],
                "scenarioid": scenarioid,
                "date": 2023
            }
        }

    response = client.post(
        reverse("update-value"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()
    assert response.status_code == 200
    assert body["data"] == 4

    create_payload = {
    "data": {
        "datalist": [
                    {
                        "columns": [
                            "Account Type",
                            "Account SubType",
                            "Project Name",
                            "Customer Name"
                        ],
                        "rows": [
                            "Revenue",
                            "Base Revenue",
                            "Delta",
                            "Customer 2"
                        ],
                        "changeValue": "100000",
                        "amount_type": 0,
                        "date": 202307
                    }
                ],
                "scenarioid": scenarioid,
                "date": 2023
            }
        }

    response = client.post(
        reverse("update-value"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()
    assert response.status_code == 500
    print(body)
    assert body["error"] == True
    assert body["error_message"] == "'userid'"


@patch("finance.database.get_data.Session")
def test_update_amounttype(mock_session, client: APIClient):
    '''test_update_value _summary_

    Args:
        mock_session (_type_): _description_
        mock_update_value (_type_): _description_
        client (APIClient): _description_
    '''

    mock_session_instance = MagicMock()
    mock_session_instance.query.return_value.filter.return_value.update.return_value = 1
    mock_session.return_value = mock_session_instance

    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
            "data": {
                "userid": userid,
                "scenarioid": scenarioid,
                "date": 202307,
                "amount_type": 1
            }
        }
    response = client.post(
        reverse("update-actual"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()
    assert response.status_code == 200
    assert body["data"] == 1

@patch("finance.database.get_data.Session")
def test_delete_scnario(mock_session, client: APIClient):
    '''test_update_value _summary_

    Args:
        mock_session (_type_): _description_
        mock_update_value (_type_): _description_
        client (APIClient): _description_
    '''

    mock_session_instance = MagicMock()
    mock_session_instance.query.return_value.filter.return_value.update.side_effect = [1, 2]
    mock_session.return_value = mock_session_instance

    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
            "data": {
                "userid": userid,
                "scenarioid": scenarioid,
                "formid": formid,
                "status": True
            }
        }
    response = client.delete(
        reverse("create-scenario"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()
    assert response.status_code == 200
    assert body["data"] == 1


@patch("finance.database.get_data.Session")
def test_save_scenario(mock_session, client: APIClient):
    '''test_update_value _summary_

    Args:
        mock_session (_type_): _description_
        mock_update_value (_type_): _description_
        client (APIClient): _description_
    '''

    mock_session_instance = MagicMock()
    mock_session_instance.query.return_value.filter.return_value.update.return_value = 1
    mock_session.return_value = mock_session_instance

    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
            "data": {
                "scenarioid": scenarioid,
                "formid": formid,
                "userid": userid
            }
        }
    response = client.post(
        reverse("save-scenario"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()
    assert response.status_code == 200
    assert body["data"] == 1

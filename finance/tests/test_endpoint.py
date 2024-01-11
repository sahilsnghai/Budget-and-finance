import pytest
import secrets
from rest_framework.test import APIClient
from django.urls import reverse
from .cases.cases import get_header, userid, scenarioid, formid, organizationId, email


@pytest.fixture
def client():
    return APIClient()


def test_form_status(client):
    """Change Form Status

    Args:
        client (APIClient): for request and response
    """
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


def CRUD_scenario(client):
    """
    test_create_save_scenario

    Args:
        client (APIClient): for request and response
    """

    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
        "data": {
            "scenario_name": f"scenario_name{secrets.token_urlsafe(7)[:7]}",
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
    assert type(body["data"]) == dict
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
    body = response.json()

    assert response.status_code == 200
    assert response.json()["data"] == 1

    create_payload = {
        "data": {
            "scenario_name": "TEST",
            "scenario_decription": "TEST",
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

    assert response.status_code == 500
    assert response.json()["error_message"] == "Scenario already exits"

    delete_payload = {
            "data": {
                "userid": userid,
                "scenarioid": scenarioid,
                "formid": formid,
                "status": False
            }
        }
    response = client.delete(
        reverse("create-form"),
        headers=headers,
        data=delete_payload,
    )
    body = response.json()

    print(body)

    assert response.status_code == 200
    assert response.json()["data"] == 1


def test_filter_form(client):
    """fetch filter form

    Args:
        client (APIClient): for request and response
    """
    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
            "data":{
                "userid":userid,
                "organizationId":organizationId
            }
        }
    response = client.post(
        reverse("filter-form"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()

    assert response.status_code == 200
    assert len(body["data"]) != 0

def test_filter_scenario(client):
    """fetch filter form

    Args:
        client (APIClient): for request and response
    """
    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
            "data":{
                "userid":userid,
                "formid":formid,
                "organizationId":organizationId

            }
        }
    response = client.post(
        reverse("filter-scenario"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()

    assert response.status_code == 200
    assert len(body["data"]) != 0

def test_get_data(client):
    """fetch filter form

    Args:
        client (APIClient): for request and response
    """
    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
            "data":{
                "userid":userid,
                "formid":formid
            }
        }
    response = client.post(
        reverse("get-data"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()

    assert response.status_code == 200
    assert len(body["data"]) != 0

def test_filter_column(client):
    """fetch filter form

    Args:
        client (APIClient): for request and response
    """
    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
            "data": {
                "userid": userid,
                "formid": formid,
                "scenarioid": scenarioid,
                "year": 2023,
                "unit":"Business Unit 3"
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

def test_get_scenario(client):
    """fetch filter form

    Args:
        client (APIClient): for request and response
    """
    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
            "data":{
                "userid":userid,
                "scenarioid":scenarioid,
                "formid":formid
            }
        }
    response = client.post(
        reverse("get-scenario"),
        headers=headers,
        data=create_payload,
    )
    body = response.json()

    assert response.status_code == 200
    assert len(body["data"]) != 0

def test_update_scenario(client):
    """fetch filter form

    Args:
        client (APIClient): for request and response
    """
    headers = get_header(user_id=userid, org_id=organizationId, email=email)
    create_payload = {
            "data": {
                "userid": userid,
                "formid": formid,
                "datalist": [
                    {
                        "columns": [
                            "Account Type"
                        ],
                        "rows": [
                            "COGS"
                        ],
                        "changePrecentage": 75
                    }
                ],
                "scenarioid": scenarioid,
                "date": 2022
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
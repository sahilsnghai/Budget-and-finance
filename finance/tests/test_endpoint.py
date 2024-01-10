from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoproject.djangoproject.settings")
import django
django.setup()

client = APIClient()
userid = 10910
orgid = 247
email = 'ssjain@lumenore.com'
formid = 18
Status = True
scenarioid = 7


class CreateFrom(APITestCase):
    def test_create_form(self):
        req = {
            "data":{
                'userid': userid,
                'formid': formid,
                'status': Status,
                'scenarioid': scenarioid
            }
        }
        response = client.put(
                '/finance/create-form', data = req
            )
        print(response.status_code)
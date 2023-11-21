
"""constants.py File"""

import json
from os import path
from os.path import dirname, abspath


class ConstantsMeta(type):
    """update this doc string"""
    _instance = None

    def __call__(self):
        if self._instance is None:
            self._instance = super().__call__()
        return self._instance


class Constants(metaclass=ConstantsMeta):
    """update this doc string"""

    def __init__(self):

        self.time_zone = 'US/Eastern'  # timezone for date formatting
        self.STATUS200 = {'version': {'pointer': "2.0", "name": "AskMe Engine"},
                          "status": {"code": None, "value": None},
                          "data": None, 'error': None}
        self.ROOT_DIR = dirname(dirname(abspath(__file__)))
        self.HEADERS = {'content-type': "application/json", 'cache-control': "no-cache", 'version': None}

    # def get_conn_info(self, org=None):
    #     """

    #     Parameters
    #     ----------
    #     org

    #     Returns
    #     -------

    #     """
    #     return {
    #         "host": self.get_config(org=org, key="host"),
    #         "port": self.get_config(org=org, key="port"),
    #         "user": self.get_config(org=org, key="userName"),
    #         "password": self.get_config(org=org, key="password"),
    #         "database": self.get_config(org=org, key="schema"),
    #         "driver": self.get_config(org=org, key="driver")
    #     }

    # def get_config(self, org, key):
    #     """

    #     Parameters
    #     ----------
    #     org
    #     key

    #     Returns
    #     -------

    #     """
    #     json_filename = self.ROOT_DIR + "/configuration/configuration.json"
    #     if not path.exists(json_filename):
    #         json_filename = self.ROOT_DIR + "/configuration/askme-config-map-rsh"
    #     with open(json_filename, "r") as f:
    #         try:
    #             if org == "parameters":
    #                 return json.load(f)["parameters"][key]
    #             else:
    #                 return json.load(f)["dataSources"][org][key]

    #         except KeyError:
    #             return None

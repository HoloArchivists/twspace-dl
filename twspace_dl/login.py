"Module providing login utilities for twspace_dl"
import re

import requests


def load_from_file(filename: str) -> str:
    """return auth_token from netscape cookie file"""
    try:
        token = re.findall(
            r"(?<=auth_token\s)\w{40}", open(filename, "r", encoding="utf-8").read()
        )[0]
    except IndexError as err:
        raise ValueError(
            (
                "Cookie file does not have auth_token.\n"
                "Please check if you were connected when creating it"
            )
        ) from err
    return token


def write_to_file(auth_token: str, filename: str) -> None:
    """Write cookie to file in a format recognizable by the module
    (`auth_token        {auth_token}`)"""
    with open(filename, "w", encoding="utf-8") as cookie_file:
        cookie_file.write("auth_token" + 8 * " " + auth_token)


class Login:
    def __init__(self, username, password, guest_token):
        self.username = username
        self.password = password
        self.guest_token = guest_token
        self.session = requests.Session()
        self.task_url = "https://twitter.com/i/api/1.1/onboarding/task.json"
        self.flow_token: str

    def login(self) -> str:
        request_flow = self.session.post(
            self.task_url,
            params={"flow_name": "login"},
            headers=self._headers,
            json=self._initial_params,
        )
        try:
            self.flow_token = request_flow.json()["flow_token"]
        except KeyError as err:
            raise RuntimeError(
                "Error while initiating parameters:", request_flow.json()
            ) from err

        # js instrumentation subtask
        request_flow = self.session.post(
            self.task_url, headers=self._headers, json=self._js_instrumentation_data
        )
        try:
            self.flow_token = request_flow.json()["flow_token"]
        except KeyError as err:
            raise RuntimeError(
                "Error while performing js instrumentation:", request_flow.json()
            ) from err

        # user identifier sso subtask
        request_flow = self.session.post(
            self.task_url, headers=self._headers, json=self._user_identifier_sso_data
        )
        try:
            self.flow_token = request_flow.json()["flow_token"]
        except KeyError as err:
            raise RuntimeError("Error identifying user:", request_flow.json()) from err

        # account duplication check
        request_flow = self.session.post(
            self.task_url, headers=self._headers, json=self._account_dup_check_data
        )
        try:
            self.flow_token = request_flow.json()["flow_token"]
        except KeyError as err:
            raise RuntimeError(
                "Error while checking account duplication:", request_flow.json()
            ) from err

        # enter password
        request_flow = self.session.post(
            self.task_url, headers=self._headers, json=self._enter_password_data
        )
        try:
            auth_token = str(request_flow.cookies["auth_token"])
        except KeyError as err:
            raise RuntimeError(
                "Error while while entering password:", request_flow.json()
            ) from err

        return auth_token

    @property
    def _headers(self):
        return {
            "authorization": (
                "Bearer "
                "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
                "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
            ),
            "x-guest-token": self.guest_token,
        }

    @property
    def _js_instrumentation_data(self) -> dict:
        return {
            "flow_token": self.flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "LoginJsInstrumentationSubtask",
                    "js_instrumentation": {
                        "response": (
                            '{"rf":{"a976808c0d7d2c9a6081e997a1114f952a'
                            'f0067dcb59267ac8d852ec0ef98fe6":-65,"a1442a'
                            "8ec6ecb5804b8f60864cc54ded1bc140c4adaef6ac8"
                            '642d181ba17e0fd":1,"a3d158c7a0003247a36ff48'
                            '60f096c8eeefb23608d983162f94344db0b0a1f84":-10'
                            ',"a8031adb0e4372374f15125f9a10e5b8017743895f49'
                            '5b43c1aa74839c9a5876":15},"s":"HrR8ThECGdeQ4Ug'
                            "aWLIMSqGx0fL_7FOf7KjX8tlWN6WBN6HVcojL3if3rN"
                            "bYDtDhDmwK1jxMViInpjc1hc-kOO5w6Ej7WxoqdmI0eTVj-"
                            "5iul5FMdGaGZUVuWtkq3A7A42Y5RAsgNwYtpVB44XifZ3W1f"
                            "MscefI8HovjFtWUm0caZkF6_Y_1iFr0FSWHgM95gx0pXkK"
                            "910VlKn0HqT8Dvo6ss7LMA5Cf-VS84q284Vsx6h3nqwT"
                            "gzo4Nx3V4d86VL45GqIzqbwKT0OMlM6DHKk2Pi8WxKZ"
                            "_QoHAMQI0AzBCJ6McdfjGf7lCjtLLRb4ClfZNTW0g"
                            'IX3dMSEj03mvOkgAAAX4abfqW"}'
                        ),
                        "link": "next_link",
                    },
                }
            ],
        }

    @property
    def _user_identifier_sso_data(self) -> dict:
        # assert self.flow_token[-1] == "1"
        return {
            "flow_token": self.flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "LoginEnterUserIdentifierSSOSubtask",
                    "settings_list": {
                        "setting_responses": [
                            {
                                "key": "user_identifier",
                                "response_data": {
                                    "text_data": {"result": self.username}
                                },
                            }
                        ],
                        "link": "next_link",
                    },
                }
            ],
        }

    @property
    def _account_dup_check_data(self) -> dict:
        # assert self.flow_token[-1] == "2"
        return {
            "flow_token": self.flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "AccountDuplicationCheck",
                    "check_logged_in_account": {
                        "link": "AccountDuplicationCheck_false"
                    },
                }
            ],
        }

    @property
    def _enter_password_data(self) -> dict:
        # assert self.flow_token[-1] == "6"
        return {
            "flow_token": self.flow_token,
            "subtask_inputs": [
                {
                    "subtask_id": "LoginEnterPassword",
                    "enter_password": {"password": self.password, "link": "next_link"},
                }
            ],
        }

    @property
    def _initial_params(self) -> dict:
        return {
            "input_flow_data": {
                "flow_context": {
                    "debug_overrides": {},
                    "start_location": {"location": "splash_screen"},
                }
            },
            "subtask_versions": {
                "contacts_live_sync_permission_prompt": 0,
                "email_verification": 1,
                "topics_selector": 1,
                "wait_spinner": 1,
                "cta": 4,
            },
        }

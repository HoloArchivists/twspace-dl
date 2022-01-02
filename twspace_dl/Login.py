import requests

class Login:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.guest_token = None
        self.flow_token = None
        self.auth_token = None
        self.task_url = "https://twitter.com/i/api/1.1/onboarding/task.json"
        
    def set_token(self, guest_token):
        self.guest_token = guest_token

    def get_token(self) -> str:
        return self.auth_token

    def login(self) -> str:
        if self.auth_token:
            return self.auth_token
        # Just do simple post request to get the auth token
        r = self.session.post(self.task_url + "?flow_name=login",
            headers = self.get_headers(),
            json = self.get_initial_params()
        )
        try:
            self.flow_token = r.json()["flow_token"]
        except:
            print("Error while intiial_params:", r.json())
            return None
        
        # Task 0
        r = self.session.post(self.task_url,
            headers = self.get_headers(),
            json = self.get_task0_data()
        )
        try:
            self.flow_token = r.json()["flow_token"]
        except:
            print("Error while task0:", r.json())
            return None
        
        # Task 1
        r = self.session.post(self.task_url,
            headers = self.get_headers(),
            json = self.get_task1_data()
        )
        try:
            self.flow_token = r.json()["flow_token"]
        except:
            print("Error while task1:", r.json())
            return None

        # Task 2
        r = self.session.post(self.task_url,
            headers = self.get_headers(),
            json = self.get_task2_data()
        )
        try:
            self.flow_token = r.json()["flow_token"]
        except:
            print("Error while task2:", r.json())
            return None

        # Task 6
        r = self.session.post(self.task_url,
            headers = self.get_headers(),
            json = self.get_task6_data()
        )
        try:
            self.auth_token = str(r.cookies["auth_token"])
        except:
            print("Error while task6:", r.json())
            return None
        return self.auth_token
    
    def get_headers(self):
        return {
            "authorization": (
                "Bearer "
                "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
                "=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
            ),
            "x-guest-token": self.guest_token,
        }

    def get_task0_data(self) -> dict:
        return {
            "flow_token": self.flow_token,
            "subtask_inputs":[
                {
                    "subtask_id":"LoginJsInstrumentationSubtask",
                    "js_instrumentation":{
                        "response":"{\"rf\":{\"a976808c0d7d2c9a6081e997a1114f952af0067dcb59267ac8d852ec0ef98fe6\":-65,\"a1442a8ec6ecb5804b8f60864cc54ded1bc140c4adaef6ac8642d181ba17e0fd\":1,\"a3d158c7a0003247a36ff4860f096c8eeefb23608d983162f94344db0b0a1f84\":-10,\"a8031adb0e4372374f15125f9a10e5b8017743895f495b43c1aa74839c9a5876\":15},\"s\":\"HrR8ThECGdeQ4UgaWLIMSqGx0fL_7FOf7KjX8tlWN6WBN6HVcojL3if3rNbYDtDhDmwK1jxMViInpjc1hc-kOO5w6Ej7WxoqdmI0eTVj-5iul5FMdGaGZUVuWtkq3A7A42Y5RAsgNwYtpVB44XifZ3W1fMscefI8HovjFtWUm0caZkF6_Y_1iFr0FSWHgM95gx0pXkK910VlKn0HqT8Dvo6ss7LMA5Cf-VS84q284Vsx6h3nqwTgzo4Nx3V4d86VL45GqIzqbwKT0OMlM6DHKk2Pi8WxKZ_QoHAMQI0AzBCJ6McdfjGf7lCjtLLRb4ClfZNTW0gIX3dMSEj03mvOkgAAAX4abfqW\"}",
                        "link":"next_link"
                    }
            }
        ]}
    def get_task1_data(self) -> dict:
        # assert self.flow_token[-1] == "1"
        return {
            "flow_token": self.flow_token,
            "subtask_inputs":[{
                "subtask_id":"LoginEnterUserIdentifierSSOSubtask",
                "settings_list":{
                    "setting_responses":[{
                        "key":"user_identifier",
                        "response_data":{
                            "text_data":{
                                "result": self.username
                            }
                        }
                    }
                ],
                "link":"next_link"
                }
            }]
        }

    def get_task2_data(self) -> dict:
        # assert self.flow_token[-1] == "2"
        return {
            "flow_token": self.flow_token,
            "subtask_inputs":[
                {
                    "subtask_id":"AccountDuplicationCheck",
                    "check_logged_in_account":{
                        "link":"AccountDuplicationCheck_false"
                    }
                }
            ]
        }

    def get_task6_data(self) -> dict:
        # assert self.flow_token[-1] == "6"
        return {
            "flow_token": self.flow_token,
            "subtask_inputs":[{
                "subtask_id":"LoginEnterPassword",
                "enter_password":{
                    "password": self.password,
                    "link":"next_link"
                }
            }]
        }

    def get_initial_params(self) -> dict:
        return {
            "input_flow_data":{
                "flow_context":{
                    "debug_overrides":{
                        
                    },
                    "start_location":{
                        "location":"splash_screen"
                    }
                }
            },
            "subtask_versions":{
                "contacts_live_sync_permission_prompt":0,
                "email_verification":1,
                "topics_selector":1,
                "wait_spinner":1,
                "cta":4
            }
        }


if __name__ == "__main__":
    from TwspaceDL import TwspaceDL
    username = input("Username: ")
    password = input("Password: ")

    t = Login(username, password)
    t.set_token(TwspaceDL.guest_token())
    t.login()
    print(t.get_token())
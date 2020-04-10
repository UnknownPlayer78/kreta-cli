import json
import requests as http
from .utils import log


class Route:
    ENDPOINTS = {
        "token": "/idp/api/v1/Token",
        "user_data": "/mapi/api/v1/StudentAmi",
        "tests": "/mapi/api/v1/BejelentettSzamonkeresAmi",
        "messages": "/integration-kretamobile-api/v1/kommunikacio/postaladaelemek/",
        "lessons": "/mapi/api/v1/LessonAmi",
        "events": "/mapi/api/v1/EventAmi",
        "homeworks_user": "/mapi/api/v1/HaziFeladat/TanuloHaziFeladatLista/",
        "homeworks_teacher": "/mapi/api/v1/HaziFeladat/TanarHaziFeladat/",
    }

    def __init__(self, institute_code):
        self.base = f"https://{institute_code}.e-kreta.hu"
        self.base2 = "https://eugyintezes.e-kreta.hu"

    @property
    def token(self):
        return self.base + self.ENDPOINTS["token"]

    @property
    def user_data(self):
        return self.base + self.ENDPOINTS["user_data"]

    @property
    def tests(self):
        return self.base + self.ENDPOINTS["tests"]

    @property
    def messages(self):
        return self.base2 + self.ENDPOINTS["messages"]

    @property
    def lessons(self):
        return self.base + self.ENDPOINTS["lessons"]

    @property
    def events(self):
        return self.base + self.ENDPOINTS["events"]

    @property
    def homeworks_user(self):
        return self.base + self.ENDPOINTS["homeworks_user"]

    @property
    def homeworks_teacher(self):
        return self.base + self.ENDPOINTS["homeworks_teacher"]


class API:
    client_id = "919e0c1c-76a2-4646-a2fb-7085bbbf3c56"

    def __init__(self, config):
        self.config = config
        if "institute_code" in config.keys():
            self.institute_code = config["institute_code"]
        else:
            self.institute_code = ""

        if "user_agent" in config.keys():
            self.user_agent = config["user_agent"]
        else:
            self.user_agent = ""

        if "auth_token" in config.keys():
            self.auth_token = config["auth_token"]
        else:
            self.auth_token = ""

        self.route = Route(self.institute_code)
        self.headers = {'Accept': 'application/json',
                        'User-Agent': self.user_agent}

    def auth(self):
        try:
            payload = f'institute_code={self.config["institute_code"]}&userName={self.config["username"]}' + \
                f'&grant_type=password&client_id={self.client_id}&password={self.config["password"]}'
        except Exception as e:
            log([{"text": "ERROR: ", "color": "red"}, {
                "text": f"{e} is not configured"}])
            exit(1)

        headers = self.headers
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        try:
            r = http.post(self.route.token, data=payload, headers=headers)
            access_token = r.json()['access_token']
        except Exception as error:
            log([{"text": "ERROR: ", "color": "red"}, {
                "text": "login error: " + str(error)}])
            try:
                log([{"text": "Server response: ", "color": "yellow"}, {"text": r.text}])
            except:
                pass
            exit(1)

        return access_token

    def auth_check(self, r):
        if r.text == "invalid_grant":
            log([{"text": "ERROR: ", "color": "red"},
                 {"text": "authentication faliure"}])
            exit(1)

    def get_user_data(self):
        headers = self.headers
        headers['Authorization'] = f'bearer {self.auth_token}'

        r = http.get(self.route.user_data, headers=headers)
        self.auth_check(r)

        return r.json()

    def get_tests(self):
        headers = self.headers
        headers['Authorization'] = f'bearer {self.auth_token}'

        r = http.get(self.route.tests, headers=headers)
        self.auth_check(r)

        return r.json()

    def get_messages(self):
        headers = self.headers
        headers['Authorization'] = f'bearer {self.auth_token}'

        r = http.get(self.route.messages + "sajat", headers=headers)
        self.auth_check(r)

        return r.json()

    def get_message(self, uid):
        headers = self.headers
        headers['Authorization'] = f'bearer {self.config["token"]}'

        r = http.get(self.route.messages + str(uid), headers=headers)
        self.auth_check(r)

        return r.json()

    def get_lessons(self, from_date, to_date):
        headers = self.headers
        headers['Authorization'] = f'bearer {self.auth_token}'

        timestamp = f"?fromDate={from_date[0]}-{from_date[1]}-{from_date[2]}" + \
            f"&toDate={to_date[0]}-{to_date[1]}-{to_date[2]}"

        r = http.get(self.route.lessons + timestamp, headers=headers)
        self.auth_check(r)

        return r.json()

    def get_homework(self, uid):
        headers = self.headers
        headers['Authorization'] = f'bearer {self.auth_token}'

        r = http.get(self.route.homeworks_user + str(uid), headers=headers)
        self.auth_check(r)
        homeworks = r.json()

        r = http.get(self.route.homeworks_teacher + str(uid), headers=headers)
        self.auth_check(r)
        homeworks.append(r.json())

        return homeworks

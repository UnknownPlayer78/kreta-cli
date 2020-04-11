import json
import requests as http
from .utils import log


class Route:
    ENDPOINTS = {
        "token": "/idp/api/v1/Token",
        "user_data": "/mapi/api/v1/Student",
        "tests": "/mapi/api/v1/BejelentettSzamonkeres",
        "messages": "/integration-kretamobile-api/v1/kommunikacio/postaladaelemek/",
        "lessons": "/mapi/api/v1/Lesson",
        "events": "/mapi/api/v1/EventAmi",
        "homeworks_user": "/mapi/api/v1/HaziFeladat/TanuloHaziFeladatLista/",
        "homeworks_teacher": "/mapi/api/v1/HaziFeladat/TanarHaziFeladat/",
        "averages": "/mapi/api/v1/TantargyiAtlagAmi"
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

    @property
    def averages(self):
        return self.base + self.ENDPOINTS["averages"]


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
            log([{"text": "ERROR: ", "color": "red"},
                 {"text": f"{e} is not configured"}])
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
                 {"text": "authentication faliure (try to login again)"}])
            exit(1)

    def get_api(self, endpoint, args="", ami=False):
        headers = self.headers
        headers['Authorization'] = f'bearer {self.auth_token}'

        if ami:
            api = "Ami"
        else:
            api = ""

        try:
            r = http.get(endpoint + api + str(args), headers=headers)
        except UnicodeError:
            log([{"text": "ERROR: ", "color": "red"}, {
                "text": "'institute_code' is not configured"}])
            exit(1)
        except http.exceptions.ConnectionError:
            log([{"text": "ERROR: ", "color": "red"}, {
                "text": "could not connect to " + self.institute_code + ".e-kreta.hu"}])
            exit(1)

        self.auth_check(r)

        return r

    def get_user_data(self, ami=True):
        return self.get_api(self.route.user_data, ami=ami).json()

    def get_tests(self, ami=True):
        return self.get_api(self.route.tests, ami=ami).json()

    def get_messages(self):
        return self.get_api(self.route.messages, args="sajat").json()

    def get_message(self, uid):
        return self.get_api(self.route.messages, args=uid).json()

    def get_lessons(self, from_date, to_date, ami=True):
        timestamp = f"?fromDate={from_date[0]}-{from_date[1]}-{from_date[2]}" + \
            f"&toDate={to_date[0]}-{to_date[1]}-{to_date[2]}"

        return self.get_api(self.route.lessons, args=timestamp, ami=ami).json()

    def get_homework(self, uid):
        homeworks = self.get_api(self.route.homeworks_user, args=uid).json()
        homeworks.append(self.get_api(
            self.route.homeworks_teacher, args=uid).json())

        return homeworks

    def get_averages(self):
        return self.get_api(self.route.averages).json()

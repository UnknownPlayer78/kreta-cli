import json
from kreta import api
from .utils import log, format_date, format_time, parse_html
import time
import math
import datetime
import os
import sys
import pathlib
HOME = pathlib.Path().home()


class Kreta:
    def __init__(self):
        self.config = self.load_config()
        self.api = api.API(self.config)

    def config_file(self, mode="r"):
        if sys.platform == "linux":
            conf_path = f"{HOME}/.config/kreta"
        elif sys.platform == "win32":
            conf_path = f"{HOME}/appdata/local/kreta"

        else:
            log([{"text": "ERROR: ", "color": "red"}, {
                "text": "unsupported platform: " + sys.platform}])
            sys.exit(1)

        try:
            conf = open(f"{conf_path}/config.json", mode=mode)
        except FileNotFoundError:
            try:
                os.mkdir(conf_path)
            except FileExistsError:
                pass

        return conf

    def load_config(self):
        try:
            f = self.config_file()
        except:
            self.config = {}
            self.save_config()
            return self.config
        else:
            conf = f.read()
            f.close()

            try:
                conf = json.loads(conf)
            except:
                conf = {}

            return conf

    def save_config(self):
        conf = self.config
        conf = json.dumps(conf)

        f = self.config_file("w")
        f.write(conf)
        f.close()

    def set_config(self, key, value, silent=False):
        self.config = self.load_config()
        self.config[key] = value

        if not silent:
            log([{"text": f'"{key}"', "bold": True}, {
                "text": " set to "}, {"text": f'"{value}"', "bold": True}])

        self.save_config()

    def login(self):
        auth_token = self.api.auth()
        self.set_config("auth_token", auth_token, silent=True)
        log({"text": "Logged in successfully", "color": "green"})

    def get_user_data(self):
        user = self.api.get_user_data()

        log([{"text": "Name:\t\t", "bold": True}, {"text": user['Name']}])
        log([{"text": "Adresses:\t", "bold": True},
             {"text": ",\n\t\t".join(user['AddressDataList'])}])
        log([{"text": "Parents: ", "bold": True}, {"text": "\tMother: " +
                                                   user['MothersName'] + "\n\t\tFather: " + user['Tutelaries'][0]['Name']}])
        log([{"text": "Birth:\t\t", "bold": True}, {
            "text": user['PlaceOfBirth'] + " " + format_date(user['DateOfBirthUtc'])}])
        log([{"text": "School:\t\t", "bold": True},
             {"text": user['InstituteName']}])
        log([{"text": "Class:\t\t", "bold": True}, {
            "text": user['Osztalyfonokok'][0]["Osztalyai"][0]['Nev']}])

    def ping(self):
        start = time.time()
        self.api.auth()
        took = round((time.time() - start) * 1000)

        log({
            "text": f'Reply from {self.config["institute_code"]}.e-kreta.hu took: {took}ms'})

    def show(self, type_, page, show_all):
        if type_ == "grades":
            self.print_grades(page=page, show_all=show_all)
        elif type_ == "notes":
            self.print_notes(page=page, show_all=show_all)
        elif type_ == "absences":
            self.print_absences(page=page, show_all=show_all)
        elif type_ == "tests":
            self.print_tests(page=page, show_all=show_all)
        elif type_ == "messages":
            self.print_messages(page=page, show_all=show_all)
        elif type_ == "homeworks":
            self.print_homeworks(page=page, show_all=show_all)

    def show_message(self, message_id):
        message = self.api.get_message(message_id)
        print(parse_html(message["uzenet"]["szoveg"]))

    def print_messages(self, page=1, show_all=False):
        messages = self.api.get_messages()

        if not show_all:
            pages = math.ceil(len(messages) / 10)

            start = (int(page) - 1) * 10
            end = start + 10

            messages.reverse()
            messages = messages[start:end]
            messages.reverse()

        log([{"text": "Date", "bold": True}, {"text": "ID", "bold": True}, {"text": "Author", "bold": True}, {"text": "Subject", "bold": True}],
            table=True, table_template="{:<24}{:<19}{:<31}{}")

        for message in messages:
            uid = message["azonosito"]
            message = message["uzenet"]
            date = format_date(message["kuldesDatum"])
            author = message["feladoNev"]
            subject = message['targy']

            log([{"text": f"[{date}] "}, {"text": str(uid)+" ", "color": "cyan"}, {"text": author+" ", "color": "yellow"}, {"text": subject, "dark": "True"}],
                table=True, table_template="{}{:<20}{:<32}{}")

        if not show_all:
            log({"text": f"Showing page: {page}/{pages}", "dark": True})

    def print_tests(self, page=1, show_all=False):
        tests = self.api.get_tests()

        if not show_all:
            pages = math.ceil(len(tests) / 10)

            start = (int(page) - 1) * 10
            end = start + 10

            tests = tests[start:end]

        tests.reverse()

        log([{"text": "Date", "bold": True}, {"text": "Subject", "bold": True},
             {"text": "Teacher", "bold": True}, {"text": "Title", "bold": True}],
            table=True, table_template="{:<24}{:<31}{:<31}{}")

        for test in tests:
            date = format_date(test["Datum"])
            subject = test["Tantargy"]
            teacher = test["Tanar"]
            title = test["SzamonkeresMegnevezese"]
            #mode = test["SzamonkeresModja"]

            log([{"text": f"[{date}] ", "color": "white"}, {"text": subject+" ", "color": "blue"},
                 {"text": teacher+" ", "color": "yellow"}, {"text": title, "dark": True}],
                table=True, table_template="{}{:<32}{:<32}{}")

        if not show_all:
            log({"text": f"Showing page: {page}/{pages}", "dark": True})

    def print_absences(self, page=1, show_all=False):
        data = self.api.get_user_data()
        absences = data["Absences"]

        if not show_all:
            pages = math.ceil(len(absences) / 10)

            start = (int(page) - 1) * 10
            end = start + 10

            absences.reverse()
            absences = absences[start:end]
            absences.reverse()

        date_before = ""

        log([{"text": ""}, {"text": "  Subject", "bold": True}, {"text": "Teacher", "bold": True},
             {"text": "Type", "bold": True}, {"text": "Amount", "bold": True}],
            table=True, table_template="{}{:<33}{:<31}{:<17}{}")

        for absence in absences:
            if absence["JustificationState"] == "Justified":
                state = "✔️ "
                state_color = "green"
            else:
                state = "❌"
                state_color = "red"

            if absence["SubjectCategoryName"] != "Na":
                subject = absence["SubjectCategoryName"].split(",")[0]
            else:
                subject = absence["Subject"]

            if absence["DelayTimeMinutes"] > 0:
                minutes = str(absence["DelayTimeMinutes"]) + " perc"
            else:
                minutes = ""

            teacher = absence["Teacher"]
            type_name = absence["TypeName"]
            date = format_date(absence["CreatingTime"])

            if date != date_before:
                if not date_before == "":
                    print()

                log({"text": f"[{date}] ", "color": "white"})

            date_before = date

            log([{"text": state, "color": state_color}, {"text": subject+" ", "color": "blue"},
                 {"text": teacher + " ", "color": "yellow"}, {"text": type_name+" ", "dark": True}, {"text": minutes, "color": "magenta"}, ],
                table=True, table_template="{}{:<32}{:<32}{:<17}{}")

        if not show_all:
            log({"text": f"Showing page: {page}/{pages}", "dark": True})

    def show_note(self, note_id):
        data = self.api.get_user_data()
        notes = data["Notes"]

        for note in notes:
            if note["NoteId"] == note_id:
                print(note["Content"])
                return

        print("Note not found")

    def print_notes(self, page=1, show_all=False):
        data = self.api.get_user_data()
        notes = data["Notes"]

        if not show_all:
            pages = math.ceil(len(notes) / 10)

            start = (int(page) - 1) * 10
            end = start + 10

            notes = notes[start:end]

        notes.reverse()

        log([{"text": "Date", "bold": True}, {"text": "ID", "bold": True}, {"text": "Teacher", "bold": True}, {"text": "Title", "bold": True}],
            table=True, table_template="{:<24}{:<19}{:<31}{}")

        for note in notes:
            uid = note["NoteId"]
            date = format_date(note["Date"])
            teacher = note["Teacher"]
            title = note["Title"]
            #content = note["Content"]

            log([{"text": f'[{date}] ', "color": "white"}, {"text": str(uid)+" ", "color": "cyan"}, {"text": teacher+" ", "color": "yellow"}, {"text": title, "dark": True}],
                table=True, table_template="{:<24}{:<20}{:<32}{}")

        if not show_all:
            log({"text": f"Showing page: {page}/{pages}", "dark": True})

    def print_grades(self, page=1, show_all=False):
        data = self.api.get_user_data()
        grades = data["Evaluations"]

        if not show_all:
            pages = math.ceil(len(grades) / 10)

            start = (int(page) - 1) * 10
            end = start + 10
            grades = grades[start:end]

        grades.reverse()

        log([{"text": "Date", "bold": True}, {"text": "Value", "bold": True}, {"text": "Subject", "bold": True},
             {"text": "Teacher", "bold": True}, {"text": "Description", "bold": True}],
            table=True, table_template="{:<24}{:<17}{:<31}{:<31}{}")

        for grade in grades:
            if grade["SubjectCategoryName"] != "Na":
                subject = grade["SubjectCategoryName"]
            else:
                subject = grade["Subject"]

            if not grade["Subject"]:
                subject = grade["Jelleg"]["Leiras"]

            date = format_date(grade["Date"])
            if grade["NumberValue"] > 0:
                value = grade["NumberValue"]
            else:
                value = grade["Value"]

            teacher = grade["Teacher"]

            if grade["Weight"] != "100%" and grade["Weight"] != "-":
                weight = f'({grade["Weight"]}) '
            else:
                weight = ""

            if grade["Theme"]:
                desc = grade["Theme"].replace("  ", " ")
            else:
                desc = ""

            if grade["NumberValue"] > 0:
                log([{"text": "["+date+"] ", "color": "white"}, {"text": str(value)+" ", "color": "magenta", "bold": True}, {"text": weight, "color": "green"},
                     {"text": subject+" ", "color": "blue"}, {"text": teacher + " ", "color": "yellow"}, {"text": desc, "dark": True}],
                    table=True, table_template="{}{}{:<16}{:<32}{:<32}{}")
            else:
                log([{"text": "["+date+"] ", "color": "white"}, {"text": str(value)+" ", "color": "magenta", "bold": True}, {"text": subject+" ", "color": "blue"},
                     {"text": teacher + " ", "color": "yellow"}, {"text": desc, "dark": True}],
                    table=True, table_template="{}{:<22}{:<32}{:<32}{}")

        if not show_all:
            log({"text": f"Showing page: {page}/{pages}", "dark": True})

    def print_lessons(self, week=False, day=0):
        days = ["Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday", "Sunday"]

        if not week:
            try:
                today = int(datetime.datetime.now().strftime(
                    '%s')) + int(day) * 86400
            except ValueError:
                log([{"text": "ERROR: ", "color": "red"},
                     {"text": "invalid number"}])
                exit(1)

            today = datetime.datetime.fromtimestamp(today)
            today = [today.year, today.month, today.day]

            lessons = self.api.get_lessons(today, today)

            if len(lessons) != 0:
                log([{}, {"text": "    Subject", "bold": True}, {"text": "Room", "bold": True},
                     {"text": "Teacher", "bold": True}, {"text": "Description", "bold": True}],
                    table=True, table_template="{}{:<35}{:<19}{:<31}{}")

            for i, lesson in enumerate(lessons):
                template = "{:<8}{:<32}{:<20}{:<<t>}{}"

                date = format_date(lesson["Date"])
                weekday = days[datetime.datetime(
                    *[int(d) for d in lesson["Date"].split("T")[0].split("-")]).weekday()]
                teacher = lesson["Teacher"]
                teacher_ = False

                if lesson["DeputyTeacher"] != "":
                    teacher = lesson["DeputyTeacher"]
                    teacher_ = True
                    template = template.replace("<t>", "36")
                else:
                    template = template.replace("<t>", "32")

                room = lesson["ClassRoom"]
                description = lesson['Theme']

                if lesson["SubjectCategoryName"] != "Na":
                    subject = lesson["SubjectCategoryName"].split(",")[0]
                else:
                    subject = lesson["Subject"]

                log([{"text": f"{i+1}. "}, {"text": subject+" ", "color": "blue"}, {"text": str(room)+" ", "color": "magenta"},
                     {"text": teacher+" ", "color": "yellow", "dark": teacher_}, {"text": description, "dark": True}],
                    table=True, table_template=template)

            if len(lessons) == 0:
                if day == 0:
                    log({"text": "You don't have lessons today.", "color": "yellow"})
                else:
                    log({"text": "You don't have lessons on this day.", "color": "yellow"})
            else:
                log({"text": f"{date} {weekday}", "dark": True})

        else:
            today = datetime.datetime.now()
            start = int(today.strftime('%s')) - \
                (today.weekday() * 86400) + (day * 604800)
            end = start + 6 * 86400
            start = datetime.datetime.fromtimestamp(start)
            start = [start.year, start.month, start.day]
            end = datetime.datetime.fromtimestamp(end)
            end = [end.year, end.month, end.day]

            lessons = self.api.get_lessons(start, end)
            lesson_days = {}

            for lesson in lessons:
                date = lesson["Date"].split("T")[0]

                if not date in lesson_days:
                    lesson_days[date] = []
                lesson_days[date].append(lesson)

            max_lesson_len = 0

            for day in lesson_days.items():
                day = day[1]
                if len(day) > max_lesson_len:
                    max_lesson_len = len(day)

            day_names = [{}]
            for date in lesson_days.keys():
                day_names.append({"text": days[int(datetime.datetime(
                    *[int(d) for d in date.split("-")]).weekday())], "bold": True})

            template = "{:<4}" + "{:<31}" * len(lesson_days)
            log(day_names, table=True, table_template=template)
            template = "{:<8}" + "{:<32}" * len(lesson_days)

            for i in range(0, max_lesson_len):
                lessons = [{"text": f"{i+1}. "}]
                for date in lesson_days.keys():
                    day = lesson_days[date]

                    try:
                        lesson = day[i]
                    except:
                        lessons.append({"text": "", "color": "blue"})
                        continue

                    if lesson["SubjectCategoryName"] != "Na":
                        subject = lesson["SubjectCategoryName"].split(",")[0]
                    else:
                        subject = lesson["Subject"]

                    lessons.append({"text": subject+" ", "color": "blue"})

                log(lessons, table=True, table_template=template)

    def print_homeworks(self, page=1, show_all=False):
        today = datetime.datetime.now()
        end = int(today.strftime('%s'))
        start = end - (today.weekday() * 86400)
        start = datetime.datetime.fromtimestamp(start)
        start = [start.year, start.month, start.day]
        end = datetime.datetime.fromtimestamp(end)
        end = [end.year, end.month, end.day]

        lessons = self.api.get_lessons(start, end)

        log([{"text": "Date", "bold": True}, {"text": "ID", "bold": True}, {"text": "Subject", "bold": True},
             {"text": "Author", "bold": True}, {"text": "Deadline", "bold": True}],
            table=True, table_template="{:<24}{:<19}{:<31}{:<31}{}")

        for lesson in lessons:
            if lesson["TeacherHomeworkId"]:
                homeworks = self.api.get_homework(lesson["TeacherHomeworkId"])
                for homework in homeworks:
                    try:
                        author = homework["Rogzito"]
                        htype = "teacher"
                    except:
                        author = homework["TanuloNev"]
                        htype = "user"

                    if lesson["SubjectCategoryName"] != "Na":
                        subject = lesson["SubjectCategoryName"].split(",")[0]
                    else:
                        subject = lesson["Subject"]

                    uid = homework["Uid"]

                    if htype == "teacher":
                        date = format_date(homework["FeladasDatuma"])
                        deadline = format_date(homework["Hatarido"])

                        log([{"text": f"[{date}] "}, {"text": uid+" ", "color": "cyan"}, {"text": subject+" ", "color": "blue"},
                             {"text": author+" ", "color": "yellow"}, {"text": deadline, "dark": True}],
                            table=True, table_template="{}{:<20}{:<32}{:<32}{}")
                    else:
                        date = format_date(homework["FeladasDatuma"])
                        if homework["TanuloAltalTorolt"] or homework["TanarAltalTorolt"]:
                            deleted = "[deleted]"
                        else:
                            deleted = ""

                        log([{"text": f"[{date}] "}, {"text": uid+" ", "color": "cyan"}, {"text": subject+" ", "color": "blue"},
                             {"text": author+" ", "color": "yellow"}, {"text": deleted, "color": "red"}],
                            table=True, table_template="{}{}{}{}{}")

    def show_homework(self, hwid):
        today = datetime.datetime.now()
        end = int(today.strftime('%s'))
        start = end - (today.weekday() * 86400)
        start = datetime.datetime.fromtimestamp(start)
        start = [start.year, start.month, start.day]
        end = datetime.datetime.fromtimestamp(end)
        end = [end.year, end.month, end.day]

        lessons = self.api.get_lessons(start, end)

        for lesson in lessons:
            if lesson["TeacherHomeworkId"]:
                homeworks = self.api.get_homework(lesson["TeacherHomeworkId"])
                for homework in homeworks:
                    if homework["Uid"] == str(hwid):
                        try:
                            print(parse_html(homework["Szoveg"]))
                        except:
                            print(parse_html(homework["FeladatSzovege"]))

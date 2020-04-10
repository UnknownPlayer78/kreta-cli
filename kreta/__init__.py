import sys
from .core import Kreta
from .utils import splash, log


__version__ = "0.0.9"
__help__ = """\
usage: kreta [--version] [--help] <command>

KRÉTA Ellenőrző CLI

General:
  usage: kreta login                    log in to kréta
         kreta ping                     show latency to kreta servers

  Options:
    -h, --help                          show this help message and exit
    -v, --version                       show the current local version of kreta-cli
  
Config:
  usage: kreta config [options]         configure kreta-cli settings

  Options:
    -i, --institute [INSTITUTE ...]     configure institute code
    -u, --user [USERNAME ...]           configure username
    -p, --password [PASSWORD ...]       configure password
    -ua, --user-agent [USER-AGENT ...]  configure user-agent
    
Data:
  usage: kreta user                     show user information
         kreta averages                 show averages
         kreta messages                 show messages
         kreta show <id>                show message, homework or note content
         kreta homeworks                show homeworks from current week
         kreta timetable <day>          show timetable by day relative to today
         kreta notes                    show notes
         kreta tests                    show tests
         kreta absences                 show absences
         kreta grades                   show grades
         
  Options:
    -p, --page                          show page
    -a, --all                           show all entries
    
  Timetable Options:
    -w, --week                          show full week"""


def arg(*args, argv=[]):
    for arg in args:
        if arg in argv:
            return True

    return False


def main(argv):
    kreta = Kreta()

    if len(argv) == 1:
        splash()
        print(__help__)
        return

    if arg("-h", "--help", argv=argv):
        print(__help__)
        return

    if arg("-v", "--version", argv=argv):
        print("kreta-cli", __version__)
        return

    command = argv[1]

    if command == "login":
        kreta.login()

    elif command == "config":
        if len(argv) == 2:
            print(__help__)

        try:
            if arg("-i", argv=argv):
                value = argv[argv.index("-i") + 1]
                kreta.set_config("institute_code", value)

            if arg("--institute", argv=argv):
                value = argv[argv.index("--institute-code") + 1]
                kreta.set_config("institute_code", value)

            if arg("-u", argv=argv):
                value = argv[argv.index("-u") + 1]
                kreta.set_config("username", value)

            if arg("--username", argv=argv):
                value = argv[argv.index("--username") + 1]
                kreta.set_config("username", value)

            if arg("-p", argv=argv):
                value = argv[argv.index("-p") + 1]
                kreta.set_config("password", value)

            if arg("--password", argv=argv):
                value = argv[argv.index("--password") + 1]
                kreta.set_config("password", value)

            if arg("-ua", argv=argv):
                value = argv[argv.index("-ua") + 1]
                kreta.set_config("user_agent", value)

            if arg("--user-agent", argv=argv):
                value = argv[argv.index("--user-agent") + 1]
                kreta.set_config("user_agent", value)
        except IndexError:
            log([{"text": "ERROR: ", "color": "red"}, {"text": "missing value"}])
            exit(1)

    elif command == "user":
        kreta.get_user_data()

    elif command == "ping":
        kreta.ping()

    elif command in ["grades", "messages", "notes", "homeworks", "tests", "absences"]:
        if arg("-a", "--all", argv=argv):
            all_ = True
        else:
            all_ = False

        try:
            if arg("-p", argv=argv):
                page = argv[argv.index("-p") + 1]
            elif arg("--page", argv=argv):
                page = argv[argv.index("--page") + 1]
            else:
                page = 1
        except IndexError:
            log([{"text": "ERROR: ", "color": "red"}, {"text": "missing value"}])
            exit(1)

        kreta.show(command, page=page, show_all=all_)

    elif command == "show":
        uid = int(argv[2])

        if uid < 500000:
            kreta.show_homework(uid)
        elif uid < 1000000:
            kreta.show_note(uid)
        else:
            kreta.show_message(uid)

    elif command == "timetable":
        if arg("-w", "--week", argv=argv):
            try:
                day = int(argv[3])
            except IndexError:
                day = 0
            except ValueError:
                day = int(argv[2])

            kreta.print_lessons(week=True, day=day)
        else:
            try:
                day = argv[2]
            except:
                day = 0
            kreta.print_lessons(day=day)

    elif command == "averages":
        log([{"text": "ERROR: ", "color": "red"}, {"text": "not implemented"}])
        exit(0)

    else:
        log([{"text": "ERROR: ", "color": "red"}, {
            "text": f"unknown command: {command}"}])
        exit(1)


if __name__ == "__main__":
    main(sys.argv)

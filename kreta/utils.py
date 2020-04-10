import re

colors = {
    'grey': 30,
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37,
}

def format_text(text, color=None, bold=False, dark=False):
    if color:
        text = f'\033[{colors[color]}m' + text

    if bold:
        text = '\033[1m' + text

    if dark:
        text = '\033[2m' + text

    text += '\033[0m'

    return text


def format_date(date):
    return date.replace("-", ". ").split("T")[0] + "."

def format_time(time):
    return ":".join(time.split("T")[1].replace("Z", "").split(":")[:2])

def log(msg_obj, table=False, table_template=""):
    if not table:
        buffer = ""
    else:
        buffer = []

    if type(msg_obj) == dict:
        msg_obj = [msg_obj]

    for msg in msg_obj:
        if len(msg) > 0:
            bold, dark = False, False

            if "bold" in msg.keys():
                bold = msg["bold"]

            if "dark" in msg.keys():
                dark = msg["dark"]

            if not "color" in msg.keys():
                msg["color"] = None

            formatted = format_text(str(msg["text"]), msg["color"], dark=dark, bold=bold)

            if not table:
                buffer += formatted
            else:
                buffer.append(formatted)
        else:
            if table:
                buffer.append("")

    if not table:
        print(buffer)
    else:
        print(table_template.format(*buffer))


def splash():
    print(r"""                    ____
                    \  /
                     \/
   _  __  _____    ______   _______       
  | |/ / |  __ \  |  ____| |__   __|  /\    
  |   /  | |__) | | |__       | |    /  \   
  |  (   |  _  /  |  __|      | |   / /\ \  
  |   \  | | \ \  | |____     | |  / /  \ \ 
  |_|\_\ |_|  \_\ |______|    |_| /_/    \_\
                     
                     /\
                    /  \
                     ̅ ̅ ̅ ̅
    """)


def parse_html(html):
    text = html
    text = text.replace("</p>", "\n")
    text = text.replace("<br />", "\n")
    text = re.sub(r"<[^>]*>", "", text)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&auml;", "ä")
    text = text.replace("&ouml;", "ö")
    text = text.replace("&uuml;", "ü")
    text = text.replace("&Auml;", "Ä")
    text = text.replace("&Ouml;", "Ö")
    text = text.replace("&Uuml;", "Ü")
    text = text.replace("&aacute;", "á")
    text = text.replace("&eacute;", "é")
    text = text.replace("&uacute;", "ú")
    text = text.replace("&iacute;", "í")
    text = text.replace("&oacute;", "ó")
    text = text.replace("&Aacute;", "Á")
    text = text.replace("&Eacute;", "É")
    text = text.replace("&Uacute;", "Ú")
    text = text.replace("&Iacute;", "I")
    text = text.replace("&Oacute;", "Ó")
    text = text.replace("&szlig;", "ß")

    return text

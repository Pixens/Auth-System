import json
import datetime

from base64 import b64decode


users = json.load(open("users.json", "r", encoding="utf-8"))


class ApiUtils:

    @staticmethod
    def check_authorization(authorization):
        if not authorization or json.loads(b64decode(authorization.encode()).decode()) not in users:
            return False
        else:
            return True


class Logger:
    @staticmethod
    def inp(level: str, content: str = "", extra: dict = {}):
        message = f"\x1b[0m\x1b[38;5;239m{datetime.datetime.now().strftime('%I:%M:%S %p')} \x1b[38;5;14m{level}\u001B[0m {content}\x1b[0m"
        fields = []
        for key, value in extra.items():
            fields.append(f"\u001B[38;5;239m{key}=\u001B[0m{value}")
        if fields:
            message += " " + " ".join(fields)

        return message

    @staticmethod
    def info(level: str, content: str = "", extra: dict = {}):
        message = f"\x1b[0m\x1b[38;5;239m{datetime.datetime.now().strftime('%I:%M:%S %p')} \x1b[38;5;120m{level}\u001B[0m {content}\x1b[0m"
        fields = []
        for key, value in extra.items():
            fields.append(f"\u001B[38;5;239m{key}=\u001B[0m{value}")
        if fields:
            message += " " + " ".join(fields)

        print(message)

    @staticmethod
    def debug(level: str, content: str = "", extra: dict = {}):
        message = f"\x1b[0m\x1b[38;5;239m{datetime.datetime.now().strftime('%I:%M:%S %p')} \x1b[38;5;221m{level}\u001B[0m {content}\x1b[0m"
        fields = []
        for key, value in extra.items():
            fields.append(f"\u001B[38;5;239m{key}=\u001B[0m{value}")
        if fields:
            message += " " + " ".join(fields)

        print(message)

    @staticmethod
    def error(level: str, content: str = "", extra: dict = {}):
        message = f"\x1b[0m\x1b[38;5;239m{datetime.datetime.now().strftime('%I:%M:%S %p')} \x1b[38;5;203m{level}\u001B[0m {content}\x1b[0m"
        fields = []
        for key, value in extra.items():
            fields.append(f"\u001B[38;5;239m{key}=\u001B[0m{value}")
        if fields:
            message += " " + " ".join(fields)

        print(message)

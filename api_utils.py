import json

from base64 import b64decode


users = json.load(open("users.json", "r", encoding="utf-8"))


class ApiUtils:

    @staticmethod
    def check_authorization(authorization):
        if not authorization or json.loads(b64decode(authorization.encode()).decode()) not in users:
            return False
        else:
            return True

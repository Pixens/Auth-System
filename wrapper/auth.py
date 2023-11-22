import rsa
import requests
import sys
import hashlib
import platform
import os
import subprocess
import binascii

from base64 import b64decode

if os.name == 'nt':
    import win32security


class Utils:

    @staticmethod
    def load_public_key(public_secret):
        base64_decoded_key = b64decode(public_secret)
        public_key = rsa.PublicKey.load_pkcs1(base64_decoded_key)
        return public_key

    @staticmethod
    def encrypt_data(message, public_key):
        return binascii.hexlify(rsa.encrypt(message.encode(), public_key)).decode()

    @staticmethod
    def encrypt_dict(data, public_key):
        encrypted_dict = {}
        for key, value in data.items():
            enc_key = Utils.encrypt_data(key, public_key)
            enc_value = Utils.encrypt_data(value, public_key)

            encrypted_dict[enc_key] = enc_value

        return encrypted_dict

    @staticmethod
    def get_file_hash():
        path = sys.argv[0]
        with open(path, 'rb') as f:
            content = f.read()
            md5 = hashlib.md5()
            md5.update(content)

        return md5.hexdigest()

    @staticmethod
    def get_ip():
        response = requests.get('https://api64.ipify.org?format=json')
        return response.json().get('ip')

    @staticmethod
    def get_hwid():
        if platform.system() == "Linux":
            with open("/etc/machine-id") as f:
                hwid = f.read()
                return hashlib.sha256(hwid.encode()).hexdigest()

        elif platform.system() == 'Windows':
            winuser = os.getlogin()
            sid = win32security.LookupAccountName(None, winuser)[0]
            hwid = win32security.ConvertSidToStringSid(sid)
            return hashlib.sha256(hwid.encode()).hexdigest()

        elif platform.system() == 'Darwin':
            output = subprocess.Popen("ioreg -l | grep IOPlatformSerialNumber", stdout=subprocess.PIPE, shell=True).communicate()[0]
            serial = output.decode().split('=', 1)[1].replace(' ', '')
            hwid = serial[1:-2]
            return hashlib.sha256(hwid.encode()).hexdigest()

        else:
            raise Exception('Unsupported operating system.')

    @staticmethod
    def validate_signature(message, signature, public_key):
        try:
            response = rsa.verify(message.encode(), binascii.unhexlify(signature.encode()), public_key)
            if response == 'SHA-256':
                return True
            else:
                return False

        except rsa.pkcs1.VerificationError:
            return False


class Auth:

    def __init__(self, public_secret: str):
        self.session = requests.Session()
        self.public_key = Utils.load_public_key(public_secret)

    def license_login(self, app_id: str, app_version: str, license_key: str):
        payload = {
            "app_id": app_id,
            "app_version": app_version,
            "license_key": license_key,
            "hwid": Utils.get_hwid(),
            "ip": Utils.get_ip(),
            "file_hash": Utils.get_file_hash()
        }
        encrypted_payload = Utils.encrypt_dict(payload, self.public_key)

        payload = {
            "encrypted_dict": encrypted_payload
        }

        response = self.session.post('http://127.0.0.1:80/license-login', json=payload)
        if response.json()["success"]:
            validity = Utils.validate_signature(license_key, response.json()["signature"], self.public_key)
            if validity:
                return True
            else:
                raise Exception("Could not verify signature. Please do not alter the requests.")

        else:
            if response.json().get("download_link"):
                raise Exception(f'Application is not up to date. Use this link to download the latest version. {response.json()["download_link"]}')
            else:
                raise Exception(f'{response.json()["message"]}')


auth = Auth(
    public_secret="LS0tLS1CRUdJTiBSU0EgUFVCTElDIEtFWS0tLS0tCk1JR0pBb0dCQU9oTFRZRzBMc3hubDlzREllbE5XM1ZLTDhlY0RtOG5NVnh2RitvTkJoYjF0dFB5WVZsL0N0NisKeVQ3Q0ozb2czWTR0WDZoMkxGYVdmTHdVMkNYbnNzR2R3aGpDWVhJUWpMMFY5bS9ISTRMRHJXQVVNazFHWnIvQwpwaGlFUUhnZUQzejZlaTdLTG1JbTB6WGNKbUlWaGVqTWg4aGlOTUhxSkt5dUhTa0dsL1dqQWdNQkFBRT0KLS0tLS1FTkQgUlNBIFBVQkxJQyBLRVktLS0tLQo="
)

result = auth.license_login(
    app_id="65535a1113facd3ba4d54ea0",
    app_version="1.0",
    license_key="Boostup-63F29"
)
print(result)

import rsa
import binascii
import threading

from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from authentication.utils import Utils


client = MongoClient("localhost", 27017)
database = client.boostupauth


class Authenticate:

    def __init__(self):
        self.license_collection = database.licenses
        self.app_collection = database.applications

    def license_login(self, encrypted_data: dict) -> dict:
        try:
            decryption_result = Utils.decrypt_dict(encrypted_data)

            if not decryption_result["private_key"]:
                return {
                    'success': False,
                    'message': 'Failed to decrypt data.'
                }

            data = decryption_result["data"]

            if not data.get('app_id') or not data.get('license_key') or not data.get('hwid') or not data.get('ip') or not data.get('file_hash') or not data.get('app_version'):
                return {
                    'success': False,
                    'message': 'Invalid/Insufficient data received.'
                }

            app_data = self.app_collection.find_one({'_id': ObjectId(data['app_id'])})
            if decryption_result["app_found"]["public_secret"] != app_data["public_secret"]:
                return {
                    'success': False,
                    'message': 'Public secret is invalid.'
                }

            if not app_data:
                return {
                    'success': False,
                    'message': 'Application does not exist.'
                }

            if data['app_version'] != app_data['app_version']:
                return {
                    'success': False,
                    'message': 'Application is not up to date. Please update or contact your seller for update.',
                    'download_link': app_data['download_link']
                }

            if app_data['file_hash'] != data['file_hash']:
                return {
                    'success': False,
                    'message': 'File hash does not match. Please do not alter the executable in any way.'
                }

            license_data = self.license_collection.find_one({'_id': {'license_key': data['license_key']}})
            if not license_data or data['app_id'] != license_data['app_id']:
                return {
                    'success': False,
                    'message': 'Invalid license key.'
                }
            updated_data = {}

            if not license_data['expires_on']:
                updated_data['expires_on'] = (datetime.now() + timedelta(days=license_data['duration'])).strftime("%d-%m-%Y %H:%M:%S")
            if not license_data['hwid']:
                updated_data['hwid'] = data['hwid']
            elif license_data['hwid'] != data['hwid']:
                return {
                    'success': False,
                    'message': 'The HWID does not match. Please use the program on the same device you used the very first time or ask for an HWID reset.'
                }
            if not license_data.get('ip'):
                updated_data['ip'] = data['ip']

            if len(updated_data):
                self.license_collection.update_one(
                    {"_id": {'license_key': data['license_key']}},
                    {
                        "$set": updated_data
                    }
                )

            license_data = self.license_collection.find_one({'_id': {'license_key': data['license_key']}})
            valid = Utils.validate_license(license_data)
            if valid:
                signature = binascii.hexlify(rsa.sign(data['license_key'].encode(), Utils.load_private_key(app_data['private_secret']), "SHA-256")).decode()
                return {
                    'success': True,
                    'message': 'Valid license key.',
                    'signature': signature
                }
            else:
                return {
                    'success': False,
                    'message': 'Your license has expired.'
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to validate key. {str(e).capitalize() if '.' in str(e).capitalize() else f'{str(e).capitalize()}.'}"
            }


# Test


# authenticate = Authenticate()
#
# public_key = Utils.load_public_key("LS0tLS1CRUdJTiBSU0EgUFVCTElDIEtFWS0tLS0tCk1JR0pBb0dCQUlGN1RZbEFXYU1tVStlZHBMb0hSaTRoOWc5RWE1NDVrZkNUWldncmMwWGY0MFNldUd5bTJwQUkKYUdVZnBxZG5hS0xUSlpvOEJPUEk5YkVId3NHL1hLSVZITUFDaTVaRmErYVpQSDE3aHNXcVFyemtXTHFuRkZZUgpDOFZ0RWNoSXBKSlRrUmt3UEVVK1dOZWpQb2dHYTNlT1RHTWlONUozVmQ3T3pHQ0IvNVViQWdNQkFBRT0KLS0tLS1FTkQgUlNBIFBVQkxJQyBLRVktLS0tLQo=")
#
# ed = {
#     binascii.hexlify(rsa.encrypt("app_id".encode(), public_key)).decode(): binascii.hexlify(rsa.encrypt("6553bc50086cc1b5b4779851".encode(), public_key)).decode(),
#     binascii.hexlify(rsa.encrypt("license_key".encode(), public_key)).decode(): binascii.hexlify(rsa.encrypt("Boostup-363A".encode(), public_key)).decode(),
#     binascii.hexlify(rsa.encrypt("hwid".encode(), public_key)).decode(): binascii.hexlify(rsa.encrypt("eb5ba6d59a5a23e49b7fd0b624d06b3321ec5d00a45001630dcebcad72d2f3ad785759d78cae30960e237f51d4c6ee4e".encode(), public_key)).decode(),
#     binascii.hexlify(rsa.encrypt("ip".encode(), public_key)).decode(): binascii.hexlify(rsa.encrypt("1.20.0".encode(), public_key)).decode(),
#     binascii.hexlify(rsa.encrypt("file_hash".encode(), public_key)).decode(): binascii.hexlify(rsa.encrypt("2".encode(), public_key)).decode(),
#     binascii.hexlify(rsa.encrypt("app_version".encode(), public_key)).decode(): binascii.hexlify(rsa.encrypt("1.0".encode(), public_key)).decode()
# }
# re = authenticate.license_login(ed)
# print(re)

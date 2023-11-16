import rsa
import binascii

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
        self.private_key = None

    def initialize_app(self, app_id: str, app_version: str) -> dict:
        try:
            application_data = self.app_collection.find_one({'_id': ObjectId(app_id)})
            if not application_data:
                return {
                    'success': False,
                    'message': 'Application does not exist.'
                }

            if app_version != application_data['app_version']:
                return {
                    'success': False,
                    'message': 'Application is not up to date. Please update or contact your seller for update.',
                    'download_link': application_data['download_link']
                }

            new_private_key = Utils.load_private_key(application_data['private_secret'])
            if new_private_key:
                self.private_key = new_private_key
                signature = binascii.hexlify(rsa.sign(app_id.encode(), new_private_key, "SHA-256"))
                return {
                    'success': True,
                    'message': 'Successfully initialized app.',
                    'signature': signature
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to initialize app.'
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to initialize app. {str(e).capitalize if '.' in str(e).capitalize else f'{str(e).capitalize}.'}"
            }

    def license_login(self, encrypted_data: dict) -> dict:
        try:
            data = {}

            for enc_key in encrypted_data:
                enc_value = encrypted_data[enc_key]
                key = Utils.decrypt_data(enc_key, self.private_key)
                value = Utils.decrypt_data(enc_value, self.private_key)

                data[key] = value

            app_data = self.app_collection.find_one({'_id': ObjectId(data['app_id'])})
            if not app_data:
                return {
                    'success': False,
                    'message': 'Invalid app ID provided.'
                }
            if app_data['file_hash'] != data['file_hash']:
                return {
                    'success': False,
                    'message': 'File hash does not match. Please do not alter the executable in any way.'
                }

            license_data = self.license_collection.find_one({'_id': {'license_key': data['license_key']}})
            if not license_data or not data['app_id'] == license_data['app_id']:
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
            if not license_data['ip']:
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
                signature = binascii.hexlify(rsa.sign(data['license_key'].encode(), self.private_key, "SHA-256"))
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
                "message": f"Failed to validate key. {str(e).capitalize if '.' in str(e).capitalize else f'{str(e).capitalize}.'}"
            }



authenticate = Authenticate()
o = authenticate.initialize_app(app_id='65535a1113facd3ba4d54ea0', app_version='1.0')
print(o)

if o['success']:
    public_key = Utils.load_public_key("LS0tLS1CRUdJTiBSU0EgUFVCTElDIEtFWS0tLS0tCk1JR0pBb0dCQU9oTFRZRzBMc3hubDlzREllbE5XM1ZLTDhlY0RtOG5NVnh2RitvTkJoYjF0dFB5WVZsL0N0NisKeVQ3Q0ozb2czWTR0WDZoMkxGYVdmTHdVMkNYbnNzR2R3aGpDWVhJUWpMMFY5bS9ISTRMRHJXQVVNazFHWnIvQwpwaGlFUUhnZUQzejZlaTdLTG1JbTB6WGNKbUlWaGVqTWg4aGlOTUhxSkt5dUhTa0dsL1dqQWdNQkFBRT0KLS0tLS1FTkQgUlNBIFBVQkxJQyBLRVktLS0tLQo=")

    ed = {
        binascii.hexlify(rsa.encrypt("app_id".encode(), public_key)).decode(): binascii.hexlify(rsa.encrypt("65535a1113facd3ba4d54ea0".encode(), public_key)).decode(),
        binascii.hexlify(rsa.encrypt("license_key".encode(), public_key)).decode(): binascii.hexlify(rsa.encrypt("Boostup-63F29".encode(), public_key)).decode(),
        binascii.hexlify(rsa.encrypt("hwid".encode(), public_key)).decode(): binascii.hexlify(rsa.encrypt("eb5ba6d59a5a23e49b7fd0b624d06b3321ec5d00a45001630dcebcad72d2f3ad785759d78cae30960e237f51d4c6ee4e".encode(), public_key)).decode(),
        binascii.hexlify(rsa.encrypt("ip".encode(), public_key)).decode(): binascii.hexlify(rsa.encrypt("106.2".encode(), public_key)).decode(),
        binascii.hexlify(rsa.encrypt("file_hash".encode(), public_key)).decode(): binascii.hexlify(rsa.encrypt("2".encode(), public_key)).decode()
    }

    re = authenticate.license_login(ed)
    print(re)

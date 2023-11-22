import string
import random
import rsa
import binascii

from base64 import b64decode
from datetime import datetime
from pymongo import MongoClient

client = MongoClient("localhost", 27017)
database = client.boostupauth
app_collection = database.applications


class Utils:

    @staticmethod
    def generate_license_key(key_mask: str):
        key_mask_list = list(key_mask)

        for _ in range(key_mask.count('X')):
            index = key_mask_list.index('X')
            key_mask_list[index] = random.choice(list(string.hexdigits))

        license_key = ''.join(map(str, key_mask_list))
        return license_key

    @staticmethod
    def load_private_key(private_secret):
        base64_decoded_key = b64decode(private_secret)
        private_key = rsa.PrivateKey.load_pkcs1(base64_decoded_key)
        return private_key

    @staticmethod
    def load_public_key(public_secret):
        base64_decoded_key = b64decode(public_secret)
        public_key = rsa.PublicKey.load_pkcs1(base64_decoded_key)
        return public_key

    @staticmethod
    def find_private_key(encrypted_data):
        private_key = None
        app = None
        for app in app_collection.find():
            try:
                private_secret = app["private_secret"]
                private_key = Utils.load_private_key(private_secret)
                decrypted_message = rsa.decrypt(binascii.unhexlify(encrypted_data.encode()), private_key).decode()
                if decrypted_message:
                    break
            except rsa.pkcs1.DecryptionError:
                continue

        return private_key, app


    @staticmethod
    def decrypt_data(encrypted_data, private_key):
        return rsa.decrypt(
            binascii.unhexlify(
                encrypted_data.encode()
            ), private_key
        ).decode()


    @staticmethod
    def decrypt_dict(encrypted_dict):
        data = {}
        private_key, app_found = Utils.find_private_key(list(encrypted_dict.items())[0][0])
        if not private_key:
            return {
                'data': None,
                'private_key': None,
                'app_found': None
            }

        for enc_key, enc_value in encrypted_dict.items():
            key = Utils.decrypt_data(enc_key, private_key)
            value = Utils.decrypt_data(enc_value, private_key)

            data[key] = value

        return {
            'data': data,
            'private_key': private_key,
            'app_found': app_found
        }

    @staticmethod
    def validate_license(license_data):
        now = datetime.now()
        return now <= datetime.strptime(license_data['expires_on'], "%d-%m-%Y %H:%M:%S")



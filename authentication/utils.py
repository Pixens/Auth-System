import string
import random
import rsa
import binascii

from base64 import b64decode
from datetime import datetime


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
    def decrypt_data(encrypted_data, private_key):
        return rsa.decrypt(
            binascii.unhexlify(
                encrypted_data.encode()
            ), private_key
        ).decode()

    @staticmethod
    def validate_license(license_data):
        now = datetime.now()
        return now > datetime.strptime(license_data['expires_on'], "%d-%m-%Y %H:%M:%S")




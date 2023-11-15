from pymongo import MongoClient
from datetime import datetime, timedelta
from authentication.utils import Utils


client = MongoClient("localhost", 27017)
database = client.boostupauth


class LicenseFunctions:

    def __init__(self):
        self.license_collection = database.licenses
        self.app_collection = database.applications

    def create_license(self, app_name: str, key_mask: str, duration: int, note: str = str()) -> dict:
        try:
            if not self.app_collection.find_one({"app_name": app_name}):
                return {
                    "success": False,
                    "message": "Failed to create license. Application does not exist."
                }
            else:
                app_id = str(self.app_collection.find_one({"app_name": app_name})['_id'])
                license_key = Utils.generate_license_key(key_mask)
                tries = 0
                while self.license_collection.find_one({"_id": {'license_key': license_key}}) and tries < 100:
                    license_key = Utils.generate_license_key(key_mask)
                    tries += 1

                if tries >= 100:
                    return {
                        "success": False,
                        "message": "Failed to create license. Cannot generate a unique license key."
                    }

                license_key_object = {
                    "license_key": license_key
                }

                insert_dict = {
                    "_id": license_key_object,
                    "app_id": app_id,
                    "generated_on": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                    "duration": duration,
                    "expires_on": "",
                    "hwid": "",
                    "ip": "",
                    "note": note
                }
                result = self.license_collection.insert_one(insert_dict)

                return_dict = {
                    "success": result.acknowledged,
                    "message": "Successfully created license." if result.acknowledged else "Failed to create license.",
                }
                if result.acknowledged:
                    return_dict["data"] = {
                        "app_name": app_name,
                        "license_key": license_key,
                        "duration": duration,
                        "note": note
                    }
                return return_dict

        except Exception as e:
            return {
                    "success": False,
                    "message": f"Failed to create license. {str(e).capitalize if '.' in str(e).capitalize else str(e).capitalize + '.'}"
                }

    def get_license_info(self, license_key: str) -> dict:
        try:
            if not self.license_collection.find_one({"_id": {"license_key": license_key}}):
                return {
                    "success": False,
                    "message": "Failed to fetch license information. License does not exist."
                }
            else:
                license_information = self.license_collection.find_one({"_id": {"license_key": license_key}})
                return {
                    "success": True,
                    "message": "Successfully fetched license information.",
                    "data": {
                        "license_key": license_information["_id"]["license_key"],
                        "duration": license_information["duration"],
                        "app_id": license_information["app_id"],
                        "expires_on": license_information["expires_on"],
                        "ip": license_information["ip"],
                        "note": "Pixens"
                    }
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to fetch license information. {str(e).capitalize if '.' in str(e).capitalize else f'{str(e).capitalize}.'}"
            }

    def extend_license(self, license_key: str, extension_days: int) -> dict:
        try:
            if not self.license_collection.find_one({"_id": {"license_key": license_key}}):
                return {
                    "success": False,
                    "message": "Failed to update license. License does not exist."
                }
            else:
                updated_dict = {}
                license_information = self.license_collection.find_one({"_id": {'license_key': license_key}})
                new_expiry = license_information['duration'] + extension_days
                updated_dict["duration"] = new_expiry
                if license_information['expires_on']:
                    extended_expiry_date = (datetime.strptime(license_information['expires_on'], "%d-%m-%Y %H:%M:%S") + timedelta(days=extension_days)).strftime("%d-%m-%Y %H:%M:%S")
                    updated_dict["expires_on"] = extended_expiry_date


                result = self.license_collection.update_one(
                    {"_id": {"license_key": license_key}},
                    {
                        "$set": updated_dict
                    }
                )

                return {
                    'success': result.acknowledged,
                    'message': f'Successfully extended license by {extension_days} days.' if result.acknowledged else 'Failed to extend license.'
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to extend license. {str(e).capitalize if '.' in str(e).capitalize else str(e).capitalize + '.'}"
            }


    def delete_license(self, license_key: str) -> dict:
        try:
            if not self.license_collection.find_one({"_id": {"license_key": license_key}}):
                return {
                    "success": False,
                    "message": "Failed to delete license. License does not exist."
                }
            else:
                result = self.license_collection.delete_one({"_id": {"license_key": license_key}})
                return {
                    'success': result.acknowledged,
                    'message': 'Successfully deleted license.' if result.acknowledged else 'Failed to delete license.'
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to delete license. {str(e).capitalize if '.' in str(e).capitalize else str(e).capitalize + '.'}"
            }

    def reset_hwid(self, license_key: str) -> dict:
        try:
            if not self.license_collection.find_one({"_id": {"license_key": license_key}}):
                return {
                    "success": False,
                    "message": "Failed to reset HWID. License does not exist."
                }
            else:
                result = self.license_collection.update_one(
                    {"_id": {"license_key": license_key}},
                    {
                        "$set": {"hwid": ""}
                    }
                )

                return {
                    'success': result.acknowledged,
                    'message': 'Successfully reset HWID.' if result.acknowledged else 'Failed to reset HWID.'
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to reset HWID. {str(e).capitalize if '.' in str(e).capitalize else str(e).capitalize + '.'}"
            }

    def hwid_reset_all(self):
        try:
            result = self.license_collection.update_many(
                {}, {"$set": {"hwid": ""}}
            )

            return {
                "success": result.acknowledged,
                "message": "Successfully reset all HWIDs." if result.acknowledged else "Failed to reset all HWIDs."
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to reset HWIDs. {str(e).capitalize if '.' in str(e).capitalize else str(e).capitalize + '.'}"
            }


# LicenseFunctions().create_license(
#     app_name='Boost Tool',
#     key_mask='Boostup-XXXXX',
#     duration=30,
#     note='Pixens'
# )

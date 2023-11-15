import rsa

from base64 import b64encode
from pymongo import MongoClient
from bson.objectid import ObjectId


client = MongoClient("localhost", 27017)
database = client.boostupauth


class ApplicationFunctions:

    def __init__(self):
        self.app_collection = database.applications

    def create_application(self, app_name: str, app_version: str) -> dict:
        try:
            if self.app_collection.find_one({"app_name": app_name}):
                return {
                    "success": False,
                    "message": 'Application already exists.'
                }

            else:
                public_key, private_key = rsa.newkeys(1024)
                public_secret = b64encode(public_key.save_pkcs1("PEM")).decode()
                private_secret = b64encode(private_key.save_pkcs1("PEM")).decode()
                inserted_app = self.app_collection.insert_one(
                    {
                        "app_name": app_name,
                        "private_secret": private_secret,
                        "public_secret": public_secret,
                        "app_version": app_version,
                        "download_link": "",
                        "file_hash": ""
                    }
                )
                return {
                    "success": True,
                    "message": "Successfully created application.",
                    "data": {
                        "app_id": str(inserted_app.inserted_id),
                        "app_name": app_name,
                        "public_secret": public_secret,
                        "app_version": app_version
                    }
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create application. {str(e).capitalize if '.' in str(e).capitalize else f'{str(e).capitalize}.'}"
            }

    def get_application_info(self, app_name: str) -> dict:
        try:
            if not self.app_collection.find_one({"app_name": app_name}):
                return {
                    "success": False,
                    "message": "Failed to fetch application information. Application does not exist."
                }
            else:
                app_info = self.app_collection.find_one({"app_name": app_name})
                return {
                    "success": True,
                    "message": "Successfully fetched application information.",
                    "data": {
                        "app_id": str(app_info['_id']),
                        "app_name": app_info['app_name'],
                        "public_secret": app_info['public_secret'],
                        "app_version": app_info['app_version'],
                        "download_link": app_info['download_link'],
                        "file_hash": app_info['file_hash']
                    }
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to fetch application information. {str(e).capitalize if '.' in str(e).capitalize else f'{str(e).capitalize}.'}"
            }

    def update_application(self, app_id: str, app_name: str = str(), app_version: str = str(), download_link: str = str(), file_hash: str = str()) -> dict:
        try:
            if not self.app_collection.find_one({"_id": ObjectId(app_id)}):
                return {
                    "success": False,
                    "message": "Failed to update application. Application does not exist."
                }
            else:
                update_dict = {}

                if app_name:
                    update_dict["app_name"] = app_name
                if app_version:
                    update_dict["app_version"] = app_version
                if download_link:
                    update_dict["download_link"] = download_link
                if file_hash:
                    update_dict["file_hash"] = file_hash

                if len(update_dict):
                    result = self.app_collection.update_one(
                        {"_id": ObjectId(app_id)},
                        {
                            "$set": update_dict
                        }
                    )

                    return {
                        "success": result.acknowledged,
                        "message": "Successfully updated application info." if result.acknowledged else "Failed to update application info."
                    }
                else:
                    return {
                        "success": False,
                        "message": "No data provided."
                    }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to update application info. {str(e).capitalize if '.' in str(e).capitalize else f'{str(e).capitalize}.'}"
            }

    def delete_application(self, app_name: str) -> dict:
        try:
            if not self.app_collection.find_one({"app_name": app_name}):
                return {
                    "success": False,
                    "message": "Failed to delete application. Application does not exist."
                }
            else:
                result = self.app_collection.delete_one({'app_name': app_name})
                return {
                    "success": result.acknowledged,
                    "message": "Successfully deleted application." if result.acknowledged else "Failed to delete application."
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to fetch application info. {str(e).capitalize if '.' in str(e).capitalize else f'{str(e).capitalize}.'}"
            }


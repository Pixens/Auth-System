import json
import logging

from flask import Flask, request, jsonify
from api_utils import ApiUtils
from api_utils import Logger
from authentication.app_functions import ApplicationFunctions
from authentication.license_functions import LicenseFunctions
from authentication.auth_functions import Authenticate


users = json.load(open("users.json", "r", encoding="utf-8"))

ApplicationFunctions = ApplicationFunctions()
LicenseFunctions = LicenseFunctions()
Auth = Authenticate()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask("auth")


# ---App Endpoints---

@app.route("/create-app", methods=["POST"])
def create_app():
    authorization = request.headers.get("Authorization")

    if not ApiUtils.check_authorization(authorization):
        return jsonify({"success": False, "message": "Invalid authorization."}), 401

    app_payload = request.get_json()

    if not app_payload.get("app_name") or not app_payload.get("app_version"):
        return jsonify({"success": False, "message": "Invalid/Insufficient data received."}), 400

    create_app_result = ApplicationFunctions.create_application(
        app_name=app_payload["app_name"],
        app_version=app_payload["app_version"]
    )

    Logger.info('[+]', '/create-app', {'result': create_app_result["message"]})

    return jsonify(create_app_result), 201


@app.route("/app-info", methods=["GET"])
def app_info():
    authorization = request.headers.get("Authorization")

    if not ApiUtils.check_authorization(authorization):
        return jsonify({"success": False, "message": "Invalid authorization."}), 401

    app_payload = request.get_json()

    if not app_payload.get("app_name"):
        return jsonify({"success": False, "message": "Invalid/Insufficient data received."}), 400

    app_info_result = ApplicationFunctions.get_application_info(
        app_name=app_payload["app_name"]
    )

    Logger.info('[+]', '/app-info', {'result': app_info_result["message"]})

    return jsonify(app_info_result), 200


@app.route("/update-app/<app_id>", methods=["PATCH"])
def update_app(app_id):
    authorization = request.headers.get("Authorization")

    if not ApiUtils.check_authorization(authorization):
        return jsonify({"success": False, "message": "Invalid authorization."}), 401

    app_payload = request.get_json()

    if not app_payload:
        return jsonify({"success": False, "message": "No data received."}), 400

    update_app_result = ApplicationFunctions.update_application(
        app_id=app_id,
        app_name=app_payload.get("app_name"),
        app_version=app_payload.get("app_version"),
        download_link=app_payload.get("download_link"),
        file_hash=app_payload.get("file_hash")
    )

    Logger.info('[+]', f'/update-app/{app_id}', {'result': update_app_result["message"]})

    return jsonify(update_app_result), 200


@app.route("/delete-app", methods=["DELETE"])
def delete_app():
    authorization = request.headers.get("Authorization")

    if not ApiUtils.check_authorization(authorization):
        return jsonify({"success": False, "message": "Invalid authorization."}), 401

    app_payload = request.get_json()

    if not app_payload.get("app_name"):
        return jsonify({"success": False, "message": "Invalid/Insufficient data received."}), 400

    delete_app_result = ApplicationFunctions.delete_application(
        app_name=app_payload["app_name"]
    )

    Logger.info('[+]', f'/delete-app', {'result': delete_app_result["message"]})

    return jsonify(delete_app_result), 200


@app.route("/fetch-apps", methods=["GET"])
def fetch_apps():
    authorization = request.headers.get("Authorization")

    if not ApiUtils.check_authorization(authorization):
        return jsonify({"success": False, "message": "Invalid authorization."}), 401

    fetch_apps_result = ApplicationFunctions.get_all_apps()

    Logger.info('[+]', f'/fetch-apps', {'result': fetch_apps_result["message"]})

    return jsonify(fetch_apps_result), 200


# ---License Endpoints---

@app.route("/create-sellix-license", methods=["GET"])
def sellix_create_license():
    app_name = request.args.get('app')
    license_duration = request.args.get('duration')
    note = request.args.get('note')

    if not app_name or not license_duration or not note:
        return "Insufficient data passed.", 200

    create_license_result = LicenseFunctions.create_license(
        app_name=app_name,
        key_mask='Boostup-XXXXX-XXXXX',
        duration=int(license_duration),
        note=note
    )

    Logger.info('[+]', '/create-sellix-license', {'result': create_license_result["message"]})

    return create_license_result["data"]["license_key"] if create_license_result["success"] else create_license_result["message"], 200


@app.route("/create-license", methods=["POST"])
def create_license():
    authorization = request.headers.get("Authorization")

    if not ApiUtils.check_authorization(authorization):
        return jsonify({"success": False, "message": "Invalid authorization."}), 401

    license_payload = request.get_json()

    if not license_payload.get("app_name") or not license_payload.get("key_mask") or not license_payload.get("duration"):
        return jsonify({"success": False, "message": "Invalid/Insufficient data received."}), 400

    create_license_result = LicenseFunctions.create_license(
        app_name=license_payload["app_name"],
        key_mask=license_payload["key_mask"],
        duration=int(license_payload["duration"]),
        note=license_payload["note"] if license_payload.get("note") else ""
    )

    Logger.info('[+]', f'/create-license', {'result': create_license_result["message"]})

    return jsonify(create_license_result), 200


@app.route("/license-info", methods=["GET"])
def fetch_license():
    authorization = request.headers.get("Authorization")

    if not ApiUtils.check_authorization(authorization):
        return jsonify({"success": False, "message": "Invalid authorization."}), 401

    license_payload = request.get_json()

    if not license_payload.get("license_key"):
        return jsonify({"success": False, "message": "Invalid/Insufficient data received."}), 400

    fetch_license_result = LicenseFunctions.get_license_info(
        license_key=license_payload["license_key"]
    )

    Logger.info('[+]', f'/fetch-license', {'result': fetch_license_result["message"]})

    return jsonify(fetch_license_result), 200


@app.route("/extend-license", methods=["PATCH"])
def extend_license():
    authorization = request.headers.get("Authorization")

    if not ApiUtils.check_authorization(authorization):
        return jsonify({"success": False, "message": "Invalid authorization."}), 401

    license_payload = request.get_json()

    if not license_payload.get("license_key") or not license_payload.get("extension_days"):
        return jsonify({"success": False, "message": "Invalid/Insufficient data received."}), 400

    extend_license_result = LicenseFunctions.extend_license(
        license_key=license_payload["license_key"],
        extension_days=license_payload["extension_days"]
    )

    Logger.info('[+]', f'/extend-license', {'result': extend_license_result["message"]})

    return jsonify(extend_license_result), 200


@app.route("/delete-license", methods=["DELETE"])
def delete_license():
    authorization = request.headers.get("Authorization")

    if not ApiUtils.check_authorization(authorization):
        return jsonify({"success": False, "message": "Invalid authorization."}), 401

    license_payload = request.get_json()

    if not license_payload.get("license_key"):
        return jsonify({"success": False, "message": "Invalid/Insufficient data received."}), 400

    delete_license_result = LicenseFunctions.delete_license(
        license_key=license_payload["license_key"]
    )

    Logger.info('[+]', f'/delete-license', {'result': delete_license_result["message"]})

    return jsonify(delete_license_result), 200


@app.route("/reset-hwid", methods=["PATCH"])
def reset_user_hwid():
    authorization = request.headers.get("Authorization")

    if not ApiUtils.check_authorization(authorization):
        return jsonify({"success": False, "message": "Invalid authorization."}), 401

    license_payload = request.get_json()

    if not license_payload.get("license_key"):
        return jsonify({"success": False, "message": "Invalid/Insufficient data received."}), 400

    reset_hwid_result = LicenseFunctions.reset_hwid(
        license_key=license_payload["license_key"]
    )

    Logger.info('[+]', f'/reset-hwid', {'result': reset_hwid_result["message"]})

    return jsonify(reset_hwid_result), 200


@app.route("/reset-all-hwids", methods=["PATCH"])
def reset_all_hwids():
    authorization = request.headers.get("Authorization")

    if not ApiUtils.check_authorization(authorization):
        return jsonify({"success": False, "message": "Invalid authorization."}), 401

    reset_all_hwids_result = LicenseFunctions.hwid_reset_all()

    Logger.info('[+]', f'/reset-all-hwids', {'result': reset_all_hwids_result["message"]})

    return jsonify(reset_all_hwids_result), 200


# ---Authentication Endpoints---

@app.route("/license-login", methods=["POST"])
def license_login():
    auth_payload = request.get_json()

    if not auth_payload.get("encrypted_dict"):
        return jsonify({"success": False, "message": "Invalid/Insufficient data received."}), 400

    result = Auth.license_login(
        encrypted_data=auth_payload["encrypted_dict"]
    )

    Logger.info('[+]', f'/license-login', {'result': result["message"]})

    if result.get('message') == 'Invalid/Insufficient data received.':
        return jsonify(result), 400

    return jsonify(result), 200


Logger.info('[+]', 'Started API on port 80')
app.run(
    host='0.0.0.0',
    port=80
)
print()

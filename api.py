from flask import Flask, request, jsonify
from authentication.app_functions import ApplicationFunctions


app = Flask("auth")


@app.route("/create-app", methods=["POST"])
def create_app():
    app_payload = request.get_json()

    if not app_payload.get("app_name") or not app_payload.get("app_version"):
        return jsonify({"success": False, "message": "Invalid/Insufficient data received."}), 400

    create_app_result = ApplicationFunctions().create_application(
        app_name=app_payload["app_name"],
        app_version=app_payload["app_version"]
    )

    return jsonify(create_app_result), 201


@app.route("/app-info", methods=["GET"])
def app_info():
    app_payload = request.get_json()

    if not app_payload.get("app_name"):
        return jsonify({"success": False, "message": "Invalid/Insufficient data received."}), 400

    app_info_result = ApplicationFunctions().get_application_info(
        app_name=app_payload["app_name"]
    )

    return jsonify(app_info_result), 200


@app.route("/update-app/<app_id>", methods=["PATCH"])
def update_app(app_id):
    app_payload = request.get_json()

    if not app_payload:
        return jsonify({"success": False, "message": "No data received."}), 400

    update_app_result = ApplicationFunctions().update_application(
        app_id=app_id,
        app_name=app_payload.get("app_name"),
        app_version=app_payload.get("app_version"),
        download_link=app_payload.get("download_link"),
        file_hash=app_payload.get("file_hash")
    )

    return jsonify(update_app_result), 200



app.run(
    host='0.0.0.0',
    port=80,
    debug=True
)
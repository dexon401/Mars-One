import flask

from datetime import datetime
from flask import request, make_response, jsonify

from . import db_session
from .users import User

blueprint = flask.Blueprint("user_api", __name__, template_folder="templates")


@blueprint.route("/api/user")
def get_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(User).all()
    return jsonify([item.to_dict(rules=("-departments", "-jobs")) for item in jobs])


@blueprint.route("/api/user/<user_id>")
def get_job(user_id):
    db_sess = db_session.create_session()
    try:
        user = db_sess.get(User, int(user_id))
        if user:
            return jsonify(user.to_dict(rules=("-departments", "-jobs")))
        else:
            return make_response(jsonify({"error": "Not found"}), 404)
    except Exception:
        pass
    return make_response(jsonify({"error": "Bad request"}), 400)


@blueprint.route("/api/user", methods=["POST"])
def create_job():
    if not request.json:
        return make_response(jsonify({"error": "Empty request"}), 400)
    elif not all(
        key in request.json
        for key in [
            "surname",
            "name",
            "age",
            "position",
            "speciality",
            "address",
            "email",
            "password",
            "modified_date"
        ]
    ):
        return make_response(jsonify({"error": "Bad request"}), 400)

    try:
        surname = request.json["surname"]
        name = request.json["name"]
        age = int(request.json["age"])
        position = request.json["position"]
        speciality = request.json["speciality"]
        address = request.json["address"]
        email = request.json["email"]
        password = request.json["password"]
        modified_date = datetime.fromisoformat(request.json["modified_date"])
    except (ValueError, TypeError) as e:
        return make_response(jsonify({"error": f"invalid data type: {e}"}), 400)

    db_sess = db_session.create_session()
    user = User()
    user.surname = surname
    user.name = name
    user.age = age
    user.position = position
    user.speciality = speciality
    user.address = address
    user.email = email
    user.modified_date = modified_date
    user.set_password(password)
    db_sess.add(user)
    db_sess.commit()
    return jsonify({"id": user.id})


@blueprint.route("/api/user/<user_id>", methods=["DELETE"])
def delete_news(user_id):
    try:
        user_id = int(user_id)
    except (ValueError, TypeError) as e:
        return make_response(jsonify({"error": f"invalid data type: {e}"}), 400)
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)
    if not user:
        return make_response(jsonify({"error": "Not found"}), 404)
    db_sess.delete(user)
    db_sess.commit()
    return jsonify({"success": "OK"})


@blueprint.route("/api/user/<user_id>", methods=["PUT"])
def edit_job(user_id):
    try:
        user_id = int(user_id)
    except (ValueError, TypeError) as e:
        return make_response(jsonify({"error": f"invalid data type: {e}"}), 400)
    db_sess = db_session.create_session()
    user = db_sess.get(User, user_id)
    if not user:
        return make_response(jsonify({"error": "Not found"}), 404)
    
    if not request.json:
        return make_response(jsonify({"error": "Empty request"}), 400)
    
    for k in request.json:
        if hasattr(user, k) and k != "id":
            try:
                setattr(user, k, request.json[k])
            except (ValueError, TypeError) as e:
                return make_response(jsonify({"error": f"invalid data type: {e}"}), 400)
    db_sess.commit()
    
    return jsonify({"success": "OK"})

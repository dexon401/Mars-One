from flask_restful import Resource, abort, reqparse
from flask import jsonify
from .db_session import create_session
from .users import User

parser = reqparse.RequestParser()
parser.add_argument("surname", required=True)
parser.add_argument("name", required=True)
parser.add_argument("age", required=True, type=int)
parser.add_argument("position", required=True)
parser.add_argument("speciality", required=True)
parser.add_argument("address", required=True)
parser.add_argument("email", required=True)
parser.add_argument("password", required=True)


def abort_if_user_not_found(user_id):
    session = create_session()
    user = session.get(User, user_id)
    session.close()
    if not user:
        abort(404, messsage=f"User {user_id} not found")


class UsersResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = create_session()
        user = session.get(User, user_id)
        return jsonify(
            {"user": user.to_dict(rules=["-departments", "-jobs", "-hashed_password"])}
        )

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = create_session()
        user = session.get(User, user_id)
        session.delete(user)
        session.commit()
        return jsonify({"success": "OK"})


class UsersListResourse(Resource):
    def get(self):
        session = create_session()
        users = session.query(User).all()
        return jsonify(
            {
                "users": [
                    item.to_dict(rules=["-departments", "-jobs", "-hashed_password"])
                    for item in users
                ]
            }
        )

    def post(self):
        args = parser.parse_args()
        session = create_session()

        user = User()
        user.set_password(args["password"])
        user.surname = args["surname"]
        user.name = args["name"]
        user.age = args["age"]
        user.position = args["position"]
        user.speciality = args["speciality"]
        user.address = args["address"]
        user.email = args["email"]

        session.add(user)
        session.commit()

        return jsonify({"id": user.id})

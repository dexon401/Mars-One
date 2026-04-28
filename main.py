import datetime
import os

import requests
from flask import Flask, jsonify, make_response, redirect, render_template
from flask_login import LoginManager, login_required, login_user, logout_user
from flask_restful import Api

from data import db_session, jobs_api, user_api, users_resource
from data.jobs import Jobs
from data.users import User
from forms.job import NewJobForm
from forms.user import LoginForm, RegisterForm

GEOCODER_API_KEY = "8013b162-6b42-4997-9691-77b7074026e0"
STATIC_MAPS_API_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"

api = Api(app)
api.add_resource(users_resource.UsersListResourse, "/api/v2/users")
api.add_resource(users_resource.UsersResource, "/api/v2/users/<int:user_id>")


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not found"}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({"error": "Bad Request"}), 400)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    data = []
    for job in db_sess.query(Jobs).all():
        leader = db_sess.query(User).filter(User.id == job.team_leader).first()
        data.append((job, leader))
    return render_template("journal.html", data=data)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template(
                "register.html",
                title="Регистрация",
                form=form,
                message="Такой пользователь уже есть",
            )
        user = User()
        user.email = form.email.data
        user.set_password(form.password.data)
        user.surname = form.surname.data
        user.name = form.name.data
        user.age = form.age.data
        user.position = form.position.data
        user.speciality = form.speciality.data
        user.address = form.address.data
        user.modified_date = datetime.datetime.now()
        db_sess.add(user)
        db_sess.commit()
        return redirect("/")
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    db_sess = db_session.create_session()

    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template("login.html", message="Неправильный логин или пароль", form=form)
    return render_template("login.html", title="Авторизация", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/new_job", methods=["GET", "POST"])
def new_job():
    form = NewJobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs()
        job.job = form.job.data
        job.work_size = form.work_size.data
        job.team_leader = form.team_leader.data
        job.collaborators = form.collaborators.data
        job.start_date = form.start_date.data
        job.end_date = form.end_date.data
        job.is_finished = form.is_finished.data
        db_sess.add(job)

        db_sess.commit()
        return redirect("/")

    return render_template("new_job.html", title="Новая работа", form=form)


@app.route("/users_show/<int:user_id>")
def show_user(user_id):
    response = requests.get(f"http://127.0.0.1:5000/api/v2/users/{user_id}")
    user = response.json()["user"]
    if not response.ok:
        return user

    params = {
        "apikey": GEOCODER_API_KEY,
        "geocode": user["from_city"],
        "lang": "ru_RU",
        "format": "json",
    }
    response = requests.get("https://geocode-maps.yandex.ru/v1", params=params)
    response_json = response.json()
    envelope = response_json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["boundedBy"]["Envelope"]
    lon1, lat1 = map(float, envelope["lowerCorner"].split())
    lon2, lat2 = map(float, envelope["upperCorner"].split())

    spn_lon = abs(lon2 - lon1)
    spn_lat = abs(lat2 - lat1)

    hometown_coords = response_json["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"].split()

    params = {"apikey": STATIC_MAPS_API_KEY, "ll": f"{hometown_coords[0]},{hometown_coords[1]}", "spn": f"{spn_lon},{spn_lat}"}
    response = requests.get("https://static-maps.yandex.ru/v1", params=params)
    if response.ok:
        os.makedirs("static/img/", exist_ok=True)
        with open("static/img/image.png", "wb") as file:
            file.write(response.content)
    else:
        return response.reason

    kwargs = {
        "name": user.get("name"),
        "surname": user.get("surname"),
        "from_city": user.get("from_city"),
        "img_path": "/static/img/image.png",
    }
    return render_template("show_user.html", **kwargs)


def main():
    os.makedirs("db", exist_ok=True)
    db_session.global_init("db/mars_explorer.db")

    db_sess = db_session.create_session()

    if db_sess.query(User).count() == 0:
        user = User()
        user.surname = "Scott"
        user.name = "Ridley"
        user.age = 21
        user.position = "captain"
        user.speciality = "recearch engineer"
        user.address = "module_1"
        user.email = "scott_chief@mars.org"
        user.from_city = "Москва"
        db_sess.add(user)

        user2 = User()
        user2.surname = "Smith"
        user2.name = "John"
        user2.age = 25
        user2.position = "engineer"
        user2.speciality = "mechanical engineer"
        user2.address = "module_2"
        user2.email = "john_smith@mars.org"
        user2.from_city = "Санкт-Питербург"
        db_sess.add(user2)

        user3 = User()
        user3.surname = "Johnson"
        user3.name = "Jane"
        user3.age = 28
        user3.position = "scientist"
        user3.speciality = "biologist"
        user3.address = "module_3"
        user3.email = "jane_johnson@mars.org"
        user3.from_city = "Екатиренбург"
        db_sess.add(user3)

        user4 = User()
        user4.surname = "Brown"
        user4.name = "Bob"
        user4.age = 30
        user4.position = "pilot"
        user4.speciality = "aeronautics"
        user4.address = "module_4"
        user4.email = "bob_brown@mars.org"
        user4.from_city = "Красноярск"
        db_sess.add(user4)

    if db_sess.query(Jobs).count() == 0:
        job = Jobs()
        job.team_leader = 1
        job.job = "deployment of residential modules 1 and 2"
        job.work_size = 15
        job.collaborators = "2, 3"
        job.start_date = datetime.datetime.now()
        job.is_finished = False
        db_sess.add(job)

        job2 = Jobs()
        job2.team_leader = 2
        job2.job = "maintenance of module 3"
        job2.work_size = 10
        job2.collaborators = "1, 3"
        job2.start_date = datetime.datetime.now()
        job2.is_finished = True
        db_sess.add(job2)

    db_sess.commit()

    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(user_api.blueprint)

    app.run()


if __name__ == "__main__":
    main()

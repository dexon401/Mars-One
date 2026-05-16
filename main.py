import datetime
import os

import requests
from flask import Flask, jsonify, make_response, redirect, render_template, request
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_restful import Api

from data import db_session, jobs_api, jobs_resource, user_api, users_resource
from data.departments import Department as Department
from data.jobs import Jobs
from data.users import User
from data.hazard import Hazard, association_table
from forms.department import DelDepForm, NewDepForm
from forms.job import DelJobForm, NewJobForm
from forms.user import LoginForm, RegisterForm

GEOCODER_API_KEY = "8013b162-6b42-4997-9691-77b7074026e0"
STATIC_MAPS_API_KEY = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"

api = Api(app)
api.add_resource(users_resource.UsersListResourse, "/api/v2/users")
api.add_resource(users_resource.UsersResource, "/api/v2/users/<int:user_id>")
api.add_resource(jobs_resource.JobsListResource, "/api/v2/jobs")
api.add_resource(jobs_resource.JobsResource, "/api/v2/jobs/<int:job_id>")


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
        hazard = ', '.join([hazard.name for hazard in job.hazard])
        data.append((job, leader, hazard))
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
        return render_template(
            "login.html", message="Неправильный логин или пароль", form=form
        )
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

    return render_template(
        "new_job.html", title="Новая работа", header="New job", form=form
    )


@app.route("/edit_job/<int:job_id>", methods=["GET", "POST"])
def edit_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.get(Jobs, job_id)
    if not job:
        return make_response(jsonify({"error": "Not Found"}), 404)
    if not current_user.is_authenticated or not (
        current_user.id == 1 or current_user.id == job.team_leader
    ):
        return make_response(jsonify({"error": "Forbidden"}), 403)
    form = NewJobForm()
    if form.validate_on_submit():
        job.job = form.job.data
        job.work_size = form.work_size.data
        job.team_leader = form.team_leader.data
        job.collaborators = form.collaborators.data
        job.start_date = form.start_date.data
        job.end_date = form.end_date.data
        job.is_finished = form.is_finished.data
        db_sess.commit()
        return redirect("/")
    elif request.method == "GET":
        form.job.data = job.job
        form.work_size.data = job.work_size
        form.team_leader.data = job.team_leader
        form.collaborators.data = job.collaborators
        form.start_date.data = job.start_date.date() if job.start_date else None
        form.end_date.data = job.end_date.date() if job.end_date else None
        form.is_finished.data = job.is_finished
    return render_template(
        "new_job.html", title="Редактирование работы", header="Edit job", form=form
    )


@app.route("/delete_job/<int:job_id>", methods=["GET", "POST"])
def delete_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.get(Jobs, job_id)
    if not job:
        return make_response(jsonify({"error": "Not Found"}), 404)
    if not current_user.is_authenticated or not (
        current_user.id == 1 or current_user.id == job.team_leader
    ):
        return make_response(jsonify({"error": "Forbidden"}), 403)
    form = DelJobForm()
    if form.validate_on_submit():
        db_sess.delete(job)
        db_sess.commit()
        return redirect("/")
    return render_template("delete_job.html", title="Удаление работы", form=form)


@app.route("/departments")
def departments():
    db_sess = db_session.create_session()
    data = []
    for department in db_sess.query(Department).all():
        chief = db_sess.get(User, department.chief)
        data.append((department, chief))
    return render_template("departments.html", title="List of Departments", data=data)


@app.route("/new_department", methods=["GET", "POST"])
def new_department():
    form = NewDepForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        department = Department()
        department.title = form.title.data
        department.chief = form.chief.data
        department.members = form.members.data
        department.email = form.email.data
        db_sess.add(department)

        db_sess.commit()
        return redirect("/departments")

    return render_template(
        "new_department.html", title="Новый Депаратмент", header="New department", form=form
    )


@app.route("/edit_department/<int:department_id>", methods=["GET", "POST"])
def edit_department(department_id):
    db_sess = db_session.create_session()
    department = db_sess.get(Department, department_id)
    if not department:
        return make_response(jsonify({"error": "Not Found"}), 404)
    if not current_user.is_authenticated or not (
        current_user.id == 1 or current_user.id == department.chief
    ):
        return make_response(jsonify({"error": "Forbidden"}), 403)
    form = NewDepForm()
    if form.validate_on_submit():
        department.title = form.title.data
        department.chief = form.chief.data
        department.members = form.members.data
        department.email = form.email.data
        db_sess.commit()
        return redirect("/departments")
    elif request.method == "GET":
        form.title.data = department.title
        form.chief.data = department.chief
        form.members.data = department.members
        form.email.data = department.email
    return render_template(
        "new_department.html", title="Редактирование Департмента", header="Edit department", form=form
    )


@app.route("/delete_department/<int:department_id>", methods=["GET", "POST"])
def delete_department(department_id):
    db_sess = db_session.create_session()
    department = db_sess.get(Department, department_id)
    if not department:
        return make_response(jsonify({"error": "Not Found"}), 404)
    if not current_user.is_authenticated or not (
        current_user.id == 1 or current_user.id == department.chief
    ):
        return make_response(jsonify({"error": "Forbidden"}), 403)
    form = DelDepForm()
    if form.validate_on_submit():
        db_sess.delete(department)
        db_sess.commit()
        return redirect("/departments")
    return render_template("delete_department.html", title="Удаление Департмента", form=form)


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
    envelope = response_json["response"]["GeoObjectCollection"]["featureMember"][0][
        "GeoObject"
    ]["boundedBy"]["Envelope"]
    lon1, lat1 = map(float, envelope["lowerCorner"].split())
    lon2, lat2 = map(float, envelope["upperCorner"].split())

    spn_lon = abs(lon2 - lon1)
    spn_lat = abs(lat2 - lat1)

    hometown_coords = response_json["response"]["GeoObjectCollection"]["featureMember"][
        0
    ]["GeoObject"]["Point"]["pos"].split()

    params = {
        "apikey": STATIC_MAPS_API_KEY,
        "ll": f"{hometown_coords[0]},{hometown_coords[1]}",
        "spn": f"{spn_lon},{spn_lat}",
    }
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
    
    if db_sess.query(Hazard).count() == 0:
        haz = Hazard()
        haz.name = "1"
        db_sess.add(haz)
        haz = Hazard()
        haz.name = "2"
        db_sess.add(haz)
        haz = Hazard()
        haz.name = "3"
        db_sess.add(haz)

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
        user.set_password("admin")
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
        job.end_date = datetime.datetime.now() + datetime.timedelta(days=10)
        job.is_finished = False
        job.hazard.append(db_sess.get(Hazard, 1))
        db_sess.add(job)

        job2 = Jobs()
        job2.team_leader = 2
        job2.job = "maintenance of module 3"
        job2.work_size = 10
        job2.collaborators = "1, 3"
        job2.start_date = datetime.datetime.now()
        job2.end_date = datetime.datetime.now() + datetime.timedelta(days=10)
        job2.is_finished = True
        job2.hazard.append(db_sess.get(Hazard, 2))
        db_sess.add(job2)

    if db_sess.query(Department).count() == 0:
        dept1 = Department()
        dept1.title = "Engineering"
        dept1.chief = 1
        dept1.members = "1, 2, 3"
        dept1.email = "engineering@mars.com"
        db_sess.add(dept1)

        dept2 = Department()
        dept2.title = "Human Resources"
        dept2.chief = 2
        dept2.members = "2, 4"
        dept2.email = "hr@mars.com"
        db_sess.add(dept2)

    db_sess.commit()

    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(user_api.blueprint)

    app.run()


if __name__ == "__main__":
    main()

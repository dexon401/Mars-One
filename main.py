import datetime
from flask import Flask, render_template, redirect, request, make_response
from flask_login import LoginManager
from forms.user import RegisterForm
from data import db_session
from data.users import User
from data.jobs import Jobs

app = Flask(__name__)
app.config["SECRET_KEY"] = "yandexlyceum_secret_key"


def main():
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
        db_sess.add(user)

        user2 = User()
        user2.surname = "Smith"
        user2.name = "John"
        user2.age = 25
        user2.position = "engineer"
        user2.speciality = "mechanical engineer"
        user2.address = "module_2"
        user2.email = "john_smith@mars.org"
        db_sess.add(user2)

        user3 = User()
        user3.surname = "Johnson"
        user3.name = "Jane"
        user3.age = 28
        user3.position = "scientist"
        user3.speciality = "biologist"
        user3.address = "module_3"
        user3.email = "jane_johnson@mars.org"
        db_sess.add(user3)

        user4 = User()
        user4.surname = "Brown"
        user4.name = "Bob"
        user4.age = 30
        user4.position = "pilot"
        user4.speciality = "aeronautics"
        user4.address = "module_4"
        user4.email = "bob_brown@mars.org"
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

    app.run()


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


@app.route("/cookie_test")
def cookie_test():
    visits_count = int(request.cookies.get("visits_count", 0))
    if visits_count:
        res = make_response(f"Вы пришли на эту страницу {visits_count + 1} раз")
        res.set_cookie(
            "visits_count", str(visits_count + 1), max_age=60 * 60 * 24 * 365 * 2
        )
    else:
        res = make_response(
            "Вы пришли на эту страницу в первый раз за последние 2 года"
        )
        res.set_cookie("visits_count", "1", max_age=60 * 60 * 24 * 365 * 2)
    return res


if __name__ == "__main__":
    main()

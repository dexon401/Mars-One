from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms import validators


class RegisterForm(FlaskForm):
    email = StringField("Email", [validators.DataRequired()])
    password = PasswordField(
        "Password",
        [
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Passwords should match"),
        ],
    )
    confirm = PasswordField("Repeat Password")
    surname = StringField("Surname")
    name = StringField("Name")
    age = IntegerField("Age")
    position = StringField("Position")
    speciality = StringField("Speciality")
    address = StringField("Address")
    submit = SubmitField("Submit")

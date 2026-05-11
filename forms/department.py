from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    StringField,
    SubmitField,
)


class NewDepForm(FlaskForm):
    title = StringField("Title of department")
    chief = IntegerField("ID of the chief")
    members = StringField("IDs of members (<id1>, <id2>, ...)")
    email = StringField("Department Email")
    submit = SubmitField("Submit")


class DelDepForm(FlaskForm):
    submit = SubmitField("DELETE DEPARTMENT")

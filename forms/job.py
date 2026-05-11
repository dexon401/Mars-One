from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    IntegerField,
    StringField,
    SubmitField,
    TextAreaField,
)


class NewJobForm(FlaskForm):
    job = TextAreaField("Job description")
    work_size = IntegerField("The duration of work (in hours)")
    team_leader = IntegerField("ID of the team leader")
    collaborators = StringField("IDs of collaborators (<id1>, <id2>, ...)")
    start_date = DateField("Date of work start")
    end_date = DateField("Date of work finish")
    is_finished = BooleanField("Is job finished?")
    submit = SubmitField("Submit")

class DelJobForm(FlaskForm):
    submit = SubmitField("DELETE JOB")
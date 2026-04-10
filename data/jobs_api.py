import flask

from . import db_session
from .jobs import Jobs

blueprint = flask.Blueprint("jobs_api", __name__, template_folder="templates")


@blueprint.route("/api/jobs")
def get_jobs():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return flask.jsonify([item.to_dict(rules=("-user",)) for item in jobs])


@blueprint.route("/api/jobs/<int:job_id>")
def get_job(job_id):
    db_sess = db_session.create_session()
    job = db_sess.get(Jobs, job_id)
    if job:
        return flask.jsonify(job.to_dict(rules=("-user",)))
    return "Job not found"
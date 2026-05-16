import sqlalchemy

from .db_session import SqlAlchemyBase

association_table = sqlalchemy.Table(
    "association",
    SqlAlchemyBase.metadata,
    sqlalchemy.Column("job_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("jobs.id")),
    sqlalchemy.Column("hazard_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("hazard.id")),
)


class Hazard(SqlAlchemyBase):
    __tablename__ = "hazard"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)

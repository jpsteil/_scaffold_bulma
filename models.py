"""
This file defines the database models
"""

from .common import db, Field
from pydal.validators import *

### Define your table below
db.define_table(
    "speaker",
    Field("first_name", length=20),
    Field("last_name", length=20),
    Field("company", length=100),
    Field("title", length=100),
    Field("bio", "text"),
)

db.define_table("room", Field("name", length=100))

db.define_table(
    "session",
    Field("start_time", "datetime", requires=IS_DATETIME()),
    Field("name", length=100),
    Field("description", "text"),
    Field(
        "speaker",
        "reference speaker",
        requires=IS_IN_DB(db, "speaker.id", "%(first_name)s %(last_name)s"),
    ),
    Field("room", "reference room", requires=IS_IN_DB(db, "room.id", "%(name)s")),
)
db.commit()

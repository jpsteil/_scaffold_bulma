from apps.wmcpa_live_demo.lib.grid_helpers import GridSearch, GridSearchQuery
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A, XML
from pydal.validators import IS_NULL_OR, IS_IN_DB
from py4web.utils.form import FormStyleBulma

from py4web.utils.grid import Column, Grid, GridClassStyleBulma
from .common import (
    db,
    T,
    session,
    auth,
)


@action("index")
@action.uses("index.html", auth, T)
def index():
    user = auth.get_user()
    message = T("Hello {first_name}".format(**user) if user else "Hello")
    actions = {"allowed_actions": auth.param.allowed_actions}
    return dict(message=message, actions=actions)


@action("rooms", method=["GET", "POST"])
@action("rooms/<path:path>", method=["GET", "POST"])
@action.uses("grid.html", auth, db, session)
def rooms(path=None):
    grid = Grid(
        path,
        db.room,
        formstyle=FormStyleBulma,
        search_queries=[["name", lambda value: db.room.name.contains(value)]],
        orderby=db.room.name,
        grid_class_style=GridClassStyleBulma,
        rows_per_page=10,
        details=False,
    )

    return dict(grid=grid)


@action("speakers", method=["GET", "POST"])
@action("speakers/<path:path>", method=["GET", "POST"])
@action.uses("grid.html", auth, db, session)
def speakers(path=None):
    columns = [
        Column(
            "name",
            lambda r: XML(
                f'{r.first_name} {r.last_name}<div style="font-size: smaller;">{r.company}</div>'
            ),
            orderby=db.speaker.last_name,
        ),
        db.speaker.title,
    ]
    search_queries = [
        ["Company", lambda value: db.speaker.company.contains(value)],
        ["Title", lambda value: db.speaker.title.contains(value)],
    ]
    grid = Grid(
        path,
        db.speaker,
        columns=columns,
        formstyle=FormStyleBulma,
        search_queries=search_queries,
        grid_class_style=GridClassStyleBulma,
        orderby=db.speaker.last_name,
        rows_per_page=10,
        details=False,
    )

    return dict(grid=grid)


@action("sessions", method=["GET", "POST"])
@action("sessions/<path:path>", method=["GET", "POST"])
@action.uses("grid.html", auth, db, session)
def sessions(path=None):
    search_queries = [
        GridSearchQuery(
            "filter by room",
            lambda value: db.session.room == value,
            requires=IS_NULL_OR(IS_IN_DB(db, "room.id", "%(name)s")),
        ),
        GridSearchQuery(
            "filter by speaker",
            lambda value: db.session.speaker == value,
            requires=IS_NULL_OR(
                IS_IN_DB(db, "speaker.id", "%(first_name)s %(last_name)s")
            ),
        ),
        GridSearchQuery(
            "filter by text",
            lambda value: db.session.name.contains(value)
            | db.session.description.contains(value),
        ),
    ]

    search = GridSearch(search_queries=search_queries, queries=[db.session.id > 0])
    columns = [
        db.session.start_time,
        db.session.name,
        Column(
            "speaker",
            lambda r: XML(f"{r.speaker.first_name} {r.speaker.last_name}"),
            orderby=db.speaker.last_name,
            required_fields=[db.speaker.first_name, db.speaker.last_name],
        ),
        Column(
            "room",
            lambda r: r.room.name,
            orderby=db.room.name,
            required_fields=[db.room.name],
        ),
    ]
    left = [
        db.speaker.on(db.session.speaker == db.speaker.id),
        db.room.on(db.session.room == db.room.id),
    ]
    grid = Grid(
        path,
        query=search.query,
        columns=columns,
        field_id=db.session.id,
        search_form=search.search_form,
        formstyle=FormStyleBulma,
        grid_class_style=GridClassStyleBulma,
        orderby=db.session.start_time,
        rows_per_page=10,
        details=False,
        left=left,
    )

    return dict(grid=grid)

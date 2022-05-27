"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
import time

from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.grid import Grid, GridClassStyleBulma


from .models import OLIVE_KINDS

url_signer = URLSigner(session)

class GridEditButton(object):
    """This is the edit button for the grid."""
    def __init__(self):
        self.url = URL('edit')
        self.append_id = True # append the ID to the edit.
        self.additional_classes = 'button'
        self.icon = 'fa-pencil'
        self.text = 'Edit'
        self.message = None
        self.onclick = None # Used for things like confirmation.

@action('index', method=['POST', 'GET']) # /fixtures_example/index
@action('index/<path:path>', method=['POST', 'GET']) # /fixtures_example/index
@action.uses('index.html', db, auth.user)
def index(path=None):
    grid = Grid(
        path,
        query=db.classes.id > 0,
        search_queries=None, search_form=None,
        editable=False, deletable=False, details=False, create=False,
        grid_class_style=GridClassStyleBulma,
        formstyle=FormStyleBulma,
        post_action_buttons=[GridEditButton()],
    )
    grid.formatters = {'olives.olive_kind': lambda v : OLIVE_KINDS.get(v)}
    return dict(grid=grid)


def validate_form_weights(form):
    return
    """Checks that the gross weight is larger than the net weight."""
    if form.vars['weight_net'] > form.vars['weight_tot']:
        form.errors['weight_tot'] = T('The gross weight should be more than the net.')

@action('add', method=["GET", "POST"])
@action.uses('add.html', db, session, auth.user)
def add():
    form = Form(db.classes, validation=validate_form_weights,
                csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        redirect(URL('index'))
    return dict(form=form)

# @action('edit/<olives_id:int>', method=["GET", "POST"])
# @action.uses('edit.html', db, session, auth.user)
# def edit(olives_id=None):
#     p = db.olives[olives_id]
#     if p is None:
#         redirect(URL('index'))
#     form = Form(db.olives, record=p, deletable=False,
#                 validation=validate_form_weights,
#                 csrf_session=session, formstyle=FormStyleBulma)
#     if form.accepted:
#         redirect(URL('index'))
#     return dict(form=form)

@action('edit_class', method="POST")
@action.uses(url_signer.verify(), db)
def edit_contact():
    id = request.json.get('id')
    field = request.json.get('field')
    value = request.json.get('value')
    db(db.classes.id == id).update(**{field: value})
    time.sleep(1)
    return "ok"

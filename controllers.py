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

from py4web import action, request, abort, redirect, URL, Field
from pydal.validators import IS_NOT_EMPTY, IS_IN_SET
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email, get_user_name
import time
from .courses import *

from py4web.utils.form import Form, FormStyleBulma, RadioWidget
from py4web.utils.grid import Grid, GridClassStyleBulma


from .models import OLIVE_KINDS

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', url_signer)
def index():
    if len(db(db.admin).select().as_list()) == 0 and get_user_email() != None:
        db.admin.insert(email = get_user_email(), name = get_user_name(), permission = "admin")
    perm = db(db.admin.email == get_user_email()).select().as_list()
    active_tables = db(db.planners.status == True).select().as_list()
    inactive_tables = db(db.planners.status == False).select().as_list()
    # print(perm[0])
    user_name = None
    user_perm = None
    print(perm)
    if len(perm) != 0:
        user_name = perm[0]["name"]
        user_perm = perm[0]["permission"]

    return dict(
        # This is the signed URL for the callback.
        user_name = user_name,
        user_perm = user_perm,
        user_email = get_user_email(),
        active_tables = active_tables,
        inactive_tables = inactive_tables
    )

@action('add_table', method=["GET","POST"])
@action.uses('add_table.html', url_signer)
def add_table():
    if len(db(db.admin.email == get_user_email()).select().as_list()) == 0:
        return dict(error = True)
    form = Form(db.planners, deletable=False, formstyle=FormStyleBulma)
    # FormStyleBulma.widgets['Populate_with_default_class_data']=RadioWidget()
    # FormStyleBulma.widgets['Populate_with_default_instructor_data']=RadioWidget()
    form = Form([Field('Table_Name', requires=IS_NOT_EMPTY()), 
        Field('Populate_with_default_class_data', requires=IS_IN_SET(['Yes','No'])),
        Field('Populate_with_default_instructor_data', requires=IS_IN_SET(['Yes','No']))], csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # The update already happened!
        db.planners.insert(name = form.vars['Table_Name'], status = True, class_num = 142, instruct_num = 100)
        redirect(URL('index'))
    return dict(
        # This is the signed URL for the callback.
        error = False,
        form = form
    )

@action('init_table', method=["GET","POST"])
@action.uses('init_table.html', url_signer)
def init_table():
    print(courses)
    redirect(URL('add_table'))
    return dict(
        # This is the signed URL for the callback.
        error = False,
        form = form
    )

@action('table/<table_id:int>')
@action.uses('table.html', url_signer)
def table(table_id = None):
    planner = db(db.planners.id == table_id).select().as_list()[0]

    # instructors = db(db.users.name == get_user_name()).select().as_list()
    # for instructor in instructors:
    #     instructor['classes'] = ''
    #     s = db(db.classes.contact_id == instructor['id']).select()

    return dict(
        # This is the signed URL for the callback.
        planner = planner,
        # instructors = instructors,
        load_classes_url = URL('load_classes', table_id, signer=url_signer),
        add_class_url = URL('add_class', table_id, signer=url_signer),
        delete_class_url = URL('delete_class', signer=url_signer),
        edit_class_url = URL('edit_class', signer=url_signer),
    )

@action('archive/<table_id:int>')
@action.uses('archive.html', url_signer)
def archive(table_id = None):
    db(db.planners.id == table_id).update(status = False)
    redirect(URL('index'))

@action('unarchive/<table_id:int>')
@action.uses('unarchive.html', url_signer)
def unarchive(table_id = None):
    db(db.planners.id == table_id).update(status = True)
    redirect(URL('index'))

# This is our very first API function.
@action('load_classes/<table_id:int>')
@action.uses(url_signer.verify(), db)
def load_classes(table_id = None):
    rows = db(db.classes.planner_id == table_id).select().as_list()
    return dict(rows=rows)

@action('add_class/<table_id:int>', method="POST")
@action.uses(url_signer.verify(), db)
def add_class(table_id = None):
    print(request.json)
    id = db.classes.insert(
        class_name=request.json.get('class_name'),
        class_type=request.json.get('class_type'),
        planner_id = table_id
    )
    return dict(id=id)

@action('delete_class')
@action.uses(url_signer.verify(), db)
def delete_class():
    id = request.params.get('id')
    assert id is not None
    db(db.classes.id == id).delete()
    return "ok"

@action('edit_class', method="POST")
@action.uses(url_signer.verify(), db)
def edit_class():
    id = request.json.get('id')
    field = request.json.get('field')
    value = request.json.get('value')
    db(db.classes.id == id).update(**{field: value})
    time.sleep(1)
    return "ok"

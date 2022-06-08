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

from sqlite3 import Row
from unicodedata import name
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
        db.admin.insert(email = get_user_email(), name = get_user_name(), permission = "admin", true_permission = "admin")
    perm = db(db.admin.email == get_user_email()).select().as_list()
    active_tables = db(db.planners.status == True).select().as_list()
    inactive_tables = db(db.planners.status == False).select().as_list()
    # print(perm[0])
    user_name = None
    user_perm = None
    user_true_perm = None
    print(perm)
    if len(perm) != 0:
        user_name = perm[0]["name"]
        user_perm = perm[0]["permission"]
        user_true_perm = perm[0]["true_permission"]
    else:
        db.admin.insert(name=get_user_name(), email=get_user_email(), permission = "manager", true_permission = "manager")
        perm = db(db.admin.email == get_user_email()).select().as_list()
        user_name = perm[0]["name"]
        user_perm = perm[0]["permission"]
        user_true_perm = perm[0]["true_permission"]
    if user_true_perm == "admin" or user_true_perm == "manager":
        view_all = db(db.admin.email == get_user_email()).select().as_list()[0]['view_all']
        user_assignment = db(db.instructors.email == get_user_email()).select().as_list()
        all_assignment = []
        print(view_all)
        if view_all == 'True':
            all_assignment = db(db.instructors).select("planner_id").as_list()
        else:
            all_assignment = db(db.instructors.email ==  get_user_email()).select("planner_id").as_list()
        asgn_list = []
        for i in all_assignment:
            asgn_list.append(int(i['_extra']['planner_id']))
        asgn_list = list(set(asgn_list))
        print(asgn_list)
        planners = db(db.planners.id).select().as_list()
        active_all = []
        inactive_all = []
        for i in planners:
            if i['id'] in asgn_list:
                if i['status'] == 'True':
                    active_all.append(i)
                else:
                    inactive_all.append(i)

        print(active_all, inactive_all)
    else:
        view_all = False
        active_all = []
        inactive_all=[]
        user_assignment = []
        all_assignment = []

    return dict(
        # This is the signed URL for the callback.
        user_name = user_name,
        user_perm = user_perm,
        true_perm = user_true_perm,
        user_email = get_user_email(),
        active_tables = active_tables,
        inactive_tables = inactive_tables,
        active_all = active_all,
        inactive_all = inactive_all,
        view_all = view_all,
        url_signer = url_signer
    )

@action('add_table', method=["GET","POST"])
@action.uses('add_table.html', url_signer.verify())
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
        
        if form.vars['Populate_with_default_class_data'] == 'Yes':
            planner_id = db.planners.insert(name = form.vars['Table_Name'], status = True, class_num = len(courses), instruct_num = 100)
            for course in courses:
                print(course)
                db.classes.insert(class_name = course['class_name'], 
                    class_type = course['class_name'].split(" ")[0], 
                    class_num = course['class_name'].split(" ")[1],
                    class_sub = course['class_subtitle'], 
                    class_desc = course['class_description'], 
                    href = course['href'],
                    default_inst = course['class_instructor'].split(", "),
                    default_quarters = course['class_quarters'].split(", "),
                    planner_id = planner_id
                    )
        else:
            db.planners.insert(name = form.vars['Table_Name'], status = True, class_num = 0, instruct_num = 0)


        if form.vars['Populate_with_default_instructor_data'] == 'Yes':
            # planner_id = db.planners.insert(name = form.vars['Table_Name'], status = True, class_num = len(courses), instruct_num = 100)
            for course in courses:
                # print(course)
                db.instructors.insert(name = course['class_instructor'],
                    planner_id = planner_id
                    )

        redirect(URL('index'))
    return dict(
        # This is the signed URL for the callback.
        error = False,
        form = form
    )


@action('add_admin', method=["GET","POST"])
@action.uses('add_admin.html', url_signer.verify())
def add_admin():
    if len(db(db.admin.email == get_user_email()).select().as_list()) == 0:
        return dict(error = True)
    form = Form(db.planners, deletable=False, formstyle=FormStyleBulma)
    # FormStyleBulma.widgets['Populate_with_default_class_data']=RadioWidget()
    # FormStyleBulma.widgets['Populate_with_default_instructor_data']=RadioWidget()
    form = Form([Field('User_Email', requires=IS_NOT_EMPTY())], csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted:
        # The update already happened!
        db.admin.update_or_insert(db.admin.email == form.vars['User_Email'], email = form.vars['User_Email'], true_permission = 'admin')

        redirect(URL('index'))
    return dict(
        # This is the signed URL for the callback.
        error = False,
        form = form
    )
@action('assignments/<planner_id>/<perm>', method=["GET","POST"])
@action.uses('assignments.html', url_signer)
def assignments(planner_id, perm):
    view_all = db(db.admin.email == get_user_email()).select().as_list()[0]['view_all']
    assignments = []
    
    if view_all == 'True':
        assignments = db((db.instructors.planner_id == planner_id)).select().as_list()
    else:
        assignments = db((db.instructors.planner_id == planner_id) & (db.instructors.email == get_user_email())).select().as_list()
    print(assignments)

    return dict(assignments = assignments)

@action('change_view_all', method=["GET","POST"])
@action.uses('change_view_all.html', url_signer.verify())
def change_view_all():
    view_all_i = db(db.admin.email == get_user_email()).select().as_list()[0]['view_all']
    db(db.admin.email == get_user_email()).update(view_all = False if view_all_i == "True" else True)
    redirect(URL('index'))
    return

@action('change_perm/<perm>', method=["GET","POST"])
@action.uses('change_perm.html', url_signer.verify())
def change_perm(perm = "instructor"):
    db(db.admin.email == get_user_email()).update(permission = perm)
    redirect(URL('index'))
    return

@action('table/<table_id:int>')
@action.uses('table.html', url_signer.verify())
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
        load_instructors_url = URL('load_instructors', table_id, signer=url_signer),
        add_class_url = URL('add_class', table_id, signer=url_signer),
        add_instructors_url = URL('add_instructor', table_id, signer=url_signer),
        delete_class_url = URL('delete_class', signer=url_signer),
        edit_class_url = URL('edit_class', signer=url_signer),
        edit_classes_url = URL('edit_classes', signer=url_signer),
        edit_instructor_url = URL('edit_instructor', signer=url_signer),
        update_tables_url = URL('update_tables', table_id, None, signer=url_signer),
        # archive_url = URL('archive', table_id, signer=url_signer)
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

@action('load_instructors/<table_id:int>')
@action.uses(url_signer.verify(), db)
def load_instructors(table_id = None):
    rows = db(db.instructors.planner_id == table_id).select().as_list()
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

@action('add_instructor/<table_id:int>', method="POST")
@action.uses(url_signer.verify(), db)
def add_instructor(table_id = None):
    print("REQUEST",request.json)
    id = db.instructors.insert(
        email=request.json.get('email'),
        name=request.json.get('name'),
        planner_id = table_id
    )
    print(id, table_id)
    return dict(id=id)

# def parse_instr_classlist(class_list):
#     class_list = class_list.split(', ')

#     return class_list

@action('edit_class', method="POST")
@action.uses(url_signer.verify(), db)
def edit_class():
    # update class table
    id = request.json.get('id')
    field = request.json.get('field')  # quarter
    value = request.json.get('value')  # instr name
    db(db.classes.id == id).update(**{field: value})   

    # update instructor table
    instructor_name = db(db.classes.id == id).select().as_list()[0][field]
    instructor_entry = db(db.instructors.name == value).select().as_list()
    quarter = instructor_entry[0][field]
    class_name = db(db.classes.id == id).select().as_list()[0]['class_name']
    if quarter is None:
        db(db.instructors.name == value).update(**{field: class_name})
    else:
        class_list = quarter.split(', ')
        if class_name not in class_list:
            class_list.append(class_name)
            class_list = '%s' % ', '.join(map(str, class_list))
            db(db.instructors.name == value).update(**{field: class_list})

    time.sleep(1)
    return "ok"

@action('delete_class')
@action.uses(url_signer.verify(), db)
def delete_class():
    id = request.params.get('id')
    assert id is not None
    db(db.classes.id == id).delete()
    return "ok"


@action('update_tables/<planner_id:int>/<changes_list>', method=["GET","POST"])
@action.uses(url_signer.verify(), db)
def update_tables(planner_id, changes_list):
    print(changes_list)
    if changes_list == 'None':
        changes_list = request.json.get('changes_list').values()
    # print(changes_list)
    for change in list(changes_list):
        # CHANGE TO CLASSES TAB
        print('HERE', change)
        if change['table'] == 'classes':
            # update class table
            print("in classes")

            class_entry = db((db.classes.id == change['row']['id']) & (db.classes.planner_id == planner_id)).select().as_list()
            
            prev_db = db((db.classes.id == change['row']['id']) & (db.classes.planner_id == planner_id)).select().as_list()[0]
            db((db.classes.id == change['row']['id'])& (db.classes.planner_id == planner_id)).update(
                class_name = change['row']['class_name'],
                class_type = change['row']['class_type'],
                quarter_1 = change['row']['quarter_1'],
                quarter_2 = change['row']['quarter_2'],
                quarter_3 = change['row']['quarter_3'],
                summer_1 = change['row']['summer_1'],
                summer_2 = change['row']['summer_2'],
                course_time_sections = change['row']['course_time_sections'],
                actual_times = change['row']['actual_times'],

                )
            new_db = db((db.classes.id == change['row']['id']) & (db.classes.planner_id == planner_id)).select().as_list()[0]           
            for quarter in ['quarter_1', 'quarter_2', 'quarter_3', 'summer_1', 'summer_2']:
                if prev_db[quarter] == new_db[quarter]:
                    continue
                
                   
                class_query = db((db.instructors.name == new_db[quarter])& (db.instructors.planner_id == planner_id)).select().as_list()
                if len(class_query) == 0:
                    continue
                class_query = class_query[0]
                print(class_query,  new_db[quarter])
                if quarter == 'quarter_1':
                    db(db.instructors.id == class_query['id']).update(quarter_1_1 = new_db['class_name'])
                    class_query = db((db.instructors.name == new_db[quarter])& (db.instructors.planner_id == planner_id)).select().as_list()[0]
                    update_str = class_query[quarter+'_1']
                    for i in range(2,7):
                        st = class_query[quarter+'_'+str(i)]
                        if st is not None and st is not "":
                            update_str+=', '+st
                    db(db.instructors.id == class_query['id']).update(quarter_1 = update_str)
                elif quarter == 'quarter_2':
                    db(db.instructors.id == class_query['id']).update(quarter_2_1 = new_db['class_name'])
                    class_query = db((db.instructors.name == new_db[quarter])& (db.instructors.planner_id == planner_id)).select().as_list()[0]
                    update_str = class_query[quarter+'_1']
                    for i in range(2,7):
                        st = class_query[quarter+'_'+str(i)]
                        if st is not None and st is not "":
                            update_str+=', '+st
                    db(db.instructors.id == class_query['id']).update(quarter_2 = update_str)
                elif quarter == 'quarter_3':
                    db(db.instructors.id == class_query['id']).update(quarter_3_1 = new_db['class_name'])
                    class_query = db((db.instructors.name == new_db[quarter])& (db.instructors.planner_id == planner_id)).select().as_list()[0]
                    update_str = class_query[quarter+'_1']
                    for i in range(2,7):
                        st = class_query[quarter+'_'+str(i)]
                        if st is not None and st is not "":
                            update_str+=', '+st
                    db(db.instructors.id == class_query['id']).update(quarter_3 = update_str)
                elif quarter == 'summer_1':
                    db(db.instructors.id == class_query['id']).update(summer_1_1 = new_db['class_name'])
                    class_query = db((db.instructors.name == new_db[quarter])& (db.instructors.planner_id == planner_id)).select().as_list()[0]
                    update_str = class_query[quarter+'_1']
                    for i in range(2,7):
                        st = class_query[quarter+'_'+str(i)]
                        if st is not None and st is not "":
                            update_str+=', '+st
                    db(db.instructors.id == class_query['id']).update(summer_1 = update_str)
                elif quarter == 'summer_2':
                    db(db.instructors.id == class_query['id']).update(summer_2_1 = new_db['class_name'])
                    class_query = db((db.instructors.name == new_db[quarter])& (db.instructors.planner_id == planner_id)).select().as_list()[0]
                    update_str = class_query[quarter+'_1']
                    for i in range(2,7):
                        st = class_query[quarter+'_'+str(i)]
                        if st is not None and st is not "":
                            update_str+=', '+st
                    db(db.instructors.id == class_query['id']).update(summer_2 = update_str)
        # CHANGE TO INSTRUCTORS TAB
        elif change['table'] == 'instr':
            # update instr
            instructor_entry = db((db.instructors.id == change['row']['id']) & (db.instructors.planner_id == planner_id)).select().as_list()

            prev_db = db((db.instructors.id == change['row']['id']) & (db.instructors.planner_id == planner_id)).select().as_list()[0]
            db((db.instructors.id == change['row']['id'])& (db.instructors.planner_id == planner_id)).update(name = change['row']['name'],
                email = change['row']['email'],
                quarter_1 = change['row']['quarter_1'],
                quarter_1_1 = change['row']['quarter_1_1'],
                quarter_1_2 = change['row']['quarter_1_2'],
                quarter_1_3 = change['row']['quarter_1_3'],
                quarter_1_4 = change['row']['quarter_1_4'],
                quarter_1_5 = change['row']['quarter_1_5'],
                quarter_1_6 = change['row']['quarter_1_6'],

                quarter_2 = change['row']['quarter_2'],
                quarter_2_1 = change['row']['quarter_2_1'],
                quarter_2_2 = change['row']['quarter_2_2'],
                quarter_2_3 = change['row']['quarter_2_3'],
                quarter_2_4 = change['row']['quarter_2_4'],
                quarter_2_5 = change['row']['quarter_2_5'],
                quarter_2_6 = change['row']['quarter_2_6'],

                quarter_3 = change['row']['quarter_3'],
                quarter_3_1 = change['row']['quarter_3_1'],
                quarter_3_2 = change['row']['quarter_3_2'],
                quarter_3_3 = change['row']['quarter_3_3'],
                quarter_3_4 = change['row']['quarter_3_4'],
                quarter_3_5 = change['row']['quarter_3_5'],
                quarter_3_6 = change['row']['quarter_3_6'],

                summer_1 = change['row']['summer_1'],
                summer_1_1 = change['row']['summer_1_1'],
                summer_1_2 = change['row']['summer_1_2'],
                summer_1_3 = change['row']['summer_1_3'],
                summer_1_4 = change['row']['summer_1_4'],
                summer_1_5 = change['row']['summer_1_5'],
                summer_1_6 = change['row']['summer_1_6'],

                summer_2 = change['row']['summer_2'],
                summer_2_1 = change['row']['summer_2_1'],
                summer_2_2 = change['row']['summer_2_2'],
                summer_2_3 = change['row']['summer_2_3'],
                summer_2_4 = change['row']['summer_2_4'],
                summer_2_5 = change['row']['summer_2_5'],
                summer_2_6 = change['row']['summer_2_6'],
                )
            new_db = db((db.instructors.id == change['row']['id']) & (db.instructors.planner_id == planner_id)).select().as_list()[0]
            
            new_changes = {}
            classes_changed = []
            for quarter in ['quarter_1', 'quarter_2', 'quarter_3', 'summer_1', 'summer_2']:
                if prev_db[quarter] == new_db[quarter]:
                    continue
                for section in range(1,7): # probably shouldnt use magic numbers here
                    if prev_db[quarter+'_'+str(section)] == new_db[quarter+'_'+str(section)]:
                        continue
                    else:
                        class_query = db((db.classes.class_name == new_db[quarter+'_'+str(section)])& (db.classes.planner_id == planner_id)).select().as_list()
                        if len(class_query) == 0:
                            continue
                        class_query = class_query[0]
                        # print(class_query)
                        if quarter == 'quarter_1':
                            db(db.classes.id == class_query['id']).update(quarter_1 = new_db['name'])
                        elif quarter == 'quarter_2':
                            db(db.classes.id == class_query['id']).update(quarter_2 = new_db['name'])
                        elif quarter == 'quarter_3':
                            db(db.classes.id == class_query['id']).update(quarter_3 = new_db['name'])
                        elif quarter == 'summer_1':
                            db(db.classes.id == class_query['id']).update(summer_1 = new_db['name'])
                        elif quarter == 'summer_2':
                            db(db.classes.id == class_query['id']).update(summer_2 = new_db['name'])
    redirect(URL('table', planner_id, signer=url_signer))
    time.sleep(1)
    

@action('search')
@action.uses()
def search():
   # q = request.params.get("q")
   # results = [q + ":" + str(uuid.uuid1()) for _ in range(random.randint(2, 6))]
    results = [db.classes]
    return dict(results=results)

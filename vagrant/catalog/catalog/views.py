from datetime import datetime
from random import randint
import random, string
import json
import os

from flask import (
    render_template,
    url_for,
    request,
    redirect,
    flash,
    jsonify,
    make_response,
    Response
)
from sqlalchemy import desc
from werkzeug import secure_filename

from database import session, Base
from models import (
    Category,
    Item,
    User
)

from .auth import (
    CLIENT_ID,
    isActiveSession,
    getLoginSessionState,
    ConnectGoogle,
    DisconnectGoogle,
    canAlter,
    getSessionUserID
)

from urls import Urls
from . import app

# From flask docs, checks that uploaded images have specific file extensions
# http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
def allowed_image(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


# Process an uploaded image.  If it's a valid file type, then save the file
# and return the local url.
def processImageUpload(image):

    # Valid object and extension
    if image and allowed_image(image.filename):
        # Scrub filename
        filename = secure_filename(image.filename)

        # Save the file to the App's Images directory.
        image.save(os.path.join(app.config['APP_IMAGES'], filename))

        # Return the local url for the image.
        return os.path.join("images", filename)


# TODO
# Flash html element needs to be sized properly for when a user logs in.
# Add Latest Items View DONE - sort of, category names needed and "latest items"
# Add Categories Sidebar DONE
# Add JSON endpoint for entire Catalog DONE
# Add XML endpoint (optional)


# http://flask.pocoo.org/docs/0.10/templating/#context-processors
# Allow templates to generate Urls for different Models
@app.context_processor
def makeurls_processor():
    def makeUrls(suffix, key=0):
        return Urls(suffix, key)
    return dict(makeUrls=makeUrls)


@app.context_processor
def hasattr_processor():
    return dict(hasattr=hasattr)


# Checks for a valid session
@app.context_processor
def isactivesession_processor():
    return dict(isActiveSession=isActiveSession)


# Allow Templates to determine if a user can edit/delete a record
@app.context_processor
def canalter_processor():
    return dict(canAlter=canAlter)


# Returns the plural form of a word.
# In this app it turns item and user into items, users.
# and category into categories.  Allows for generic templates.
@app.context_processor
def getplural_processor():
    def getPlural(singular):
        if singular.lower() == 'category':
            return 'Categories'

        else:
            return singular.title() + "s"
    return dict(getPlural=getPlural)


@app.context_processor
def getcategories_processor():
    def getCategoryNames():
        return Category.categories()
    return dict(getCategoryNames=getCategoryNames)


# User Routes
@app.route('/user/<int:key>/')
def viewUser(key):

    vUser = User.query.filter_by(id = key).one()

    return render_template(
        'generic.html',
        modelType="user",
        viewType = os.path.join("partials","view.html"),
        key = key,
        traits = vUser.traits(),
        name = vUser.name,
        allowAlter = canAlter(key)
    )

@app.route('/user/new', methods=['GET','POST'])
@app.route('/user/new/', methods=['GET','POST'])
def newUser():

    if isActiveSession() == False:
        return redirect(url_for('listUser'))

    if request.method == 'POST':
        newUser = User(
            name = request.form['name']
        )

        session.add(newUser)
        session.commit()

        flash("New User created!")
        return redirect( url_for("viewUser", key = newUser.id) )

    else:
        return render_template(
            'new.html',
            modelType = "user",
            traits = User.defaultTraits()
        )


@app.route('/user/<int:key>/edit/', methods=['GET','POST'])
def editUser(key):
    if isActiveSession() == False:
        return redirect(url_for('listCategory'))

    edUser = User.query.filter_by(id = key).one()

    if request.method == 'POST':
        edUser.name = request.form['name']

        session.add(edUser)
        session.commit()

        return redirect( url_for('viewUser', key = edUser.id) )

    else:
        return render_template(
            'edit.html',
            modelType = "user",
            key = key,
            traits = edUser.traits()
        )


@app.route('/user/<int:key>/delete/', methods=['GET','POST'])
def deleteUser(key):
    if isActiveSession() == False:
        return redirect(url_for('listUser'))

    delUser = User.query.filter_by(id = key).one()

    if request.method == 'POST':
        session.delete(delUser)
        session.commit()

        return redirect( url_for('listUser') )

    else:
        return render_template(
            'delete.html',
            modelType = "user",
            key = key,
            name = delUser.name
        )


@app.route('/user/')
@app.route('/user')
def listUser():
    users = User.query.all()
    return render_template(
        'list.html',
        modelType = "user",
        objects = users,
        client_id = CLIENT_ID,
        state = getLoginSessionState()
    )


# Category Routes
@app.route('/category/<int:key>/')
def viewCategory(key):
    category = Category.query.filter_by(id = key).one()

    return render_template(
        'generic.html',
        modelType = "category",
        viewType = os.path.join("partials","view.html"),
        key = key,
        name = category.name,
        traits = category.traits(),
        allowAlter = canAlter(category.user_id)
    )


@app.route('/category/new',  methods=['GET','POST'])
@app.route('/category/new/', methods=['GET','POST'])
def newCategory():
    if isActiveSession() == False:
        return redirect(url_for('listCategory'))


    if request.method == 'POST':
        newCategory = Category(
            user_id = getSessionUserID(),
            name = request.form['name']
        )

        session.add(newCategory)
        session.commit()

        flash("New Category created!")
        return redirect(url_for('viewCategory', key = newCategory.id))

    else:
        return render_template(
            'new.html',
            modelType = "category",
            traits = Category.defaultTraits()
        )


# Edit a Category
@app.route('/category/<int:key>/edit/',
          methods=['GET','POST'])
def editCategory(key):

    if isActiveSession() == False:
        return redirect(url_for('listCategory'))

    editCategory = Category.query.filter_by(id = key).one()

    if request.method == 'POST':

        editCategory.name = request.form['name']

        session.add(editCategory)
        session.commit()

        flash("Category edited!")
        return redirect(url_for('viewCategory', key = key))

    else:
        return render_template(
            'edit.html',
            modelType = 'category',
            key = key,
            traits = editCategory.traits()
        )


@app.route('/category/<int:key>/delete/',
           methods=['GET','POST'])
def deleteCategory(key):
    if isActiveSession() == False:
        return redirect(url_for('listCategory'))

    deleteCategory = Category.query.filter_by(id = key).one()

    if request.method == 'POST':
        session.delete(deleteCategory)
        session.commit()

        flash("Category deleted!")
        return redirect(url_for('listCategory'))
    else:
        return render_template(
            'delete.html',
            modelType = "category",
            key = key,
            name = deleteCategory.name
        )


# List all Categorys
@app.route('/category/')
@app.route('/category')
def listCategory():
    categories = Category.query.all()
    return render_template(
        'list.html',
        modelType = "category",
        objects = categories,
        client_id = CLIENT_ID,
        state = getLoginSessionState()
    )


# Item Routes
# View a Item - This route provides a beautified url in the browser
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def viewCatItem(category_name, item_name):
    category = Category.query.filter_by(name = category_name).one()
    item = Item.query.filter_by(name = item_name, cat_id = category.id).one()

    return render_template(
        'generic.html',
        modelType = 'item',
        viewType = os.path.join("partials","view.html"),
        category = category_name,
        key = item.id,
        name = item.name,
        traits = item.traits(),
        allowAlter = canAlter(item.user_id)
    )


# Redirect to viewCatItem
@app.route('/item/<int:key>/')
def viewItem(key):
    item = Item.query.filter_by(id = key).one()
    category = Category.query.filter_by(id = item.cat_id).one()

    return redirect(
        url_for('viewCatItem', category_name=category.name, item_name = item.name)
    )


# Create a Item - could change route to /catalog/<category>/item/add
@app.route('/catalog/item/add', methods=['GET','POST'])
def newItem():
    if isActiveSession() == False:
        return redirect(url_for('listItem'))

    print app.config['APP_IMAGES']
    if request.method == 'POST':

        # Handle uploaded image
        picture = request.files['picture']
        pictureUrl = processImageUpload(picture)

        newItem = Item(
            name = request.form['name'],
            dateCreated = datetime.strptime(request.form['created'], "%Y-%m-%d"),
            category = Category.query.filter_by(name = request.form['category']).one(),
            description = request.form['description'],
            user_id = getSessionUserID(),
            picture = pictureUrl
        )
        session.add(newItem)
        session.flush()
        key = newItem.id
        session.commit()

        flash("New item created!")
        return redirect(url_for('viewItem', key = newItem.id))

    else:

        return render_template(
            'generic.html',
            modelType = "item",
            viewType = os.path.join("partials","new.html"),
            traits = Item.defaultTraits()
        )


# Edit an Item - Descriptive URL
@app.route('/catalog/<string:category_name>/<string:item_name>/edit')
def editCatItem(category_name, item_name):
    category = Category.query.filter_by(name = category_name).one()
    item = Item.query.filter_by(name = item_name, cat_id = category.id).one()


    return render_template(
        'generic.html',
        modelType = 'item',
        viewType = os.path.join("partials","edit.html"),
        category = category_name,
        key = item.id,
        name = item.name,
        traits = item.traits(True),
        allowAlter = canAlter(item.user_id)
    )


# Edit an Item
@app.route('/item/<int:key>/edit/', methods=['GET','POST'])
def editItem(key):
    if isActiveSession() == False:
        return redirect(url_for('listItem'))
    else:
        item = Item.query.filter_by(id = key).one()

        if request.method == 'POST':

            # New Image uploaded, Save and add url to Item record
            if request.files['upload']:

                item.picture = processImageUpload(request.files['upload'])

            category = Category.query.filter_by(
                name = request.form['category']).one()

            item.name = str(request.form['name'])
            item.dateCreated = datetime.strptime(
                request.form['created'], "%Y-%m-%d")

            item.cat_id = category.id
            item.description = request.form['description']

            session.add(item)
            session.commit()

            flash("Item edited!")

            return redirect(
                url_for(
                    'viewCatItem',
                    category_name = category.name,
                    item_name = item.name
                )
            )


        else:
            category = Category.query.filter_by(id = item.cat_id).one()

            return redirect(
                url_for(
                    'editCatItem',
                    category_name = category.name,
                    item_name = item.name
                )
            )

@app.route('/catalog/<string:item_name>/delete', methods=['GET'])
def delItem(item_name):

    deleteItem = Item.query.filter_by(name = item_name).one()

    return render_template(
        'generic.html',
        viewType = os.path.join("partials","delete.html"),
        modelType = "item",
        key = deleteItem.id,
        name = item_name
    )


# Delete an Item
@app.route('/item/<int:key>/delete/', methods=['GET','POST'])
def deleteItem(key):
    if isActiveSession() == False:
        return redirect(url_for('listItem'))

    deleteItem = Item.query.filter_by(id = key).one()


    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()

        flash("Item deleted!")
        return redirect( url_for('listItem') )

    else:
        return redirect(
            url_for('delItem', item_name = deleteItem.name)
        )

@app.route('/catalog/<string:category_name>/items')
def listCategoryItem(category_name):
    category = Category.query.filter_by(name = category_name).one()
    items = Item.query.filter_by(cat_id = category.id).all()

    return render_template(
        'generic.html',
        viewType = os.path.join("partials","list.html"),
        modelType = 'item',
        objects = items,
        client_id = CLIENT_ID,
        state = getLoginSessionState()
    )


# List all Items
@app.route('/item/')
@app.route('/item')
@app.route('/')
def listItem():
    items = Item.query.order_by(desc(Item.dateCreated)).all()

    return render_template(
        'generic.html',
        viewType = os.path.join("partials","list.html"),
        modelType = 'item',
        objects = items,
        client_id = CLIENT_ID,
        state = getLoginSessionState()
    )


# An API endpoint to a Item in JSON format
@app.route('/item/<int:key>/JSON')
def itemJSON(key):
    item = Item.query.filter_by(id = key).one()

    return jsonify(Item=item.serialize)


# A JSON API endpoint for the entire catalog.
@app.route('/catalog/JSON')
def catalogJSON():
    categories = Category.query.all()
    cats = [c.serialize for c in categories]
    return jsonify(Catalog=cats)


# An XML endpoint for the entire catalog
@app.route('/catalog/XML')
def catalogXML():
    categories = Category.query.all()
    cats = [c.serialize for c in categories]

    from dicttoxml import dicttoxml as d2xml
    js = jsonify(Catalog=cats)
    xmlCatalog = d2xml(cats)
    print xmlCatalog

    return Response(xmlCatalog, mimetype="text/xml")
    '''
    import xml.etree.ElementTree as ET
    root = ET.Element('Catalog')

#    response = make_response(ET.dump(root))
#    response.headers["Content-Type"] = "text/xml"

    return Response(ET.dump(root), mimetype="text/xml")'''

# Routes for Authentication with Google
@app.route('/gconnect', methods=['POST'])
def gconnect():
    return ConnectGoogle(request)


# Disconnect From Google.
@app.route('/gdisconnect')
def gdisconnect():
    print "/gdisconnect"
    res = DisconnectGoogle()
    print res
    return res

from datetime import datetime
import os

from flask import (
    render_template,
    url_for,
    request,
    redirect,
    flash,
    jsonify,
    Response
)

from sqlalchemy import desc
from werkzeug import secure_filename
from database import session

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
    getSessionUserInfo
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


# Gets Session User Info
@app.context_processor
def getsessionuserinfo_processor():
    return dict(getSessionUserInfo=getSessionUserInfo)


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
@app.route('/catalog/user/<int:key>/')
def viewUser(key):

    vUser = User.query.filter_by(id=key).one()

    return render_template(
        'generic.html',
        modelType="user",
        viewType=os.path.join("partials", "view.html"),
        key=key,
        traits=vUser.traits(),
        name=vUser.name,
        allowAlter=canAlter(key)
    )


@app.route('/catalog/user/new', methods=['GET', 'POST'])
@app.route('/catalog/user/new/', methods=['GET', 'POST'])
def newUser():

    if isActiveSession() is False:
        return redirect(url_for('listUser'))

    if request.method == 'POST':
        newUser = User(
            name=request.form['name']
        )

        session.add(newUser)
        session.commit()

        flash("New User created!")
        return redirect(url_for("viewUser", key=newUser.id))

    else:
        return render_template(
            'generic.html',
            modelType="user",
            viewType=os.path.join("partials", 'new.html'),
            traits=User.defaultTraits()
        )


@app.route('/catalog/user/<int:key>/edit/', methods=['GET', 'POST'])
def editUser(key):
    if isActiveSession() is False:
        return redirect(url_for('listCategory'))

    edUser = User.query.filter_by(id=key).one()

    # Don't allow a user to change other user records
    if canAlter(edUser.id) is False:
        return redirect(url_for('listItem'))

    if request.method == 'POST':
        edUser.name = request.form['name']

        session.add(edUser)
        session.commit()

        return redirect(url_for('viewUser', key=edUser.id))

    else:
        return render_template(
            'generic.html',
            modelType="user",
            viewType=os.path.join("partials", 'edit.html'),
            key=key,
            traits=edUser.traits()
        )


@app.route('/catalog/user/<int:key>/delete/', methods=['GET', 'POST'])
def deleteUser(key):
    if isActiveSession() is False:
        return redirect(url_for('listUser'))

    delUser = User.query.filter_by(id=key).one()

    # Don't allow a user to change other user records
    if canAlter(delUser.id) is False:
        return redirect(url_for('listItem'))

    if request.method == 'POST':
        session.delete(delUser)
        session.commit()

        return redirect(url_for('listUser'))

    else:
        return render_template(
            'generic.html',
            modelType="user",
            viewType=os.path.join("partials", 'delete.html'),
            key=key,
            name=delUser.name
        )


@app.route('/catalog/user/')
@app.route('/catalog/user')
def listUser():
    users = User.query.all()
    return render_template(
        'generic.html',
        modelType="user",
        viewType=os.path.join("partials", 'list.html'),
        objects=users,
        client_id=CLIENT_ID,
        state=getLoginSessionState()
    )


# Category Routes
@app.route('/catalog/category/<int:key>/')
def viewCategory(key):
    category = Category.query.filter_by(id=key).one()

    return render_template(
        'generic.html',
        modelType="category",
        viewType=os.path.join("partials", "view.html"),
        key=key,
        name=category.name,
        traits=category.traits(),
        allowAlter=canAlter(category.user_id)
    )


@app.route('/catalog/category/new',  methods=['GET', 'POST'])
@app.route('/catalog/category/new/', methods=['GET', 'POST'])
def newCategory():
    if isActiveSession() is False:
        return redirect(url_for('listCategory'))

    if request.method == 'POST':
        newCategory = Category(
            user_id=getSessionUserInfo()['id'],
            name=request.form['name']
        )

        session.add(newCategory)
        session.commit()

        flash("New Category created!")
        return redirect(url_for('viewCategory', key=newCategory.id))

    else:
        return render_template(
            'generic.html',
            modelType="category",
            viewType=os.path.join("partials", 'new.html'),
            traits=Category.defaultTraits()
        )


# Edit a Category
@app.route('/catalog/category/<int:key>/edit/', methods=['GET', 'POST'])
def editCategory(key):

    if isActiveSession() is False:
        return redirect(url_for('listItem'))

    editCategory = Category.query.filter_by(id=key).one()

    # Don't allow a user to change a category they don't 'own'
    if canAlter(editCategory.user_id) is False:
        return redirect(url_for('listItem'))


    if request.method == 'POST':

        editCategory.name = request.form['name']

        session.add(editCategory)
        session.commit()

        flash("Category edited!")
        return redirect(url_for('viewCategory', key=key))

    else:
        return render_template(
            'generic.html',
            modelType="category",
            viewType=os.path.join("partials", 'edit.html'),
            key=key,
            traits=editCategory.traits(),
            allowAlter=canAlter(editCategory.user_id)
        )


@app.route('/catalog/category/<int:key>/delete/', methods=['GET', 'POST'])
def deleteCategory(key):
    if isActiveSession() is False:
        return redirect(url_for('listCategory'))

    deleteCategory = Category.query.filter_by(id=key).one()

    # Don't allow a user to change a category they don't 'own'
    if canAlter(deleteCategory.user_id) is False:
        return redirect(url_for('listItem'))

    if request.method == 'POST':
        session.delete(deleteCategory)
        session.commit()

        flash("Category deleted!")
        return redirect(url_for('listCategory'))
    else:
        return render_template(
            'generic.html',
            modelType="category",
            viewType=os.path.join("partials", 'delete.html'),
            key=key,
            name=deleteCategory.name
        )


# List all Categorys
@app.route('/catalog/category/')
@app.route('/catalog/category')
def listCategory():
    categories = Category.query.all()
    return render_template(
        'generic.html',
        modelType="category",
        viewType=os.path.join("partials", "list.html"),
        objects=categories,
        client_id=CLIENT_ID,
        state=getLoginSessionState()
    )


# Item Routes
# View a Item - This route provides a beautified url in the browser
@app.route('/catalog/<string:category_name>/<string:item_name>/')
def viewCatItem(category_name, item_name):
    category = Category.query.filter_by(name=category_name).one()
    item = Item.query.filter_by(name=item_name, cat_id=category.id).one()

    return render_template(
        'generic.html',
        modelType='item',
        viewType=os.path.join("partials", "view.html"),
        category=category_name,
        key=item.id,
        name=item.name,
        traits=item.traits(),
        allowAlter=canAlter(item.user_id)
    )


# Redirect to viewCatItem
@app.route('/catalog/item/<int:key>/')
def viewItem(key):
    item = Item.query.filter_by(id=key).one()
    category = Category.query.filter_by(id=item.cat_id).one()

    return redirect(
        url_for(
            'viewCatItem',
            category_name=category.name,
            item_name=item.name
        )
    )


# Create a Item - could change route to /catalog/<category>/item/add
@app.route('/catalog/item/add', methods=['GET', 'POST'])
def newItem():
    if isActiveSession() is False:
        return redirect(url_for('listItem'))

    print app.config['APP_IMAGES']
    if request.method == 'POST':

        # Handle uploaded image
        picture = request.files['picture']
        pictureUrl = processImageUpload(picture)

        newItem = Item(
            name=request.form['name'],
            dateCreated=datetime.strptime(request.form['created'], "%Y-%m-%d"),
            category=Category.query.filter_by(
                name=request.form['category']).one(),
            description=request.form['description'],
            user_id=getSessionUserInfo()['id'],
            picture=pictureUrl
        )
        session.add(newItem)
        session.flush()
        session.commit()

        flash("New item created!")
        return redirect(url_for('viewItem', key=newItem.id))

    else:

        return render_template(
            'generic.html',
            modelType="item",
            viewType=os.path.join("partials", "new.html"),
            traits=Item.defaultTraits()
        )


# Edit an Item - Descriptive URL
@app.route('/catalog/<string:category_name>/<string:item_name>/edit')
def editCatItem(category_name, item_name):
    category = Category.query.filter_by(name=category_name).one()
    item = Item.query.filter_by(name=item_name, cat_id=category.id).one()

    return render_template(
        'generic.html',
        modelType='item',
        viewType=os.path.join("partials", "edit.html"),
        category=category_name,
        key=item.id,
        name=item.name,
        traits=item.traits(True),
        allowAlter=canAlter(item.user_id)
    )


# Edit an Item
@app.route('/catalog/item/<int:key>/edit/', methods=['GET', 'POST'])
def editItem(key):
    if isActiveSession() is False:
        return redirect(url_for('listItem'))
    else:
        item = Item.query.filter_by(id=key).one()

        if request.method == 'POST':

            # New Image uploaded, Save and add url to Item record
            if request.files['upload']:

                item.picture = processImageUpload(request.files['upload'])

            category = Category.query.filter_by(
                name=request.form['category']).one()

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
                    category_name=category.name,
                    item_name=item.name
                )
            )

        else:
            category = Category.query.filter_by(id=item.cat_id).one()

            return redirect(
                url_for(
                    'editCatItem',
                    category_name=category.name,
                    item_name=item.name
                )
            )


@app.route('/catalog/<string:item_name>/delete', methods=['GET'])
def delItem(item_name):

    deleteItem = Item.query.filter_by(name=item_name).one()

    return render_template(
        'generic.html',
        viewType=os.path.join("partials", "delete.html"),
        modelType="item",
        key=deleteItem.id,
        name=item_name
    )


# Delete an Item
@app.route('/catalog/item/<int:key>/delete/', methods=['GET', 'POST'])
def deleteItem(key):
    if isActiveSession() is False:
        return redirect(url_for('listItem'))

    deleteItem = Item.query.filter_by(id=key).one()

    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()

        flash("Item deleted!")
        return redirect(url_for('listItem'))

    else:
        return redirect(
            url_for('delItem', item_name=deleteItem.name)
        )


@app.route('/catalog/<string:category_name>/items')
def listCategoryItem(category_name):
    category = Category.query.filter_by(name=category_name).one()
    items = Item.query.filter_by(cat_id=category.id).all()

    return render_template(
        'generic.html',
        viewType=os.path.join("partials", "list.html"),
        modelType='item',
        objects=items,
        client_id=CLIENT_ID,
        state=getLoginSessionState()
    )


# List all Items
@app.route('/catalog/item/')
@app.route('/catalog/item')
@app.route('/')
def listItem():
    items = Item.query.order_by(desc(Item.dateCreated)).all()

    results = [ (Category.findByID(i.cat_id).name, i.name) for i in items ]
    objects = []

    for category, item in results:
        objects.append({'category': category, 'item': item})

    for o in objects:
        print o['item'] + " (" + o['category'] + ")"

    return render_template(
        'generic.html',
        viewType=os.path.join("partials", "list.html"),
        modelType='item',
        objects=items,
        client_id=CLIENT_ID,
        state=getLoginSessionState()
    )


# An API endpoint to a Item in JSON format
@app.route('/catalog/item/<int:key>/JSON')
def itemJSON(key):
    item = Item.query.filter_by(id=key).one()

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
    xmlCatalog = d2xml(cats)
    print xmlCatalog

    return Response(xmlCatalog, mimetype="text/xml")


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

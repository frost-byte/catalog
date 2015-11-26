from datetime import datetime
from random import randint
import random, string
import json

from .auth import CLIENT_ID, isActiveSession

from flask import (
    render_template,
    url_for,
    request,
    redirect,
    flash,
    jsonify,
    make_response
)


from database import session, Base
from models import (
    Category,
    Item,
    User
)

from .auth import getLoginSessionState, ConnectGoogle, DisconnectGoogle
from populator import item_images
from urls import Urls
from . import app


# Allow templates to generate Urls for different Models
@app.context_processor
def makeurls_processor():
    def makeUrls(suffix, key=0):
        return Urls(suffix, key)
    return dict(makeUrls=makeUrls)


@app.context_processor
def hasattr_processor():
    return dict(hasattr=hasattr)


@app.context_processor
def isactivesession_processor():
    return dict(isActiveSession=isActiveSession)


@app.context_processor
def getplural_processor():
    def getPlural(singular):
        if singular.lower() == 'category':
            return 'Categories'

        else:
            return singular.title() + "s"
    return dict(getPlural=getPlural)


# Return Category name : Category id pairs for all categories
def getCategories():
    categories = Category.query.all().order_by(Category.name)
    results = {c.name : c.id for c in categories}
    return results


# User Routes
@app.route('/user/<int:key>/')
def viewUser(key):

    vUser = User.query.filter_by(id = key).one()

    return render_template(
        'view.html',
        viewType="user",
        key = key,
        traits = vUser.traits,
        name = vUser.name
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
            viewType = "user",
            traits = User.traits
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
            viewType = "user",
            key = key,
            traits = edUser.traits
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
            viewType = "user",
            key = key,
            name = delUser.name
        )


@app.route('/user/')
@app.route('/user')
def listUser():
    users = User.query.all()
    return render_template(
        'list.html',
        viewType = "user",
        objects = users,
        client_id = CLIENT_ID,
        state = getLoginSessionState()
    )


# Category Routes
@app.route('/category/<int:key>/')
def viewCategory(key):
    category = Category.query.filter_by(id = key).one()

    return render_template(
        'view.html',
        viewType = "category",
        key = key,
        name = category.name,
        traits = category.traits
    )


@app.route('/category/new',  methods=['GET','POST'])
@app.route('/category/new/', methods=['GET','POST'])
def newCategory():
    if isActiveSession() == False:
        return redirect(url_for('listCategory'))


    if request.method == 'POST':
        newCategory = Category(
            name = request.form['name']
        )

        session.add(newCategory)
        session.commit()

        flash("New Category created!")
        return redirect(url_for('viewCategory', key = newCategory.id))

    else:
        return render_template(
            'new.html',
            viewType = "category",
            traits = Category.traits
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
            viewType = 'category',
            key = key,
            traits = editCategory.traits
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
            viewType = "category",
            key = key,
            name = deleteCategory.name
        )


# List all Categorys
@app.route('/category/')
@app.route('/category')
@app.route('/')
def listCategory():
    categories = Category.query.all()
    return render_template(
        'list.html',
        viewType = "category",
        objects = categories,
        client_id = CLIENT_ID,
        state = getLoginSessionState()
    )


# Item Routes
# View a Item
@app.route('/item/<int:key>/')
def viewItem(key):

    item = Item.query.filter_by(id = key).one()

    return render_template(
        'view.html',
        viewType = "item",
        key = key,
        name = item.name,
        traits = item.traits
    )


# Create a Item
@app.route('/item/new',  methods=['GET','POST'])
@app.route('/item/new/', methods=['GET','POST'])
def newItem():
    if isActiveSession() == False:
        return redirect(url_for('listItem'))

    if request.method == 'POST':
        newItem = Item(
            name = request.form['name'],
            dateCreated = datetime.strptime(request.form['created'], "%Y-%m-%d"),
            category = Category.query.filter_by(name = request.form['category']).one(),
            description = request.form['description'],
            #user = request.session.user
            picture = request.form['picture']
        )

        session.add(newItem)

        flash("New item created!")
        return redirect(url_for('viewItem', key = newItem.id))

    else:
        return render_template(
            'new.html',
            viewType = "item",
            traits = Item.traits
        )


# Edit a Item
@app.route('/item/<int:key>/edit/', methods=['GET','POST'])
def editItem(key):
    if isActiveSession() == False:
        return redirect(url_for('listItem'))

    editItem = Item.query.filter_by(id = key).one()

    if request.method == 'POST':
        editItem.name = request.form['name']
        editItem.dateCreated = datetime.strptime(request.form['created'], "%Y-%m-%d")
        editItem.category = Category.query.filter_by(
            name = request.form['category']).one()
        editItem.description = request.form['description']
        editItem.picture = request.form['picture']
        # editItem.user = request.session.user

        session.add(editItem)
        session.commit()

        flash("Item edited!")
        return redirect( url_for('viewItem', key = key) )

    else:
        return render_template(
            'edit.html',
            viewType = 'item',
            key = key,
            traits = editItem.traits
        )

# Delete a Item
@app.route('/item/<int:key>/delete/',
           methods=['GET','POST'])
def deleteItem(key):
    if isActiveSession() == False:
        return redirect(url_for('listItem'))

    deleteItem = Item.query.filter_by(id = key).one()

    # TODO: add user validation, the current session's user id needs to match
    # the user id of the Item.

    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()

        flash("Item deleted!")
        return redirect( url_for('listItem') )

    else:
        return render_template(
            'delete.html',
            viewType = "item",
            key = key,
            name = deleteItem.name
        )


# List all Items
@app.route('/item/')
@app.route('/item')
def listItem():
    items = Item.query.all()

    return render_template(
        'list.html',
        viewType = 'item',
        objects = items,
        client_id = CLIENT_ID,
        state = getLoginSessionState()
    )


# An API endpoint to a Item in JSON format
@app.route('/item/<int:key>/JSON')
def itemJSON(key):
    item = Item.query.filter_by(id = key).one()

    return jsonify(Item=item.serialize)


# Routes for Authentication with Google
@app.route('/gconnect', methods=['POST'])
def gconnect():
    return ConnectGoogle(request)


# Disconnect From Google.
@app.route('/gdisconnect')
def gdisconnect():
    return DisconnectGoogle()
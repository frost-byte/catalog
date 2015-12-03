'''
This is the views module for the Catalog app.
The module provides routes to create a RESTful api to create, read,
update and delete records for the following elements in the Catalog:

User, Category and Item

There are routes to authorize a user using the OAuth2 api provided by Google
to connect and disconnect a user via their Google+ profile.

There are two endpoints provided to return the entirety of the Catalog
in JSON or XML.

The module also includes a handful of context processor's for its flask app.
These functions allow the jinja2 templates, which provide the views to the
web client, with means of accessing variables and functions in the Python
modules and code.

'''
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
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from werkzeug import secure_filename
from database import session

from models import (
    Category,
    Item,
    User
)

from auth import (
    CLIENT_ID,
    isActiveSession,
    getLoginSessionState,
    ConnectGoogle,
    DisconnectGoogle,
    canAlter,
    getSessionUserInfo
)

from urls import Urls
from app import app


def allowed_image(filename):
    """Determine if the specified file has the proper extension to be classified
    as an image.

    Note:
        From flask docs, checks that uploaded images have specific file extensions
        http://flask.pocoo.org/docs/0.10/patterns/fileuploads/

    Args:
        filename (string): The filename to be validated as an acceptable image type.

    Returns:
        True if the file is a proper image file, based upon its extension.
        False if it is not considered a valid image type.

    """
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def processImageUpload(image):
    """Process an uploaded image.  If it's a valid file type, then save the file
    and return the local url.

    Args:
        image (file): A file passed via a request that was submitted via a Web Form.

    Returns:
        The local path to the file for the image, this provides a url that can
        be referred to in a database record.

    """
    # Valid object and extension
    if image and allowed_image(image.filename):

        # Scrub filename - removes and path information and results in just a
        # name with a file extension.
        filename = secure_filename(image.filename)

        # Save the file to the App's Images directory.
        image.save(os.path.join(app.config['APP_IMAGES'], filename))

        # Return the local url for the image.
        return os.path.join("images", filename)


@app.context_processor
def makeurls_processor():
    def makeUrls(suffix, key=0):
        """Refer to :py:class:`~urls.Urls`"""
        return Urls(suffix, key)
    return dict(makeUrls=makeUrls)


@app.context_processor
def hasattr_processor():
    """Provide templates with the ability to check if a python object contains
    the specified attribute

    Args:
        o (object): The object to check.
        attr (string): The name of the attribute to look for in object, o.

    Returns:
        True if object o has the attribute.
        False if there is no attribute with the value of attr in object o.

    """
    return dict(hasattr=hasattr)


# Checks for a valid session
@app.context_processor
def isactivesession_processor():
    """Refer to :py:func:`~auth.isActiveSession`"""
    return dict(isActiveSession=isActiveSession)


# Gets Session User Info
@app.context_processor
def getsessionuserinfo_processor():
    """Refer to :py:func:`~auth.getSessionUserInfo`"""
    return dict(getSessionUserInfo=getSessionUserInfo)


# Allow Templates to determine if a user can edit/delete a record
@app.context_processor
def canalter_processor():
    """Refer to :py:func:`~auth.canAlter`"""
    return dict(canAlter=canAlter)



@app.context_processor
def getplural_processor():
    def getPlural(singular):
        """Converts the form of the word in singular to its plural form.

        Notes:
            In this app it turns item and user into items, users.
            and category into categories.  Allows for generic templates.

        Args:
            singular (string): The word to pluralize

        Returns:
            The pluralized form of the word in the singular argument.

        """
        if singular.lower() == 'category':
            return 'Categories'

        else:
            return singular.title() + "s"
    return dict(getPlural=getPlural)


@app.context_processor
def getcategories_processor():
    def getCategoryNames():
        '''Refer to :py:method:`~Category.categories`'''
        return Category.categories()
    return dict(getCategoryNames=getCategoryNames)


# User Routes
@app.route('/catalog/user/<int:key>/')
def viewUser(key):
    """Present the Web User with a View for the Item with the id equal to key.

    Args:
        key (int): An ID corresponding to a User record in the database.

    Returns:
        The updated View in the User's browser that corresponds to the
        requested user.

    """
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
    """Present an Authorized Web User with a View for adding a new user.

    Returns:
        For a GET operation returns a Web View containing a form for entering
        data for the new user.

        A successful POST request directs presents a View of the new Record.

    """
    if isActiveSession() is False:
        return redirect(url_for('listUser'))

    # Process New User Form Submission
    if request.method == 'POST':
        # Add the new user record to the database
        newUser = User(
            name=request.form['name']
        )

        session.add(newUser)
        session.commit()

        flash("New User created!")

        # Redirect to the User View
        return redirect(url_for("viewUser", key=newUser.id))

    # Present the New User Form
    else:
        return render_template(
            'generic.html',
            modelType="user",
            viewType=os.path.join("partials", 'new.html'),
            traits=User.defaultTraits()
        )


@app.route('/catalog/user/<int:key>/edit/', methods=['GET', 'POST'])
def editUser(key):
    """Present the Web User with an Edit View for the their User account.

    Args:
        key (int): An ID corresponding to a User record in the database.

    Returns:
        For a GET operation returns a Web View containing a form for editing
        data for the user.

        A successful POST request directs presents the updated Record view.

    """
    # Require Authentication to Edit Users
    if isActiveSession() is False:
        return redirect(url_for('listCategory'))

    edUser = User.query.filter_by(id=key).one()

    # Don't allow a user to change other user records
    if canAlter(edUser.id) is False:
        return redirect(url_for('listItem'))

    # Process the Edit User form when submitted.
    if request.method == 'POST':
        edUser.name = request.form['name']

        session.add(edUser)
        session.commit()

        return redirect(url_for('viewUser', key=edUser.id))

    else:
        # Present the Edit User Form
        return render_template(
            'generic.html',
            modelType="user",
            viewType=os.path.join("partials", 'edit.html'),
            key=key,
            traits=edUser.traits()
        )


@app.route('/catalog/user/<int:key>/delete/', methods=['GET', 'POST'])
def deleteUser(key):
    """Present the Web User with a Delete View for the their User account.

    Args:
        key (int): An ID corresponding to a User record in the database.

    Returns:
        For a GET operation returns a Web View containing buttons for
        canceling or submitting the delete user request.

        A successful POST request would delete the User's record, sign them out
        and revoke the app's authorization to use their Google profile

    """
    if isActiveSession() is False:
        return redirect(url_for('listUser'))
    else:
        return redirect(url_for('viewUser', key=key))
'''
    # This functionality is Disabled because there is nothing in place to
    # close out the user's session and disconnect them from Google before 
    # they're deleted.
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
'''

@app.route('/catalog/user/')
@app.route('/catalog/user')
def listUser():
    """Present the Web User with an Edit View for the their User account.

    Returns:
        Presents the user with a list of all user Names
    """
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
    """A View of a specific Category's record.

    Args:
        key (int): The primary key of the category.

    Returns:
        Presents the user with a list of all Categories

    """
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
    """Allow an Authorized User to add a new Category or Process the form for
    adding a new Category.

    Returns:
        For a GET operation returns a Web View containing a form for entering
        data for the new user.

        A successful POST request directs presents a View of the new Category.

    """
    # Only an Authenticated User can add New Categories
    if isActiveSession() is False:
        return redirect(url_for('listCategory'))

    # Process the New Category Form and add it to the Database
    if request.method == 'POST':
        newCategory = Category(
            user_id=getSessionUserInfo()['id'],
            name=request.form['name']
        )

        session.add(newCategory)
        session.commit()

        flash("New Category created!")
        # Display the Information for the new Category
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
    """Allow an Authorized User to edit a new Category or Process the form for
    editing a Category.

    Args:
        key (int): The primary key of the category.

    Returns:
        For a GET operation returns a Web View containing a form for altering
        data for the category.

        A successful POST request directs presents a View of the new Category.

    """
    # Only an Authenticated User can add edit a category.
    if isActiveSession() is False:
        return redirect(url_for('listItem'))

    editCategory = Category.query.filter_by(id=key).one()

    # Don't allow a user to change a category they don't 'own'
    if canAlter(editCategory.user_id) is False:
        return redirect(url_for('viewCategory', key=editCategory.id))

    # Process the Edit Form when it is Submitted.
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
    """Allow an Authorized User to delete a new Category or Process the
    deletion of a Category.

    Args:
        key (int): The primary key of the category.

    Returns:
        For a GET operation returns a View querying whether the user wants to
        delete the Category or cancel and go back to viewing it.

        A successful POST request deletes the Category and redirects to the
        list of Categories.

    """
    # Only an Authenticated User can add delete a category.
    if isActiveSession() is False:
        return redirect(url_for('listCategory'))

    deleteCategory = Category.query.filter_by(id=key).one()

    # If the logged in user did not create this Category then redirect.
    if canAlter(deleteCategory.user_id) is False:
        return redirect(url_for('viewCategory', key=deleteCategory.id))

    # Remove the Category from the Database
    if request.method == 'POST':
        session.delete(deleteCategory)
        session.commit()

        flash("Category deleted!")
        # Back to the List of Categories
        return redirect(url_for('listCategory'))
    else:
        # Present options to Delete the Category or Cancel.
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
    """A View containing the list of Categories.

    Returns:
        Presents the user with a list of all user Categories
    """
    categories = Category.query.all()

    return render_template(
        'generic.html',
        modelType="category",
        viewType=os.path.join("partials", "list.html"),
        objects=categories,
        client_id=CLIENT_ID,
        state=getLoginSessionState()
    )


@app.route('/catalog/<string:category_name>/<string:item_name>/')
def viewCatItem(category_name, item_name):
    """Present a view of an item that belongs to a specific Category

    Note:
        This route is typically redirected to behind the scenes.  Which
        allows for a legible URL to be seen by the user.  The item record
        already contains it's category id.

    Returns:
        A Web view containing information about an item, including its Category
        in the URL displayed in the browser.

    """
    # Determine the Category of the item, based upon it's name.
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

@app.route('/catalog/item/<int:key>/')
def viewItem(key):
    """This route is used behind the scenes to view an item.  It forwards
    the request on to viewCatItem.

    Args:
        key (int): The primary key of the item.

    Returns:
        The result returned from viewCatItem

    """
    item = Item.query.filter_by(id=key).one()
    category = Category.query.filter_by(id=item.cat_id).one()

    # Have the other view Render the results, provides a clearer url to the user
    return redirect(
        url_for(
            'viewCatItem',
            category_name=category.name,
            item_name=item.name
        )
    )

@app.route('/catalog/item/add', methods=['GET', 'POST'])
def newItem():
    """This route is used behind the scenes to view an item.  It forwards
    the request on to viewCatItem.  Requires a user to be authenticated.

    Notes:
        This route could be changed to reflect which category it will be in.

    Returns:
        A GET request presents the user with a form for creating a new Item.

        A POST request processes the user's input from the form and adds the
        new item.

    """
    # A user session must exist to add an item.
    if isActiveSession() is False:
        return redirect(url_for('listItem'))

    if request.method == 'POST':
        # Process the new Item from the submitted form.
        # Make sure that an item associated with this category doesn't already have
        # the name of the one submitted in the form.
        category = Category.query.filter_by(name=request.form['category']).one()

        newItemName = request.form['name']

        try:
            # We should find either zero or one item in a category with a given
            # name.
            items = Item.query.filter_by(
                cat_id=category.id, name=newItemName).one_or_none()
            print "newItem: items = {0}".format(items)

        except MultipleResultsFound as e:
            # We more than one item with the newItemName in it's category.
            print "Multiple " + e
            flash(
                "{0} items named {1} in {2} already.".format(
                    len(items),
                    newItemName,
                    category.name
                ))
            return redirect(url_for('viewCategory', key=category.id ))

        if items is None:
            # This is a new Item for this category and it's name is unique
            # in the category.

            # Handle uploaded image
            picture = request.files['picture']
            pictureUrl = processImageUpload(picture)

            # Create the New Item and add it to the Database
            newItem = Item(
                name=request.form['name'],
                dateCreated=datetime.strptime(request.form['created'], "%Y-%m-%d"),
                cat_id=category.id,
                description=request.form['description'],
                user_id=getSessionUserInfo()['id'],
                picture=pictureUrl
            )

            session.add(newItem)
            session.flush()
            session.commit()

            flash("New item created!")
            # Present the user with a view of the new item
            return redirect(url_for('viewItem', key=newItem.id))

        else:
            # Alert the user to an already exisiting item with the specified name.
            flash(
                "An item with the name {0} already exists in {1}.".format(
                    newItemName,
                    category.name
                )
            )
            # Send the user back to the newItem Form.
            return redirect(url_for('newItem'))
    else:
        # Present the User with the New Item Form
        return render_template(
            'generic.html',
            modelType="item",
            viewType=os.path.join("partials", "new.html"),
            traits=Item.defaultTraits()
        )


# Edit an Item - Descriptive URL
@app.route('/catalog/<string:category_name>/<string:item_name>/edit')
def editCatItem(category_name, item_name):
    """Edit an Item in a Category.

    Requires a user to be authenticated and to have created the item.

    Args:
        category_name (string): The Category of the Item to edit.

        item_name (string): The name of the Item to Edit.

    Returns:
        A GET request presents the user with a form for editing an Item.

        A POST request processes the user's input from the form and updates the
        item.

    """
    # User has been authenticated and the login_session is valid.
    if isActiveSession() is False:
        flash("Please log in to edit an item.")
        return redirect(url_for('listItem'))

    # Find the Item's category by the category's name in the database
    category = Category.query.filter_by(name=category_name).one()

    # Find the item using its name and its category's id
    item = Item.query.filter_by(name=item_name, cat_id=category.id).one()

    # The active user for the session must be the creator of the item being
    # editted.
    if canAlter(item.user_id) is False:
        flash("You are not authorized to alter that item.")
        return redirect(url_for('viewItem', key=item.id))

    # This is the right user, so show them the edit form.
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



@app.route('/catalog/item/<int:key>/edit/', methods=['GET', 'POST'])
def editItem(key):
    """Edit an Item in a Category.

    Requires a user to be authenticated and to have created the item.

    Args:
        key (int): The primary key of the Item to Edit.

    Returns:
        A GET request presents the user with a form for editing an Item.

        A POST request processes the user's input from the form and updates the
        item.

    """
    # User has been authenticated and the login_session is valid.
    if isActiveSession() is False:
        flash("You need to log in to edit items.")
        return redirect(url_for('listItem'))
    else:
        # Find the item to edit using its id.
        item = Item.query.filter_by(id=key).one()

        if request.method == 'POST':
            # Make sure that an item associated with this category doesn't already have
            # the name of the one submitted in the form.
            category = Category.query.filter_by(name=request.form['category']).one()

            itemName = str(request.form['name'])

            try:
                # We should find either zero or one item in a category with a given
                # name.
                items = Item.query.filter_by(
                    cat_id=category.id, name=itemName).one_or_none()
                print "editItem: items = {0}".format(items)

            except MultipleResultsFound as e:
                # We found more than one item with the form's item name for
                # this category.
                print "Multiple " + e
                flash(
                    "{0} items named {1} in category {2} already.".format(
                        len(items),
                        itemName,
                        category.name
                    ))
                return redirect(url_for('editItem', key=key ))


            if items is None or items.id == key:
                # User can edit the item already in the category but can't move it
                # to another category that already has an item with the same name.

                # Different Image uploaded, Save and add url to Item record
                if request.files['upload']:

                    item.picture = processImageUpload(request.files['upload'])

                item.name = itemName
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
                flash(
                    '''A different item named {0} already exists in the
                    category called {1}.'''.format(itemName, category.name)
                )
                return redirect(url_for('editItem', key=key))

        else:
            category = Category.query.filter_by(id=item.cat_id).one()

            return redirect(
                url_for(
                    'editCatItem',
                    category_name=category.name,
                    item_name=item.name
                )
            )


@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods=['GET'])
def delItem(item_name):
    """Retrieve the view for Deleting an Item in a Category.

    Requires a user to be authenticated and to have created the item.

    Notes:
        The actual deletion operation, when a POST request is sent, is
        performed by the deleteItem function.

    Args:
        category_name (string): The Category name of the Item to delete.

        item_name (string):     The name of the Item to delete.

    Returns:
        A GET request presents the user with choices for deleting the Item or
        canceling the operation.

    """
    if isActiveSession() is False:
        flash("Please log in to delete an item.")
        return redirect(url_for('listItem'))

    # Find the item's category by name
    category = Category.query.filter_by(name=category_name).one()

    # Find the item by matching it's name and category id to the above category.
    try:
        deleteItem = Item.query.filter_by(
            name=item_name,
            cat_id=category.id
        ).one()

    except NoResultFound:
        flash(
            '''No item named {0} was found in the {1} category.'''.format(
                item_name,
                category_name
            )
        )
        return redirect(url_for('listItem'))


    if canAlter(deleteItem.user_id) is False:
        flash("You are not authorized to delete that item.")
        return redirect(url_for('viewItem', key=deleteItem.id))

    # Forward the request to the Delete view.
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
    """Delete an Item selected by its primary key/id.

    Requires a user to be authenticated and to have created the item.

    Args:
        key (int): The primary key of the Item to delete.

    Returns:
        A GET request presents the user with choices for deleting the Item or
        canceling the operation.
    """
    if isActiveSession() is False:
        flash("Please log in to delete an item.")
        return redirect(url_for('listItem'))

    deleteItem = Item.query.filter_by(id=key).one()

    if canAlter(deleteItem.user_id) is False:
        # The active user did not create the item.
        flash("You are not authorized to delete this item.")
        return redirect(url_for('viewItem', key=key))


    if request.method == 'POST':
        # The user submitted this item for deletion.
        session.delete(deleteItem)
        session.commit()

        flash("Item deleted!")
        return redirect(url_for('listItem'))

    else:
        # Present the Deletion View to the User for the given Item/Category
        category = Category.query.filter_by(id=deleteItem.cat_id).one()

        return redirect(
            url_for(
                'delItem',
                category_name=category.name,
                item_name=deleteItem.name
            )
        )


@app.route('/catalog/<string:category_name>/items')
def listCategoryItem(category_name):
    """List all Items in a category.

    Args:
        category_name (string): The category of items to be viewed.

    Returns:
        A GET request presents the user with the list of all items belonging to
        the specified category.

    """
    # Find the category by its name, and all Items with that category's id.
    category = Category.query.filter_by(name=category_name).one()
    items = Item.query.filter_by(cat_id=category.id).all()

    # Present the List of Items in the main view.
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
    """List all Items in the catalog.

    Returns:
        A GET request presents the user with the list of all catalog items.

    """
    # Retrieve the list of items and order them by their creation date.
    # Starting with the newest and ending with the oldest.
    items = Item.query.order_by(desc(Item.dateCreated)).all()

    # Generate a list of ( Category Name, Item Name) tuples?
    # This lets the view display each item with its respective category
    results = [ (Category.findByID(i.cat_id).name, i.name) for i in items ]
    objects = []

    # Convert the list to contain a dictionary for each item/category combo.
    for category, item in results:
        objects.append({'category': category, 'item': item})


    # Present the list of all items and their categories in the main view.
    return render_template(
        'generic.html',
        viewType=os.path.join("partials", "list.html"),
        modelType='item',
        objects=items,
        client_id=CLIENT_ID,
        state=getLoginSessionState()
    )


@app.route('/catalog/item/<int:key>/JSON')
def itemJSON(key):
    """Return information about a Catalog Item in JSON.

    Args:
        key (int): The primary key of the item to retrieve.

    Returns:
        A GET request returns information about an item in JSON

    """
    item = Item.query.filter_by(id=key).one()

    return jsonify(Item=item.serialize)


@app.route('/catalog/JSON')
def catalogJSON():
    """JSON endpoint that returns information about the entire Catalog.

    Returns:
        A GET request returns the Catalog's information in JSON

    """
    categories = Category.query.all()
    cats = [c.serialize for c in categories]
    return jsonify(Catalog=cats)


# An XML endpoint for the entire catalog
@app.route('/catalog/XML')
def catalogXML():
    """XML endpoint that returns information about the entire Catalog.

    Returns:
        A GET request returns the Catalog's information in XML

    """
    categories = Category.query.all()
    cats = [c.serialize for c in categories]

    from dicttoxml import dicttoxml as d2xml
    xmlCatalog = d2xml(cats)
    print xmlCatalog

    return Response(xmlCatalog, mimetype="text/xml")


# Routes for Authentication with Google
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Refer to :py:func:`~auth.ConnectGoogle`"""
    return ConnectGoogle(request)


# Disconnect From Google.
@app.route('/gdisconnect')
def gdisconnect():
    """Refer to :py:func:`~auth.DisconnectGoogle`"""
    res = DisconnectGoogle()
    return res

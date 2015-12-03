'''
This is the models module for the Catalog app.
The module creates the ORM model connecting classes to tables in the database.

The classes are User, Category and Item

The traits module is used for generating forms and views of instances of each
class/object.

A model uses Default Traits for plain views that offer no editing and
a traits property for views that do.

'''
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Date
)
from sqlalchemy.orm import relationship
from sqlalchemy.schema import UniqueConstraint
from trait import (
    DateTrait,
    ImageTrait,
    ImageUploadTrait,
    TextTrait,
    TextAreaTrait,
    SelectTrait
)
from database import Base, session


class Category(Base):
    '''Items in the Catalog are each assigned to a Category that pertains to
    the activity or sport associated with the item.

    Attributes:
        name (string):          The Category name.
        id (integer):           The primary key/id
        user_id (integer):      The user id of the Category's creator.
        items (relationship):   Defines the list of items in the Category.
        query (Query):          Shortcut for Querying the Category table

    '''
    __tablename__ = "category"

    query = session.query_property()

    name = Column(String(80), unique=True, nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))

    items = relationship(
        "Item",
        backref="category",
        cascade="save-update, delete, delete-orphan"
    )

    # Find a Category by its name.
    @staticmethod
    def findByName(name):
        '''Find a Category in the table by its name.

        Args:
            name (string): The Category name to find.

        Returns:
            A Category record from the database that has the specified name.
        '''
        category = Category.query.filter_by(name=name).one()
        return category

    @staticmethod
    def categories():
        '''List of all Category names in the table.

        Returns:
            A list containg the names of each Category int the table.
        '''
        return [c.name for c in Category.query.all()]

    @staticmethod
    def defaultTraits():
        '''The default traits of Category

        Returns:
            A list of Trait objects describing the attributes of a Category
            that can be viewed.
        '''
        return [TextTrait("name")]

    @staticmethod
    def findByID(id):
        '''Find a Category in the table using its id.

        Args:
            id (int): The primary key or id of the Category in the table.

        Returns:
            A Category object with the given id.
        '''
        category = Category.query.filter_by(id=id).one()
        return category

    @property
    def creator(self):
        '''The name of the user who created the Category in the Table.

        Returns:
            string: The user name who created the Category.
        '''
        user = User.query.filter_by(id=self.user_id).one()
        return user.name

    def traits(self):
        '''The attributes and values of an instance of the Category class.

        When presenting a view to a web user, the traits are parsed and
        displayed in a form or list in a format determined by the type
        of each attribute's associated Trait Class.

        Returns:
            A list containing the Traits for each attribute to be displayed
            in a view of a Category instance.
        '''
        return [
            TextTrait("name", self.name),
            TextTrait("creator", self.creator)
        ]

    @property
    def serialize(self):
        '''Serialize the properties of a Category instance.

        Returns:
            dict: A Dictionary describing key attributes of a Category instance

        '''
        cat = {
            'Category': {
                'id': self.id,
                'name': self.name,
                'creator': User.nameByID(self.user_id),
                'Items': [i.serialize for i in self.items]
            }
        }

        return cat


class User(Base):
    '''Users of the Catalog are each assigned a User record that is associated
    with the Items and Categories they create, and by extension, can edit and
    delete.  Their profile information is pulled from their Google+ profile.


    Attributes:
        name (string):              The User name.
        id (integer):               The primary key/id
        email (string):             The User's email address.
        picture (string):           The url to the user's picture in the local
        filesystem or to the url of their profile picture from Google+

        items (relationship):       Defines the list of items the User has created.
        categories (relationship):  List of Categories created by the User.
        query (Query):              Shortcut for Querying the User table.

    '''
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(100), nullable=False)
    picture = Column(String(255), nullable=False)
    items = relationship(
        "Item",
        backref="User",
        cascade="save-update, delete, delete-orphan"
    )

    categories = relationship(
        "Category",
        backref="User",
        cascade="save-update, delete, delete-orphan"
    )

    @staticmethod
    def nameByID(user_id):
        '''Retrieve a user's name by their user id.

        Args:
            user_id (int): The primary key of the User in the table.

        Returns:
            string: The name of the user associated with the given user id.

        '''
        return User.query.filter_by(id=user_id).one().name

    @staticmethod
    def defaultTraits():
        '''The attribute names for the User Class.

        When creating the new user via a form, the default traits are used to
        describe the properties that a user needs to provide information for.

        Returns:
            A list containing the Traits for each attribute to be displayed
            in a form for creating an instance of the User class.
        '''
        return [
            TextTrait("name"),
            TextTrait("email"),
            ImageTrait("picture")
        ]

    @property
    def serialize(self):
        '''Serialize the properties of a User instance.

        Returns:
            dict: A Dictionary describing key attributes of a User instance

        '''
        user = {
            'User': {
                'id': self.id,
                'name': self.name,
                'email': self.email,
                'picture': self.picture,
                'Items':  {[i.serialize for i in self.items]}
            }
        }

        # Returns object data in form that's easy to serialize.
        return user

    def traits(self):
        '''The attributes and values of an instance of the User class.

        When presenting a view to a web user, the traits are parsed and
        displayed in a form or list in a format determined by the type
        of each attribute's associated Trait Class.

        Returns:
            A list containing the Traits for each attribute to be displayed
            in a view of a User instance.
        '''
        return [
            TextTrait("name", self.name),
            TextTrait("email", self.email),
            ImageTrait("picture", self.picture)
        ]


class Item(Base):
    '''Items in the Catalog are each created by a User and belong to a specific
    Category.


    Attributes:
        name (string):          The Item name.
        id (integer):           The primary key/id
        cat_id (integer)        The primary key/id for the Item's Category
        user_id (integer):      The primary key/id for the Item's creator
        picture (string):       The url to the item's picture in the local
        filesystem.

        description (string):   The Item's description.
        dateCreated (date):     The Date the Item was created.
        query (Query):          Shortcut for Querying the Item table.

    '''
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    cat_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    picture = Column(String)
    description = Column(String)
    name = Column(String(250), nullable=False)
    dateCreated = Column(Date)
    UniqueConstraint('cat_id', 'name', name='name_cat_id')

    query = session.query_property()

    @staticmethod
    def defaultTraits():
        '''The attribute names for the Item Class.

        When creating a new item via a form, the default traits are used to
        describe the properties that define an Item in the Catalog.

        Returns:
            Each Trait in the list describes a property of the Item to be
            created.  The Trait's type changes how it is rendered when
            presented to the user.
        '''

        return [
            ImageUploadTrait("picture"),
            TextTrait("name"),
            SelectTrait(
                "category",
                Category.categories()[0],
                Category.categories()
            ),
            DateTrait("created"),
            TextAreaTrait("description")
        ]


    @property
    def creator(self):
        '''The user name of the Item's creator.

        Returns:
            string: The name of the user that created the Item record.

        '''
        user = User.query.filter_by(id=self.user_id).one()
        return user.name

    @property
    def describe(self):
        '''Describe an Item by its name and the name of its Category.

        Returns:
            string: A descriptive string including the Item name and Category.

        Example:
            "Stick (Hockey)"
        '''
        return self.name + " (" + Category.findByID(self.cat_id).name + ")"


    def traits(self, isEdit=False):
        '''The attributes and values of an instance of the Item class.

        When presenting a view to a web user, the traits are parsed and
        displayed in a form or list in a format determined by the type
        of each attribute's associated Trait Class.

        Notes:
            Traits for generating a form for view and edit. An ImageUploadTrait
            is added for the edit view (specify isEdit as True).

        Args:
            isEdit (Boolean): True means an edit view will be generated
            from the Traits of the Item. False means that it will just display
            the values of each Trait. (no HTML Form)

        Returns:
            A list containing the Traits for each attribute to be displayed
            in a view of an Item instance.

            If isEdit is True a Trait will be included that allows the user to
            upload an Image for the item.  Otherwise, the Item attributes will
            be displayed as a list of property name/value.

        '''
        # Determine the category for this item.
        category = Category.query.filter_by(id=self.cat_id).one()

        # Rendering an Edit template.
        if isEdit is True:
            return [
                ImageTrait("picture", self.picture),
                ImageUploadTrait("upload"),
                TextTrait("name", self.name),
                SelectTrait(
                    "category",
                    category.name,
                    Category.categories()
                ),
                DateTrait("created", str(self.dateCreated)),
                TextAreaTrait("description", self.description)
            ]
        # Rendering a View Template.
        else:
            return [
                ImageTrait("picture", self.picture),
                TextTrait("name", self.name),
                SelectTrait(
                    "category",
                    category.name,
                    Category.categories()
                ),
                DateTrait("created", str(self.dateCreated)),
                TextAreaTrait("description", self.description)
            ]

    @property
    def serialize(self):
        '''Serialize the properties of a Item instance.

        Returns:
            dict: A Dictionary describing key attributes for an Item instance.

        '''
        item = {
            'Item': {
                'id': self.id,
                'creator': self.creator,
                'name': self.name,
                'picture': self.picture,
                'description': self.description,
                'cat_id': self.cat_id,
                'dateCreated': str(self.dateCreated)
            }
        }

        return item

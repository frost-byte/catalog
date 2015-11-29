from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Date,
    Numeric,
    Table,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import BLOB
from trait.Trait import (
    DateTrait,
    ImageTrait,
    ImageUploadTrait,
    TextTrait,
    TextAreaTrait,
    SelectTrait
)
from database import Base, session


class Category(Base):
    __tablename__ = "category"

    query = session.query_property()

    name = Column(String(80), unique = True, nullable = False)
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id'))

    items = relationship(
        "Item",
        backref="category",
        cascade="save-update, delete, delete-orphan"
    )

    # Find a Category by its name.
    @staticmethod
    def findByName(name):
        category = Category.query.filter_by(name = name).one()
        return category


    # Return a list of names for all categories
    @staticmethod
    def categories():
        return [c.name for c in Category.query.all()]


    @staticmethod
    def defaultTraits():
        return [TextTrait("name")]


    @staticmethod
    def findByID(id):
        category = Category.query.filter_by(id = id).one()
        return category


    @property
    def creator(self):
        user = User.query.filter_by(id = self.user_id).one()
        return user.name

    def traits(self):
        return [
            TextTrait( "name", self.name),
            TextTrait( "creator", self.creator)
        ]


    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id
        }


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    email = Column(String(100), nullable = False)
    picture = Column(String(255), nullable = False)
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
    def defaultTraits():
        return [
            TextTrait( "name"),
            TextTrait( "email"),
            ImageTrait( "picture")
        ]


    @property
    def serialize(self):
        itemsInfo = [i.serialize for i in self.items]

        # Returns object data in form that's easy to serialize.
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
            'items': itemsInfo
        }


    def traits(self):

        return [
            TextTrait("name", self.name),
            TextTrait("email", self.email),
            ImageTrait("picture", self.picture)
        ]


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key = True)
    cat_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    picture = Column(String)
    description = Column(String)
    name = Column(String(250), nullable = False)
    dateCreated = Column(Date)

    query = session.query_property()


    # Helps Generate a form for Creating a new Item: render a New Item template.
    @staticmethod
    def defaultTraits():
        return [
            ImageUploadTrait( "picture"),
            TextTrait( "name" ),
            SelectTrait(
                "category",
                Category.categories()[0],
                Category.categories()
            ),
            DateTrait( "created"),
            TextAreaTrait( "description" )
        ]

    # Traits for generating a form for view and edit. An ImageUploadTrait
    # is added for the edit view (specify isEdit as True).
    def traits(self, isEdit=False):
        category = Category.query.filter_by(id = self.cat_id).one()

        # Rendering an Edit template.
        if isEdit == True:
            return [
                ImageTrait( "picture", self.picture),
                ImageUploadTrait("upload"),
                TextTrait( "name", self.name ),
                SelectTrait(
                    "category",
                    category.name,
                    Category.categories()
                ),
                DateTrait( "created", str(self.dateCreated) ),
                TextAreaTrait( "description", self.description )
            ]
        # Rendering a View Template.
        else:
            return [
                ImageTrait( "picture", self.picture),
                TextTrait( "name", self.name ),
                SelectTrait(
                    "category",
                    category.name,
                    Category.categories()
                ),
                DateTrait( "created", str(self.dateCreated) ),
                TextAreaTrait( "description", self.description )
            ]


    @property
    def serialize(self):
        category  = Category.findByID(self.cat_id)
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'picture': self.picture,
            'description': self.description,
            'category': category.serialize(),
            'dateCreated': str(self.dateCreated),
        }

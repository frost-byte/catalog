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

from trait.Trait import DateTrait, ImageTrait, TextTrait, TextAreaTrait, SelectTrait
from database import Base, session


class Category(Base):
    __tablename__ = "category"

    query = session.query_property()

    name = Column(String(80), unique = True, nullable = False)
    id = Column(Integer, primary_key = True)
    items = relationship(
        "Item",
        backref="category",
        cascade="save-update, delete, delete-orphan"
    )

    # Need to add a way for a list of available categories to be added to a drop down list
    @staticmethod
    def findByName(name):
        category = Category.query.filter_by(name = name).one()
        return category


    # Return a list of names for all categories
    @staticmethod
    def categories():
        return [c.name for c in Category.query.all()]


    @property
    def traits(self):
        return [
            TextTrait( "name", self.name )
        ]


    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name
        }


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key = True)
    name = Column(String(250), nullable = False)
    items = relationship(
        "Item",
        backref="User",
        cascade="save-update, delete, delete-orphan")


    @property
    def serialize(self):
        profileInfo = self.profile.serialize
        adoptersInfo = [a.serialize for a in self.adopters]

        # Returns object data in form that's easy to serialize.
        return {
            'id': self.id,
            'name': self.name
        }


    @property
    def traits(self):

        return [
            TextTrait( "id", self.id ),
            TextTrait( "name", self.name ),
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

    @property
    def traits(self):
        category = Category.query.filter_by(id = self.cat_id).one()

        return [
            ImageTrait( "picture", self.picture),
            TextTrait( "name", self.name ),
            SelectTrait(
                "category",
                category.name,
                Category.categories()
            ),
            DateTrait( "created", self.dateCreated ),
            TextAreaTrait( "description", self.description )
        ]


    @property
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'picture': self.picture,
            'description': self.description,
            'category': self.gender,
            'dateCreated': str(self.dateOfBirth),
        }

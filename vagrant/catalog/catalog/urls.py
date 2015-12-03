'''Generate urls for a Flask App for CRUD and list operations.

This module is used to generate routes for a Flask application given:

1. The lowercase name of the class that corresponds to an SQLAlchemy Data
Model.

2. The id or primary key for an instance of that class in the database.

'''
from flask import url_for


class Urls(object):
    """Generate a series of urls that are paths to routes for listing, viewing,
    editing, deleting or creating instances of a specified class.

    Notes:
        see http://flask.pocoo.org/docs/0.10/templating/#context-processors
        for more about context processors

    Args:
        suffix (string): Lowercase name of a class in the database.
            (i.e. category, user, item)

        key (integer): A primary key value in the database that matches
            a record for the class in suffix,

    Attributes:
        suffix (string): Lowercase representation of a class in the database.
            (Category, User, Item)

        key (integer): A primary key value in the database that matches
            a record for the class in suffix,

        Each of these routes refers to an operation on a record from the database
        table that matches the value of suffix and primary key in key.

        deleteUrl (string):     root/suffix/key/delete
        editUrl (string):       root/suffix/key/edit
        viewUrl (string):       root/suffix/key
        newUrl (string):        root/suffix/add
        listUrl (string):       root/suffix + "s"
        listString (string):    "Back to Suffix" + "s."
 
   Examples:
        For an app with /catalog as the root path/url,

        urls = makeUrls('item', 1)
        urls would return an object with the following properties/values.

        urls.suffix         "item"
        urls.key            1
        urls.deleteUrl      /catalog/item/1/delete
        urls.editUrl        /catalog/item/1/edit
        urls.viewUrl        /catalog/item/1
        urls.newUrl         /catalog/item/add
        urls.listUrl        /catalog/items
        urls.listString     "Back to Items."

    """

    def __init__(self, suffix, object_id=0):
        """Generate a series of urls that are paths to routes for listing, viewing,
        editing, deleting or creating instances of a specified class.


        Args:
            suffix (string): Lowercase name of a class in the database.
                (i.e. category, user, item)

            key (integer): A primary key value in the database that matches
                a record for the class in suffix,

        Returns:
            A Urls instance with members populated with routes to interact
            with a record in the database.

        """
        self._suffix = suffix.title()

        # The primary key or id of the data record
        self._key = object_id

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    @property
    def suffix(self):
        return "%s" % self._suffix

    @suffix.setter
    def suffix(self, value):
        self._suffix = value

    @property
    def deleteUrl(self):
        return url_for("delete" + self._suffix, key=self._key)

    @property
    def editUrl(self):
        return url_for("edit" + self._suffix, key=self._key)

    @property
    def newUrl(self):
        return url_for("new" + self._suffix)

    @property
    def viewUrl(self):
        return url_for("view" + self._suffix, key=self._key)

    @property
    def listUrl(self):
        return url_for("list" + self._suffix)

    @property
    def listString(self):
        return "Back to " + self._suffix.title() + "s."

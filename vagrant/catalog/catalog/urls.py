from flask import url_for

class Urls(object):

    def __init__(self, suffix, object_id=0):
        self._suffix = suffix.title()
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
        return url_for("delete" + self._suffix, key = self._key)


    @property
    def editUrl(self):
        return url_for("edit" + self._suffix, key = self._key)


    @property
    def newUrl(self):
        return url_for("new" + self._suffix)


    @property
    def viewUrl(self):
        return url_for("view" + self._suffix, key = self._key)


    @property
    def listUrl(self):
        return url_for("list" + self._suffix)


    @property
    def listString(self):
        return "Back to " + self._suffix.title() + "s."

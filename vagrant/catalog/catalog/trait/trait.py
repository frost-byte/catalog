from abc import ABCMeta, abstractmethod
import datetime

class Trait(object):
    inputType = ""
    inputTemplate = ""
    outputTemplate = ""

    # All traits are rendered out as table rows
    # The first table data contains the label describing what is contained
    # in the second table data.
    traitTemplate = '''
                <tr class="trait">
                    <td>{0}</td>
                    <td>
                        {1}
                    </td>
                </tr>'''


    __metaclass__ = ABCMeta


    @abstractmethod
    def isImage(self):
        pass


    @abstractmethod
    def asInputElement(self, formName, withValue = False):
        pass


    @abstractmethod
    def asOutputElement(self):
        pass


class TextTrait(Trait):

    inputTemplate = '''<input type="{0}" name="{1}" form="{2}" value="{3}">'''

    def __init__(self, name, value=""):
        self.inputType = "text"
        self.name = name
        self.value = value


    def isImage(self):
        return False


    def asInputElement(self, formName, withValue = False):

        value = ""

        if withValue == True:
            value = self.value

        element =  self.inputTemplate.format(
                self.inputType,
                self.name,
                formName,
                value
            )
        return self.traitTemplate.format(self.name.title(), element)


    def asOutputElement(self):
        return self.traitTemplate.format(self.name.title(), self.value)


class ImageTrait(Trait):
    inputTemplate = '''<input type="{0}" name="{1}" form="{2}" value="{3}">'''
    outputTemplate = '''<img src="{0}">'''


    def __init__(self, name, url=""):
        self.name = name
        self.url = url


    def isImage(self):
        return True


    def asInputElement(self, formName, withValue = False):
        value = ""

        if withValue == True:
            value = self.url

        element =  self.inputTemplate.format(
                "text",
                self.name,
                formName,
                value
            )
        return self.traitTemplate.format(self.name.title(), element)


    def asOutputElement(self):
        return self.outputTemplate.format(self.url)


class ImageUploadTrait(Trait):
    inputTemplate = '''<input type="{0}" name="{1}" form="{2}">'''

    def __init__(self, name):
        self.name = name

    def isImage(self):
        return True


    def asInputElement(self, formName, withValue = False):

        element =  self.inputTemplate.format(
                "file",
                self.name,
                formName
            )
        return self.traitTemplate.format(self.name.title(), element)


    def asOutputElement(self):
        return "<--! ImageUploadTrait not used for output -->"


class TextAreaTrait(Trait):
    inputTemplate = '''<textarea name="{0}" form="{1}">{2}</textarea>'''

    def __init__(self, name, value=""):
        self.name = name
        self.value = value


    def isImage(self):
        return False


    def asInputElement(self, formName, withValue = False):

        value = ""

        if withValue == True:
            value = self.value

        element = self.inputTemplate.format(
            self.name,
            formName,
            value
        )
        return self.traitTemplate.format(self.name.title(), element)


    def asOutputElement(self):
        return self.traitTemplate.format(self.name.title(), self.value)



class SelectTrait(Trait):
    selectTemplate = '''<select name="{0}" form="{1}">{2}
                        </select>'''

    optionTemplate = '''
                            <option value="{0}"{1}>{2}</option>'''

    '''
        Arguments:
            name: The label for the select element
            value: A string representing the value of the currently selected option.

            options: A list of strings for the options in the select
    '''
    def __init__(self, name, value, options):
        self.name = name
        self.value = value
        self.options = options


    def isImage(self):
        return False


    # When displaying the select as a form element - for retrieving input
    def asInputElement(self, formName, withValue = False):
        element =  self.inputTemplate.format(
                self.inputType,
                self.name,
                formName,
                self.value
            )

        options = ""

        # Compile options first...
        for option in self.options:
            selected = ""

            # The value will be the selected option
            if option == self.value:
                selected = " selected"

            options += self.optionTemplate.format(
                option,
                selected,
                option.title()
            )


        # Now combine the options with the select
        element = self.selectTemplate.format(
            self.name,
            formName,
            options
        )

        return self.traitTemplate.format(self.name.title(), element)


    def asOutputElement(self):
        return self.traitTemplate.format(self.name.title(), self.value)


class DateTrait(Trait):
    inputTemplate = '''<input type="{0}" name="{1}" form="{2}" value="{3}">'''


    def __init__(self, name, value=str(datetime.date.today())):
        self.name = name
        self.value = value
        print "DateTrait: value = %s" % self.value


    def isImage(self):
        return False


    def asInputElement(self, formName, withValue = False):

        element = self.inputTemplate.format(
            "date",
            self.name,
            formName,
            self.value
        )

        return self.traitTemplate.format(self.name.title(), element)


    def asOutputElement(self):
        return self.traitTemplate.format(self.name.title(), self.value)

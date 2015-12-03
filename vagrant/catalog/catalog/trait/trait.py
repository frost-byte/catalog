'''
A Trait module for generating HTML forms and views.

Default Traits can be specified for plain views of properties that don't have
a value assigned to them, yet.

The asOutputElement method is used for displaying trait values.
The asInputElement method is used for creating html forms from the trait's attributes.

'''
from abc import ABCMeta, abstractmethod
import datetime

class Trait(object):
    '''Abstract Base Class that defines the Interface and a few attributes of
    all Derived Traits.

    Notes:
        When asInputElement is called for a Trait, and the generated HTML Form
        is processed as part of a Request, then the Trait's name is used
        as a key to retrieve it's value from the Request's form.

    Attributes:
        inputType (string):         The html input type of the trait..
        inputTemplate (string):     Input Template used when the trait can
            receive input.
        outputTemplate (string):    The output template when the trait is only
            viewed.

        traitTemplate (string):     The base template that the input or output
            templates are applied.  It represents an HTML table row with two
            table data elements.  One for the Trait's property name and the 
            other for it's value.
    '''
    inputType = ""
    inputTemplate = ""
    outputTemplate = ""
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
        '''Does this Trait refer to an Image element?

        Returns:
            Boolean: True if the Trait applies to an Image, otherwise False.
        '''
        pass


    @abstractmethod
    def asInputElement(self, formName, withValue = False):
        '''Render the Trait as an HTML element as part of a form that receives
        input.

        Args:
            formName (string):      The HTML form's name attribute.
                Each trait's html element is added to a table outside it's
                form.  This argument binds the Trait's element to the form.

            withValue (Boolean):    A form for a new object will not have any
                values.  But a form that is for editing an existing object will.

        Returns:
            string: The formatted output of the combination of the
                inputTemplate and traitTemplate.
        '''
        pass


    @abstractmethod
    def asOutputElement(self):
        '''Render the Trait as an HTML element as a view that does not receive
        any input.

        Returns:
            string: The formatted output of the combination of the
                outputTemplate and traitTemplate.
        '''
        pass


class TextTrait(Trait):
    '''A Trait for a property that can be represented as a Text input or
    unalterable string value in an html element.

    Attributes:
        inputType (string):         This will be a 'text' input element.
        inputTemplate (string):     Generate's an html input of type 'text'
        name (string):              The property name or label
        value (string):             The value associated with the property.

    '''

    inputTemplate = '''<input type="{0}" name="{1}" form="{2}" value="{3}">'''

    def __init__(self, name, value=""):
        self.inputType = "text"
        self.name = name
        self.value = value


    def isImage(self):
        '''Does this Trait refer to an Image element?

        Returns:
            Boolean: A text input is not an image, so False.
        '''
        return False


    def asInputElement(self, formName, withValue = False):
        '''Render the Trait as a text input in as part of an HTML form.

        Args:
            formName (string):      The HTML form's name attribute.
            withValue (Boolean):    A form for a new object will not have any
                values.  But a form that is for editing an existing object will.

        Returns:
            string: The formatted output of the combination of the
                inputTemplate and traitTemplate.
        '''
        value = ""

        if withValue == True:
            # Add the trait's value to the second data element
            value = self.value

        # Generate the html for the text input.
        element =  self.inputTemplate.format(
                self.inputType,
                self.name,
                formName,
                value
            )

        # Inject the text input element and it's value into a table row.
        return self.traitTemplate.format(self.name.title(), element)


    def asOutputElement(self):
        """Refer to :py:method:`~Trait.asOutputElement`"""
        return self.traitTemplate.format(self.name.title(), self.value)


class ImageTrait(Trait):
    '''A Trait that represents an HTML image element.

    Attributes:
        inputType (string):     This will be a 'text' input element.
        inputTemplate (string): Generate's an html input of type 'text'
        name (string):          The property name for the element. Used
            to retrieve data from the form in a request.
        url (string):           The url associated with the image.
    '''

    inputTemplate = '''<input type="{0}" name="{1}" form="{2}" value="{3}">'''
    outputTemplate = '''<img src="{0}" class="img-responsive">'''


    def __init__(self, name, url=""):
        '''Create an ImageTrait given it's properties name and url.

        Args:
            name (string): The name of the property for the label and key in
                the form contained in the request.

            url (string): Optional value that specifies the url of the image
                in the local file system or on the web.

        Returns:
            ImageTrait: An ImageTrait containing information associated with a
                property.
        '''
        self.name = name
        self.url = url


    def isImage(self):
        '''Does this Trait refer to an Image element?

        Returns:
            Boolean: This will be an image element, so True.
        '''
        return True


    def asInputElement(self, formName, withValue = False):
        '''Render the Trait as a text input in as part of an HTML form.
        Manually enter the URL for an image, as opposed to uploading it.

        Args:
            formName (string):      The HTML form's name attribute.
            withValue (Boolean):    A form for a new object will not have any
                values.  But a form that is for editing an existing object will.

        Returns:
            string: The formatted output of the combination of the
                inputTemplate and traitTemplate.
        '''
        value = ""

        if withValue == True:
            # Add the trait's value to the second data element
            value = self.url

        # Generate the html for the text input.
        element =  self.inputTemplate.format(
                "text",
                self.name,
                formName,
                value
            )
        # Inject the results into a table row and return the result.
        return self.traitTemplate.format(self.name.title(), element)


    def asOutputElement(self):
        """Refer to :py:method:`~Trait.asOutputElement`"""
        return self.outputTemplate.format(self.url)


class ImageUploadTrait(Trait):
    '''A Trait that represents an HTML element for uploading a image file.

    Notes:
        This could be generalized into just an UploadTrait and apply to
        files of any type. This Trait is only used for Input.  An
        ImageTrait should be used for outputting an image.

    Attributes:
        inputType (string):     This will be a 'text' input element.
        inputTemplate (string): Generate's an html input of type 'text'
        name (string):          The property name for the element. Used
            to retrieve data from the form in a request.
    '''
    inputTemplate = '''<input type="{0}" name="{1}" form="{2}">'''

    def __init__(self, name):
        '''Create an ImageUploadTrait given the name of it's property/label

        Args:
            name (string): The name of the property/label and key in
                the form contained in the request.

        Returns:
            Trait: An ImageUploadTrait
        '''
        self.name = name


    def isImage(self):
        '''Does this Trait refer to an Image element?

        Returns:
            Boolean: This is not displayed as an image but as a file upload
            input, so False.
        '''
        return False


    def asInputElement(self, formName, withValue = False):
        '''Render as a file upload element in an HTML form.

        Prompts the user to choose a file on their system to upload.

        Args:
            formName (string):      The HTML form's name attribute.
            withValue (Boolean):    A form for a new object will not have any
                values.  But a form that is for editing an existing object will.

        Returns:
            string: Formatted HTML table row containing two table data elements
                containing the property name in a button and an empty
                text element that will hold the file's name after the user
                uploads an image file.

        '''

        # Return the File upload element with the button containing the
        # property name for the input.
        element =  self.inputTemplate.format(
                "file",
                self.name,
                formName
            )
        return self.traitTemplate.format(self.name.title(), element)


    def asOutputElement(self):
        '''An Image Upload element would not be presented as an Image.

        Returns:
            string: An HTML comment describing the Output Usage for
                ImageUploadTrait
        '''
        return "<--! ImageUploadTrait not used for output -->"


class TextAreaTrait(Trait):
    '''A Trait for a multi-line text property that is rendered as a TextArea
    HTML element.

    Attributes:
        inputTemplate (string):     Generate's an html 'textarea' input
        name (string):              The label or property name.
        value (string):             The value contained in the textarea.

    '''

    inputTemplate = '''<textarea name="{0}" form="{1}">{2}</textarea>'''

    def __init__(self, name, value=""):
        '''Create a TextAreaTrait given it's property name and value.

        Args:
            name (string): The name of the property for the label and key in
                the form contained in the request.

            value (string): The value containing either an empty string or
                long/detailed description of something.

        Returns:
            Trait: A TextAreaTrait containing information associated with a
                property.
        '''
        self.name = name
        self.value = value


    def isImage(self):
        '''Does this Trait refer to an Image element?

        Returns:
            Boolean: A TextArea is not an image, so False.
        '''
        return False


    def asInputElement(self, formName, withValue = False):
        '''Render as a textarea element in an HTML form.

        Provides an area for a longer text description of a property.

        Args:
            formName (string):      The HTML form's name attribute.
            withValue (Boolean):    A form for a new object will not have any
                values.  But a form that is for editing an existing object will.

        Returns:
            string: Formatted HTML table row containing two table data
                elements. One for the property name as a label and another that
                contains the Trait's value (or nothing) in a textarea HTML
                element.

        '''
        value = ""

        if withValue == True:
            value = self.value

        # Generate a label and a textarea in two table data elements of a row
        # in HTML and return the resulting string.
        element = self.inputTemplate.format(
            self.name,
            formName,
            value
        )
        return self.traitTemplate.format(self.name.title(), element)


    def asOutputElement(self):
        """Refer to :py:method:`~Trait.asOutputElement`"""
        return self.traitTemplate.format(self.name.title(), self.value)



class SelectTrait(Trait):
    '''A Trait for a property that is best represented by a a Select Element
    with a Dropdown list of different options to choose from.

    Attributes:
        selectTemplate (string):    Generate's an html 'select' input
        optionTemplate (string):    A template string that represents one
            option element contained in a select element.
        name (string):              The label or property name.
        value (string):             The string value of the currently selected
            option.
        options (list):             A list of strings describing the value for
            each option displayed in the drop down list of the select element.

    '''
    selectTemplate = '''<select name="{0}" form="{1}">{2}
                        </select>'''

    optionTemplate = '''
                            <option value="{0}"{1}>{2}</option>'''

    def __init__(self, name, value, options):
        '''Create a SelectTrait given it's property name and value.

        Args:
            name (string): The name of the property for the label and key in
                the form contained in the request.

            value (string): The value containing either an empty string or
                long/detailed description of something.

        Returns:
            Trait: A SelectTrait containing options, possibly including a
                currently selected option, for a property.

        '''
        self.name = name
        self.value = value
        self.options = options


    def isImage(self):
        '''Does this Trait refer to an Image element?

        Returns:
            Boolean: A Select element is not an image, so False.
        '''
        return False


    def asInputElement(self, formName, withValue = False):
        '''Render as a Select element containing option elements in an HTML
        form.

        Provides an dropdown list of options to choose from return the selected
        value as part of a form in a Request.

        Args:
            formName (string):      The HTML form's name attribute.
            withValue (Boolean):    A form for a new object will not have any
                values.  But a form that is for editing an existing object will.

        Returns:
            string: Formatted HTML table row containing two table data
                elements. One for the property name as a label and another that
                contains the the Select with a dropdown list of options to choose
                from.

        '''
        options = ""

        # Compile the options for the dropdown list first...
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

        # Return the final result.
        return self.traitTemplate.format(self.name.title(), element)


    def asOutputElement(self):
        """Refer to :py:method:`~Trait.asOutputElement`"""
        return self.traitTemplate.format(self.name.title(), self.value)


class DateTrait(Trait):
    '''A Trait for a property that is best represented as a date that includes
    the year, month and day.

    Attributes:
        inputTemplate (string): Template for Generating an html 'date' input.
        name (string):          The label or property name.
        value (string):         The date value associated with the property.

    '''
    inputTemplate = '''<input type="date" name="{0}" form="{1}" value="{2}">'''


    def __init__(self, name, value=str(datetime.date.today())):
        '''Create a DateTrait given it's property name and value as a Date.

        Args:
            name (string): The name of the property for the label and key in
                the form contained in the request.

            value (string): A Date

        Returns:
            Trait: A DateTrait containing options, possibly including a
                currently selected option, for a property.

        '''
        self.inputType = "date"
        self.name = name
        self.value = value


    def isImage(self):
        '''Does this Trait refer to an Image element?

        Returns:
            Boolean: A Date input element is not an image, so False.
        '''
        return False


    def asInputElement(self, formName, withValue = False):
        '''Render as an HTML date input element.

        Provides a calender like functionality or manually inputting the
        year, month and day.

        Args:
            formName (string):      The HTML form's name attribute.
            withValue (Boolean):    A Date Trait always presents a date value,
                either a default that is today's date, or one passed in.

        Returns:
            string: Formatted HTML table row containing two table data
                elements. One for the property name as a label and another that
                contains the Date input set to today's date or the date passed
                during the creation of the object.

        '''

        # Generate the Date input element.
        element = self.inputTemplate.format(
            self.name,
            formName,
            self.value
        )

        # Combine a label and the Date input element into a table row and
        # return the result.
        return self.traitTemplate.format(self.name.title(), element)


    def asOutputElement(self):
        """Refer to :py:method:`~Trait.asOutputElement`"""
        return self.traitTemplate.format(self.name.title(), self.value)

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

    .. note::
        When asInputElement is called for a Trait, and the generated HTML Form
        is processed as part of a Request, then the Trait's name is used
        as a key to retrieve it's value from the Request's form.

    :param string inputType: The html input type of the trait.
    :param string inputTemplate: Input Template used when the trait can
        receive input.
    :param string outputTemplate: The output template when the trait is only
        viewed.

    :param str traitTemplate: The base template applied to the input or
        output templates.  It represents an HTML table row with two
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

        :returns: True if the Trait applies to an Image, otherwise False.
        :rtype: Boolean
        '''
        pass


    @abstractmethod
    def asInputElement(self, formName, withValue = False):
        '''Render the Trait as an HTML element as part of a form that receives
        input.

        :param string formName: The HTML form's name attribute.
            Each trait's html element is added to a table outside it's
            form.  This argument binds the Trait's element to the form.

        :param Boolean withValue: A form for a new object will not have any
            values.  But a form that is for editing an existing object will.

        :returns: The formatted output of the combination of the
            inputTemplate and traitTemplate.
        :rtype: string
        '''
        pass


    @abstractmethod
    def asOutputElement(self):
        '''Render the Trait as an HTML element as a view that does not receive
        any input.

        :returns: The formatted output of the combination of the
            outputTemplate and traitTemplate.
        :rtype: string
        '''
        pass


class TextTrait(Trait):
    '''A Trait for a property that can be represented as a Text input or
    unalterable string value in an html element.

    :param string inputType: This will be a 'text' input element.
    :param string inputTemplate: Generate's an html input of type 'text'
    :param string name: The property name or label
    :param string value: The value associated with the property.

    '''

    inputTemplate = '''<input type="{0}" name="{1}" form="{2}" value="{3}">'''

    def __init__(self, name, value=""):
        self.inputType = "text"
        self.name = name
        self.value = value


    def isImage(self):
        '''Does this Trait refer to an Image element?

        :returns: A text input is not an image, so False.
        :rtype: Boolean
        '''
        return False


    def asInputElement(self, formName, withValue = False):
        '''Render the Trait as a text input in as part of an HTML form.

        :param string formName: The HTML form's name attribute.
        :param Boolean withValue: A form for a new object will not have any
            values.  But a form that is for editing an existing object will.

        :returns: The formatted output of the combination of the
            inputTemplate and traitTemplate.
        :rtype: string
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
        """Refer to :py:meth:`~Trait.asOutputElement`"""
        return self.traitTemplate.format(self.name.title(), self.value)


class ImageTrait(Trait):
    '''A Trait that represents an HTML image element.

    :param string inputType: This will be a 'text' input element.
    :param string inputTemplate: Generate's an html input of type 'text'
    :param string name: The property name for the element. Used
        to retrieve data from the form in a request.
    :param string url: The url associated with the image.
    '''

    inputTemplate = '''<input type="{0}" name="{1}" form="{2}" value="{3}">'''
    outputTemplate = '''<img src="{0}" class="img-responsive">'''


    def __init__(self, name, url=""):
        '''Create an ImageTrait given it's properties name and url.

        :param string name: The name of the property for the label and key in
            the form contained in the request.
        :param string url: Optional value that specifies the url of the image
            in the local file system or on the web.
        :returns: An ImageTrait containing information associated with a
            property.
        :rtype: ImageTrait
        '''
        self.name = name
        self.url = url


    def isImage(self):
        '''Does this Trait refer to an Image element?

        :returns: This will be an image element, so True.
        :rtype: Boolean
        '''
        return True


    def asInputElement(self, formName, withValue = False):
        '''Render the Trait as a text input in as part of an HTML form.
        Manually enter the URL for an image, as opposed to uploading it.

        :param string formName: The HTML form's name attribute.
        :param Boolean withValue: A form for a new object will not have any
            values.  But a form that is for editing an existing object will.
        :returns: The formatted output of the combination of the inputTemplate
            and traitTemplate.
        :rtype: string
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
        """Refer to :py:meth:`~Trait.asOutputElement`"""
        return self.outputTemplate.format(self.url)


class ImageUploadTrait(Trait):
    '''A Trait that represents an HTML element for uploading a image file.

    .. note::
        This could be generalized into just an UploadTrait and apply to
        files of any type. This Trait is only used for Input.  An
        ImageTrait should be used for outputting an image.

    :param string inputType: This will be a 'text' input element.
    :param string inputTemplate: Generate's an html input of type 'text'
    :param string name: The property name for the element. Used
        to retrieve data from the form in a request.
    '''
    inputTemplate = '''<input type="{0}" name="{1}" form="{2}">'''

    def __init__(self, name):
        '''Create an ImageUploadTrait given the name of it's property/label

        Args:
            name (string): The name of the property/label and key in
                the form contained in the request.

        :returns: An ImageUploadTrait
        :rtype: Trait
        '''
        self.name = name


    def isImage(self):
        '''Does this Trait refer to an Image element?

        :returns: This is not displayed as an image but as a file upload
            input, so False.
        :rtype: Boolean
        '''
        return False


    def asInputElement(self, formName, withValue = False):
        '''Render as a file upload element in an HTML form.

        Prompts the user to choose a file on their system to upload.

        :param string formName: The HTML form's name attribute.
        :param Boolean withValue: A form for a new object will not have any
            values.  But a form that is for editing an existing object will.
        :returns: Formatted HTML table row containing two table data elements
            containing the property name in a button and an empty text element
            that will hold the file's name after the user uploads an image
            file.
        :rtype: string

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

        :returns: An HTML comment describing the Output Usage for
            ImageUploadTrait
        :rtype: string
        '''
        return "<--! ImageUploadTrait not used for output -->"


class TextAreaTrait(Trait):
    '''A Trait for a multi-line text property that is rendered as a TextArea
    HTML element.

    :param inputTemplate: Generate's an html 'textarea' input.
    :param name: The label or property name.
    :param value: The value contained in the textarea.
    :type inputTemplate: string
    :type name: string
    :type value: string
    '''

    inputTemplate = '''<textarea name="{0}" form="{1}">{2}</textarea>'''

    def __init__(self, name, value=""):
        '''Create a TextAreaTrait given it's property name and value.

        :param str name: The name of the property for the label and key in
            the form contained in the request.
        :param str value: The value containing either an empty string or
            long/detailed description of something.
        :returns: A TextAreaTrait containing information associated with a
            property.
        :rtype: TextAreaTrait

        '''
        self.name = name
        self.value = value


    def isImage(self):
        '''Does this Trait refer to an Image element?

        :returns: A TextArea is not an image, so False.
        :rtype: Boolean

        '''
        return False


    def asInputElement(self, formName, withValue = False):
        '''Render as a textarea element in an HTML form.

        Provides an area for a longer text description of a property.

        :param formName: The HTML form's name attribute.
        :param withValue: True builds a form for creating a new object
            that will not have any values.  False, a form that is for
            editing an existing object will.
        :type formName: string
        :type withValue: Boolean
        :return string: HTML that defines a table row containing two table data
            elements. One for the property name as a label and another that
            contains the Trait's value (or nothing) in a textarea HTML element.

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
        """Refer to :py:meth:`~Trait.asOutputElement`"""
        return self.traitTemplate.format(self.name.title(), self.value)



class SelectTrait(Trait):
    '''A Trait for a property that is best represented by a Select Element
    with a Dropdown list of different options to choose from.

    :param string selectTemplate: Generate's an html 'select' input.
    :param string optionTemplate: A template string that represents one
        option element contained in a select element.
    :param string name: The label or property name.
    :param string value: The string value of the currently selected
        option.
    :param list options: A list of strings describing the value for
        each option displayed in the drop down list of the select element.

    '''
    selectTemplate = '''<select name="{0}" form="{1}">{2}
                        </select>'''

    optionTemplate = '''
                            <option value="{0}"{1}>{2}</option>'''

    def __init__(self, name, value, options):
        '''Create a SelectTrait given it's property name and value.

        :param string name: The name of the property for the label and key in
            the form contained in the request.
        :param string value: The value containing either an empty string or
            long/detailed description of something.
        :returns: A SelectTrait containing options, possibly including a
            currently selected option, for a property.
        :rtype: Trait

        '''
        self.name = name
        self.value = value
        self.options = options


    def isImage(self):
        '''Does this Trait refer to an Image element?

        :returns: A Select element is not an image, so False.
        :rtype: Boolean
        '''
        return False


    def asInputElement(self, formName, withValue = False):
        '''Render as a Select element containing option elements in an HTML
        form.

        Provides an dropdown list of options to choose from return the selected
        value as part of a form in a Request.

        :param string formName: The HTML form's name attribute.
        :param Boolean withValue: A form for a new object will not have any
            values.  But a form that is for editing an existing object will.
        :returns: Formatted HTML table row containing two table data
            elements. One for the property name as a label and another that
            contains the the Select with a dropdown list of options to choose
            from.
        :rtype: string

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
        """Refer to :py:meth:`~Trait.asOutputElement`"""
        return self.traitTemplate.format(self.name.title(), self.value)


class DateTrait(Trait):
    '''A Trait for a property that is best represented as a date that includes
    the year, month and day.

    :param string inputTemplate: Template for Generating an html 'date' input.
    :param string name: The label or property name.
    :param string value: The date value associated with the property.

    '''
    inputTemplate = '''<input type="date" name="{0}" form="{1}" value="{2}">'''


    def __init__(self, name, value=str(datetime.date.today())):
        '''Create a DateTrait given it's property name and value as a Date.

        :param string name: The name of the property for the label and key in
            the form contained in the request.
        :param string value: A Date
        :returns: A DateTrait containing options, possibly including a
            currently selected option, for a property.
        :rtype: Trait

        '''
        self.inputType = "date"
        self.name = name
        self.value = value


    def isImage(self):
        '''Does this Trait refer to an Image element?

        :returns: A Date input element is not an image, so False.
        :rtype: Boolean
        '''
        return False


    def asInputElement(self, formName, withValue = False):
        '''Render as an HTML date input element.

        Provides a calender like functionality or manually inputting the
        year, month and day.

        :param string formName: The HTML form's name attribute.
        :param Boolean withValue: A Date Trait always presents a date value,
            either a default that is today's date, or one passed in.
        :returns: Formatted HTML table row containing two table data
            elements. One for the property name as a label and another that
            contains the Date input set to today's date or the date passed
            during the creation of the object.
        :rtype: string

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
        """Refer to :py:meth:`~Trait.asOutputElement`"""
        return self.traitTemplate.format(self.name.title(), self.value)

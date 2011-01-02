import datetime

class FieldBase(object):
    """Base class for all field types"""

    def __init__(self, source=None):
        """Create a new instance of a field class.

        Keyword arguments:
        source -- the key holding the value for this field to use in the
        source data. If not supplied, the name of the class property this
        instance is assigned to will be used.
        """
        self.source = source

    def populate(self, data):
        """Set the value or values wrapped by this field"""
        self.data = data

    def to_python(self):
        return self.data


class PassField(FieldBase):
    pass


class CharField(FieldBase):
    """Field to represent a simple Unicode string value"""

    def to_python(self):
        """Convert the data supplied to the `populate` method to a Unicode string"""
        if self.data is None:
            return ''
        return unicode(self.data)


class IntegerField(FieldBase):
    """Field to represent an integer value"""

    def to_python(self):
        """Convert the data supplied to the `populate` method to an integer"""
        if self.data is None:
            return 0
        return int(self.data)


class BooleanField(FieldBase):
    """Field to represent a boolean"""

    def to_python(self):
        """Convert the data supplied to the `populate` method to a boolean value.

        The string "True" (case insensitive) will be converted
        to True, as will any positive integers.
        """
        if isinstance(self.data, basestring):
            return self.data.strip().lower() == 'true'
        if isinstance(self.data, int):
            return self.data > 0
        return bool(self.data)


class DateTimeField(FieldBase):
    """Field to represent a datetime"""

    def __init__(self, format, **kwargs):
        super(DateTimeField, self).__init__(**kwargs)
        self.format = format

    def to_python(self):
        if self.data is None:
            return None
        return datetime.datetime.strptime(str(self.data), self.format)


class DateField(DateTimeField):
    """Field to represent a datetime.date"""

    def to_python(self):
        datetime = super(DateField, self).to_python()
        return datetime.date()


class TimeField(DateTimeField):
    """Field to represent a datetime.time"""

    def to_python(self):
        datetime = super(TimeField, self).to_python()
        return datetime.time()


class WrappedObjectField(FieldBase):
    """Superclass for any fields that wrap an object"""

    def __init__(self, wrapped_class, **kwargs):
        self._wrapped_class = wrapped_class
        FieldBase.__init__(self, **kwargs)


class ModelField(WrappedObjectField):
    """Field containing a model instance"""

    def to_python(self):
        data = self.data or {}
        return self._wrapped_class(data)


class ModelCollectionField(WrappedObjectField):
    """Field containing a list of model instances"""

    def to_python(self):
        data = self.data or []
        return [self._wrapped_class(item) for item in data]


class FieldCollectionField(WrappedObjectField):
    """Field containing a list of fields"""

    def to_python(self):
        data = self.data or []
        converted = []
        for item in data:
            field_instance = self._wrapped_class()
            field_instance.populate(item)
            converted.append(field_instance.to_python())
        return converted


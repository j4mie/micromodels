from fields import FieldBase

class Model(object):

    class __metaclass__(type):
        def __init__(cls, name, bases, attrs):
            cls._fields = {}
            for name, value in attrs.items():
                if isinstance(value, FieldBase):
                    cls._fields[name] = value

    def __init__(self, data):
        """Create an instance of the model subclass. The constructor should
        be passed a dictionary of data to provide values for its fields.

        For each field defined on the class (and stored in the _fields
        property by the metaclass), a property is created on the instance
        which contains the converted value from the source data.
        """
        for name, field in self._fields.items():
            key = field.source or name
            field.populate(data.get(key))
            value = field.to_python()
            setattr(self, name, value)
        self._data = data

try:
    import json
except ImportError:
    import simplejson as json

from fields import FieldBase

class Model(object):

    class __metaclass__(type):

        def __init__(cls, name, bases, attrs):
            cls._fields = {}
            for key, value in attrs.iteritems():
                if isinstance(value, FieldBase):
                    cls._fields[key] = value
                    delattr(cls, key)

    def __init__(self, data):
        """Create an instance of the model subclass. The constructor should
        be passed a dictionary of data to provide values for its fields.

        For each field defined on the class, a property is created on the
        instance which contains the converted value from the source data.
        """
        for name, field in self._fields.iteritems():
            key = field.source or name
            field.populate(data.get(key))

    def __getattr__(self, key):
        return self._fields[key].get()


class JSONModel(Model):

    def __init__(self, json_str):
        data = json.decode(json_str)
        super(JSONModel, self).__init__(data)

    def __setattr__(self, key, value):
        if key in self._data:
            self._data[key] = data
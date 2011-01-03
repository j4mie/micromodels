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

    def __init__(self, data):
        """Create an instance of the model subclass. The constructor should
        be passed a dictionary of data to provide values for its fields.

        For each field defined on the class, a property is created on the
        instance which contains the converted value from the source data.
        """
        for name, field in self._fields.iteritems():
            key = field.source or name
            field.populate(data.get(key))
            setattr(self, name, field.to_python())

class JSONModel(Model):

    def __init__(self, json_data):
        super(JSONModel, self).__init__(json.loads(json_data))

    def to_dict(self, serial=False):
        keys = (k for k in self.__dict__.keys() if k in self._fields.keys())

        if serial:
            D = dict((key, self._fields[key].to_serial(getattr(self, key)))
                     for key in keys)
        else:
            D = dict((key, getattr(self, key)) for key in keys)
        return D

    def to_json(self):
        return json.dumps(self.to_dict(serial=True))

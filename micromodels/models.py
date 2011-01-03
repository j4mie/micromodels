try:
    import json
except ImportError:
    import simplejson as json

from fields import FieldBase

class Model(object):

    class __metaclass__(type):
        '''Creates the metaclass for Model. The main function of this metaclass
        is to move all of fields into the _fields variable on the class.
        '''
        def __init__(cls, name, bases, attrs):
            cls._clsfields = {}
            for key, value in attrs.iteritems():
                if isinstance(value, FieldBase):
                    cls._clsfields[key] = value

    def __init__(self, data, is_json=False):
        """Create an instance of the Model class. The constructor should
        be passed a dictionary of data to provide values for its fields. If
        is_json is set to True, the method will attempt to deserialize the JSON
        string.

        For each field defined on the class, a property is created on the
        instance which contains the converted value from the source data.
        """
        self._extra = {}
        if is_json:
            data = json.loads(data)
        for name, field in self._clsfields.iteritems():
            key = field.source or name
            field.populate(data.get(key))
            setattr(self, name, field.to_python())

    @property
    def _fields(self):
        return dict(self._clsfields, **self._extra)

    def add_field(self, key, value, field):
        '''This method adds a field to an existing Model instance. The field
        instance must be passed so that the field can be properly serialized.
        '''
        field.populate(value)
        setattr(self, key, field.to_python())
        self._extra[key] = field

    def to_dict(self, serial=False):
        '''Creates a datastructure representing the Model data. If serial is set
        to True, the to_serial method will be called on each field. This
        converts the field data to a type which can be serialized by the json
        (or another) encoder. If serial is set to False (the default option), a
        a Python dictionary will be returned.
        '''
        keys = (k for k in self.__dict__.keys() if k in self._fields.keys())

        if serial:
            return dict((key, self._fields[key].to_serial(getattr(self, key)))
                     for key in keys)
        else:
            return dict((key, getattr(self, key)) for key in keys)

    def to_json(self):
        '''Returns a representation of the model as a JSON string.'''
        return json.dumps(self.to_dict(serial=True))

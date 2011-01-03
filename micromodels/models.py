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
    '''The JSONModel subclasses Model and provides the ability to modify,
    process, and output form data as a Python dictionary or a JSON string.
    '''

    def __init__(self, data, is_json=False):
        '''Creates a JSONModel from data. To construct the instance from a json
        string, the is_json keyword argument must be True. Construction from a
        normal Python dictionary is support if is_json is set to false. The
        default is False for is_json to not break compatibility with the normal
        Model class.
        '''
        if is_json:
            data = json.loads(data)
        super(JSONModel, self).__init__(data)

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

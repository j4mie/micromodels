try:
    import json
except ImportError:
    import simplejson as json

from .fields import BaseField

class Model(object):
    """The Model is the main component of micromodels. Model makes it trivial
    to parse data from many sources, including JSON APIs.

    The constructor for model takes either a native Python dictionary (default)
    or a JSON dictionary if ``is_json`` is ``True``. The dictionary passed does
    not need to contain all of the values that the Model declares. These values
    can be later assigned to the Model instance. It is worth noting that when
    these values are assigned, the Model will automatically parse these into
    the appropriate form using the to_python method on the field. This means
    that the "raw" format should be assigned. For instance, if a Model has a
    date field that you wish to assign after initialization, a string must be
    assigned to the variable, not a Python date object.

    """
    class __metaclass__(type):
        '''Creates the metaclass for Model. The main function of this metaclass
        is to move all of fields into the _fields variable on the class.

        '''
        def __init__(cls, name, bases, attrs):
            cls._clsfields = {}
            for key, value in attrs.iteritems():
                if isinstance(value, BaseField):
                    cls._clsfields[key] = value
                    delattr(cls, key)

    def __init__(self):
        super(Model, self).__setattr__('_extra', {})

    @classmethod
    def from_dict(cls, D, is_json=False):
        instance = cls()
        instance.set_data(D, is_json=is_json)
        return instance

    @classmethod
    def from_kwargs(cls, **kwargs):
        instance = cls()
        instance.set_data(kwargs)
        return instance

    def set_data(self, data, is_json=False):
        if is_json:
            data = json.loads(data)
        for name, field in self._clsfields.iteritems():
            key = field.source or name
            if key in data:
                setattr(self, name, data.get(key))

    def __setattr__(self, key, value):
        if key in self._fields:
            field = self._fields[key]
            try:
                field.populate(value)
                super(Model, self).__setattr__(key, field.to_python())
            except:
                try:
                    field.to_serial(value)
                except:
                    raise TypeError('%s could not be serialized by %s' %\
                                    (type(value).__name__, type(field).__name__))
                else:
                    super(Model, self).__setattr__(key, value)
        else:
            super(Model, self).__setattr__(key, value)

    @property
    def _fields(self):
        return dict(self._clsfields, **self._extra)

    def add_field(self, key, value, field):
        ''':meth:`add_field` must be used to add a field to an existing
        instance of Model. This method is required so that serialization of the
        data is possible. Data on existing fields (defined in the class) can be
        reassigned without using this method.

        '''
        self._extra[key] = field
        setattr(self, key, value)


    def to_dict(self, serial=False):
        '''A dictionary representing the the data of the class is returned.
        Native Python objects will still exist in this dictionary (for example,
        a ``datetime`` object will be returned rather than a string)
        unless ``serial`` is set to True.

        '''
        if serial:
            return dict((key, self._fields[key].to_serial(getattr(self, key)))
                        for key in self._fields.keys() if hasattr(self, key))
        else:
            return dict((key, getattr(self, key)) for key in self._fields.keys()
                       if hasattr(self, key))

    def to_json(self):
        '''Returns a representation of the model as a JSON string. This method
        relies on the :meth:`~micromodels.Model.to_dict` method.

        '''
        return json.dumps(self.to_dict(serial=True))

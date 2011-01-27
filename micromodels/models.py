try:
    import json
except ImportError:
    import simplejson as json

from .fields import BaseField

class Model(object):
    """The Model is the main component of micromodels. Model makes it trivial
    to parse data from many sources, including JSON APIs.

    You will probably want to initialize this class using the class methods
    :meth:`from_dict` or :meth:`from_kwargs`. If you want to initialize an
    instance without any data, just call :class:`Model` with no parameters.

    :class:`Model` instances have a unique behavior when an attribute is set
    on them. This is needed to properly format data as the fields specify.
    The variable name is referred to as the key, and the value will be called
    the value. For example, in::

        instance = Model()
        instance.age = 18

    ``age`` is the key and ``18`` is the value.

    First, the model checks if it has a field with a name matching the key.

    If there is a matching field, then :meth:`to_python` is called on the field
    with the value.
        If :meth:`to_python` does not raise an exception, then the result of
        :meth:`to_python` is set on the instance, and the method is completed.
        Essentially, this means that the first thing setting an attribute tries
        to do is process the data as if it was a "primitive" data type.

        If :meth:`to_python` does raise an exception, this means that the data
        might already be an appropriate Python type. The :class:`Model` then
        attempts to *serialize* the data into a "primitive" type using the
        field's :meth:`to_serial` method.

            If this fails, a ``TypeError`` is raised.

            If it does not fail, the value is set on the instance, and the
            method is complete.

    If the instance doesn't have a field matching the key, then the key and
    value are just set on the instance like any other assignment in Python.

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
        '''This factory for :class:`Model`
        takes either a native Python dictionary or a JSON dictionary/object
        if ``is_json`` is ``True``. The dictionary passed does not need to
        contain all of the values that the Model declares.

        '''
        instance = cls()
        instance.set_data(D, is_json=is_json)
        return instance

    @classmethod
    def from_kwargs(cls, **kwargs):
        '''This factory for :class:`Model` only takes keywork arguments.
        Each key and value pair that represents a field in the :class:`Model` is
        set on the new :class:`Model` instance.

        '''
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

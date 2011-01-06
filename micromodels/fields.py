import datetime

class BaseField(object):
    """Base class for all field types.

    The ``source`` parameter sets the key that will be retrieved from the source
    data. If ``source`` is not specified, the field instance will use its own
    name as the key to retrieve the value from the source data.

    """
    def __init__(self, source=None):
        self.source = source

    def populate(self, data):
        """Set the value or values wrapped by this field"""

        self.data = data

    def to_python(self):
        '''After being populated, this method casts the source data into a
        Python object. The default behavior is to simply return the source
        value. Subclasses should override this method.

        '''
        return self.data

    def to_serial(self, data):
        '''Used to serialize forms back into JSON or other formats.

        This method is essentially the opposite of
        :meth:`~micromodels.fields.BaseField.to_python`. A string, boolean,
        number, dictionary, list, or tuple must be returned. Subclasses should
        override this method.

        '''
        return data


class CharField(BaseField):
    """Field to represent a simple Unicode string value."""

    def to_python(self):
        """Convert the data supplied using the :meth:`populate` method to a
        Unicode string.

        """
        if self.data is None:
            return ''
        return unicode(self.data)


class IntegerField(BaseField):
    """Field to represent an integer value"""

    def to_python(self):
        """Convert the data supplied to the :meth:`populate` method to an
        integer.

        """
        if self.data is None:
            return 0
        return int(self.data)


class BooleanField(BaseField):
    """Field to represent a boolean"""

    def to_python(self):
        """The string ``'True'`` (case insensitive) will be converted
        to ``True``, as will any positive integers.

        """
        if isinstance(self.data, basestring):
            return self.data.strip().lower() == 'true'
        if isinstance(self.data, int):
            return self.data > 0
        return bool(self.data)


class DateTimeField(BaseField):
    """Field to represent a datetime

    The ``format`` parameter dictates the format of the input strings, and is
    used in the construction of the :class:`datetime.datetime` object.

    The ``serial_format`` parameter is a strftime formatted string for
    serialization. If ``serial_format`` isn't specified, an ISO formatted string
    will be returned by :meth:`~micromodels.DateTimeField.to_serial`.

    """
    def __init__(self, format, serial_format=None, **kwargs):
        super(DateTimeField, self).__init__(**kwargs)
        self.format = format
        self.serial_format = serial_format

    def to_python(self):
        '''A :class:`datetime.datetime` object is returned.'''

        if self.data is None:
            return None
        return datetime.datetime.strptime(str(self.data), self.format)

    def to_serial(self, time_obj):
        if not self.serial_format:
            return time_obj.isoformat()
        return time_obj.strftime(self.serial_format)

class DateField(DateTimeField):
    """Field to represent a :mod:`datetime.date`"""

    def to_python(self):
        datetime = super(DateField, self).to_python()
        return datetime.date()


class TimeField(DateTimeField):
    """Field to represent a :mod:`datetime.time`"""

    def to_python(self):
        datetime = super(TimeField, self).to_python()
        return datetime.time()


class WrappedObjectField(BaseField):
    """Superclass for any fields that wrap an object"""

    def __init__(self, wrapped_class, **kwargs):
        self._wrapped_class = wrapped_class
        BaseField.__init__(self, **kwargs)


class ModelField(WrappedObjectField):
    """Field containing a model instance

    Use this field when you wish to nest one object inside another.
    It takes a single required argument, which is the nested class.
    For example, given the following dictionary::

        some_data = {
            'first_item': 'Some value',
            'second_item': {
                'nested_item': 'Some nested value',
            },
        }

    You could build the following classes
    (note that you have to define the inner nested models first)::

        class MyNestedModel(micromodels.Model):
            nested_item = micromodels.CharField()

        class MyMainModel(micromodels.Model):
            first_item = micromodels.CharField()
            second_item = micromodels.ModelField(MyNestedModel)

    Then you can access the data as follows::

        >>> m = MyMainModel(some_data)
        >>> m.first_item
        u'Some value'
        >>> m.second_item.__class__.__name__
        'MyNestedModel'
        >>> m.second_item.nested_item
        u'Some nested value'

    """
    def to_python(self):
        return self._wrapped_class(self.data or {})

    def to_serial(self, model_instance):
        return model_instance.to_dict(serial=True)


class ModelCollectionField(WrappedObjectField):
    """Field containing a list of model instances.

    Use this field when your source data dictionary contains a list of
    dictionaries. It takes a single required argument, which is the name of the
    nested class that each item in the list should be converted to.
    For example::

        some_data = {
            'list': [
                {'value': 'First value'},
                {'value': 'Second value'},
                {'value': 'Third value'},
            ]
        }

        class MyNestedModel(micromodels.Model):
            value = micromodels.CharField()

        class MyMainModel(micromodels.Model):
            list = micromodels.ModelCollectionField(MyNestedModel)

        >>> m = MyMainModel(some_data)
        >>> len(m.list)
        3
        >>> m.list[0].__class__.__name__
        'MyNestedModel'
        >>> m.list[0].value
        u'First value'
        >>> [item.value for item in m.list]
        [u'First value', u'Second value', u'Third value']

    """
    def to_python(self):
        return [self._wrapped_class(item) for item in self.data or []]

    def to_serial(self, model_instances):
        return [instance.to_dict(serial=True) for instance in model_instances]


class FieldCollectionField(WrappedObjectField):
    """Field containing a list of the same type of fields.

    The constructor takes the class of field. If the field needs to be
    instantiated with arguments (like the ``format`` argument for the
    :class:`~micromodels.DateTimeField`), these arguments can be passed into the
    keyword arguments ``args`` and ``kwargs``. If these optional arguments are
    used, ``args`` needs to receive a tuple and ``kwargs`` needs to receive a
    dictionary.Beyond these keyword arguments, any other keyword arguments (like
    ``source``) will be passed to :class:`~micromodels.BaseField`'s constructor.

    This description is inherently confusing as this class contains a factory,
    and code speaks better than anything, so here are some examples::

        data = {
                    'legal_name': 'John Smith',
                    'aliases': ['Larry', 'Mo', 'Curly']
        }

        class Person(Model):
            legal_name = CharField()
            aliases = FieldCollectionField(CharField)

        p = Person(data)

    And now a quick REPL session::

        >>> p.legal_name
        u'John Smith'
        >>> p.aliases
        [u'Larry', u'Mo', u'Curly']
        >>> p.to_dict()
        {'legal_name': u'John Smith', 'aliases': [u'Larry', u'Mo', u'Curly']}
        >>> p.to_dict() == p.to_dict(serial=True)
        True

    Here is a bit more complicated example involving args and kwargs::

        data = {
                    'name': 'San Andreas',
                    'dates': ['1906-05-11', '1948-11-02', '1970-01-01']
        }

        class FaultLine(Model):
            name = CharField()
            earthquake_dates = FieldCollectionField(DateField, args=('%Y-%m-%d',),
                                                    kwargs={'serial_format': '%m-%d-%Y'},
                                                    source='dates')

        f = FaultLine(data)

    So args was passed a tuple, which consisted of a sole element representing
    the input format. This is a required argument for creating a
    :class:`~micromodels.DateField`. ``kwargs`` was given the ``serial_format``
    desired for output. The ``source`` keyword argument is passed up to
    :class:`~micromodels.BaseField` and allows our field instance (named
    ``earthquake_dates`` to get the data under the key ``dates`` from the source
    data.

    Let's check out the resulting :class:`~micromodels.Model` instance with the
    REPL::

        >>> f.name
        u'San Andreas'
        >>> f.earthquake_dates
        [datetime.date(1906, 5, 11), datetime.date(1948, 11, 2), datetime.date(1970, 1, 1)]
        >>> f.to_dict()
        {'earthquake_dates': [datetime.date(1906, 5, 11), datetime.date(1948, 11, 2), datetime.date(1970, 1, 1)],
         'name': u'San Andreas'}
        >>> f.to_dict(serial=True)
        {'earthquake_dates': ['05-11-1906', '11-02-1948', '01-01-1970'], 'name': u'San Andreas'}
        >>> f.to_json()
        '{"earthquake_dates": ["05-11-1906", "11-02-1948", "01-01-1970"], "name": "San Andreas"}'

    """
    def __init__(self, field_cls, args=(), kwargs = {}, **keyargs):
        self._instance = field_cls(*args, **kwargs)
        super(FieldCollectionField, self).__init__(field_cls, **keyargs)

    def to_python(self):
        def convert(item):
            self._instance.populate(item)
            return self._instance.to_python()
        return [convert(item) for item in self.data or []]

    def to_serial(self, list_of_fields):
        return [self._instance.to_serial(data) for data in list_of_fields]

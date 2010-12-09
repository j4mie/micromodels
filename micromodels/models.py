from fields import FieldBase

class Model(object):

    class __metaclass__(type):
        def __init__(cls, name, bases, attrs):
            fields = {}
            for name, value in attrs.items():
                if isinstance(value, FieldBase):
                    fields[name] = value
            setattr(cls, '_fields', fields)

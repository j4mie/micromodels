
class FieldBase(object):
    """Base class for all field types"""

    def __init__(self, source=None):
        self.source = source

    def populate(self, data):
        """Set the value or values wrapped by this field"""
        self.data = data

class CharField(FieldBase):

    def to_python(self):
        if self.data is None:
            return ''
        return unicode(self.data)

class IntegerField(FieldBase):

    def to_python(self):
        if self.data is None:
            return 0
        return int(self.data)

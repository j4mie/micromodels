
class FieldBase(object):
    """Base class for all field types"""

    def __init__(self, source=None):
        self.source = source

    def populate(self, data):
        """Set the value or values wrapped by this field"""
        self.data = data

class CharField(FieldBase):
    """Class to represent a simple string field"""

    def to_python(self):
        return unicode(self.data)

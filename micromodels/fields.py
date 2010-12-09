
class FieldBase(object):
    """Base class for all field types"""

    def __init__(self, source=None):
        self.source = source

class CharField(FieldBase):
    pass

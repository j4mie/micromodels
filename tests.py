import unittest
import dictmodels

class SimpleModel(dictmodels.Model):
    name = dictmodels.CharField()

class ClassCreationTestCase(unittest.TestCase):

    def setUp(self):
        self.instance = SimpleModel()

    def test_class_created(self):
        """Model instance should be of type SimpleModel"""
        self.assertTrue(isinstance(self.instance, SimpleModel))

    def test_fields_created(self):
        """Model instance should have a property called _fields"""
        self.assertTrue(hasattr(self.instance, '_fields'))

    def test_field_collected(self):
        """Model property should be of correct type"""
        self.assertTrue(isinstance(self.instance._fields['name'], dictmodels.CharField))

if __name__ == "__main__":
    unittest.main()

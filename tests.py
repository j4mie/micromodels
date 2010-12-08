import unittest
import dictmodels

class SimpleModel(dictmodels.Model):
    name = dictmodels.CharField()
    field_with_source = dictmodels.CharField(source='foo')

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

    def test_field_source_not_set(self):
        """Field without a custom source should have a source of None"""
        self.assertEqual(self.instance._fields['name'].source, None)

    def test_field_source_set(self):
        """Field with custom source specificied should have source property set correctly"""
        self.assertEqual(self.instance._fields['field_with_source'].source, 'foo')

if __name__ == "__main__":
    unittest.main()

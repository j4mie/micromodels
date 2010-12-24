import unittest
import micromodels

class ClassCreationTestCase(unittest.TestCase):

    def setUp(self):
        class SimpleModel(micromodels.Model):
            name = micromodels.CharField()
            field_with_source = micromodels.CharField(source='foo')
        self.model_class = SimpleModel
        self.instance = SimpleModel({})

    def test_class_created(self):
        """Model instance should be of type SimpleModel"""
        self.assertTrue(isinstance(self.instance, self.model_class))

    def test_fields_created(self):
        """Model instance should have a property called _fields"""
        self.assertTrue(hasattr(self.instance, '_fields'))

    def test_field_collected(self):
        """Model property should be of correct type"""
        self.assertTrue(isinstance(self.instance._fields['name'], micromodels.CharField))

    def test_field_source_not_set(self):
        """Field without a custom source should have a source of None"""
        self.assertEqual(self.instance._fields['name'].source, None)

    def test_field_source_set(self):
        """Field with custom source specificied should have source property set correctly"""
        self.assertEqual(self.instance._fields['field_with_source'].source, 'foo')


class FieldBaseTestCase(unittest.TestCase):

    def test_field_without_provided_source(self):
        """If no source parameter is provided, the field's source attribute should be None"""
        field = micromodels.fields.FieldBase()
        self.assertTrue(hasattr(field, 'source'))
        self.assertTrue(field.source is None)

    def test_field_with_provided_source(self):
        """If a source parameter is provided, the field's source attribute should be set to the value of this parameter"""
        field = micromodels.fields.FieldBase(source='customsource')
        self.assertEqual(field.source, 'customsource')


class CharFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = micromodels.CharField()

    def test_string_conversion(self):
        self.field.populate('somestring')
        self.assertEqual(self.field.to_python(), 'somestring')

    def test_none_conversion(self):
        """CharField should convert None to empty string"""
        self.field.populate(None)
        self.assertEqual(self.field.to_python(), '')


class IntegerFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = micromodels.IntegerField()

    def test_integer_conversion(self):
        self.field.populate(123)
        self.assertEqual(self.field.to_python(), 123)

    def test_string_conversion(self):
        self.field.populate('123')
        self.assertEqual(self.field.to_python(), 123)

    def test_none_conversion(self):
        """IntegerField should convert None to 0"""
        self.field.populate(None)
        self.assertEqual(self.field.to_python(), 0)


class BooleanFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = micromodels.BooleanField()

    def test_true_conversion(self):
        self.field.populate(True)
        self.assertEqual(self.field.to_python(), True)

    def test_false_conversion(self):
        self.field.populate(False)
        self.assertEqual(self.field.to_python(), False)

    def test_string_conversion(self):
        """BooleanField should convert the string "True" (case insensitive) to True, all other values to False"""
        self.field.populate('true')
        self.assertEqual(self.field.to_python(), True)
        self.field.populate('True')
        self.assertEqual(self.field.to_python(), True)
        self.field.populate('False')
        self.assertEqual(self.field.to_python(), False)
        self.field.populate('asdfasfasfd')
        self.assertEqual(self.field.to_python(), False)

    def test_integer_conversion(self):
        """BooleanField should convert values <= 0 to False, all other integers to True"""
        self.field.populate(0)
        self.assertEqual(self.field.to_python(), False)
        self.field.populate(-100)
        self.assertEqual(self.field.to_python(), False)
        self.field.populate(100)
        self.assertEqual(self.field.to_python(), True)


class DateTimeFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.format = "%a %b %d %H:%M:%S +0000 %Y"
        self.datetimestring = "Tue Mar 21 20:50:14 +0000 2006"
        self.field = micromodels.DateTimeField(format=self.format)

    def test_format_conversion(self):
        import datetime
        self.field.populate(self.datetimestring)
        converted = self.field.to_python()
        self.assertTrue(isinstance(converted, datetime.datetime))
        self.assertEqual(converted.strftime(self.format), self.datetimestring)


class InstanceTestCase(unittest.TestCase):

    def test_basic_data(self):
        class ThreeFieldsModel(micromodels.Model):
            first = micromodels.CharField()
            second = micromodels.CharField()
            third = micromodels.CharField()

        data = {'first': 'firstvalue', 'second': 'secondvalue', 'third': 'thirdvalue'}
        instance = ThreeFieldsModel(data)

        self.assertEqual(instance.first, data['first'])
        self.assertEqual(instance.second, data['second'])
        self.assertEqual(instance.third, data['third'])
        self.assertEqual(instance._data, data)

    def test_custom_data_source(self):
        class CustomSourceModel(micromodels.Model):
            first = micromodels.CharField(source='custom_source')

        data = {'custom_source': 'somevalue'}
        instance = CustomSourceModel(data)

        self.assertEqual(instance.first, data['custom_source'])


class ModelFieldTestCase(unittest.TestCase):

    def test_model_field_creation(self):
        class IsASubModel(micromodels.Model):
            first = micromodels.CharField()

        class HasAModelField(micromodels.Model):
            first = micromodels.ModelField(IsASubModel)

        data = {'first': {'first': 'somevalue'}}
        instance = HasAModelField(data)
        self.assertTrue(isinstance(instance.first, IsASubModel))
        self.assertEqual(instance.first.first, data['first']['first'])


class ModelCollectionFieldTestCase(unittest.TestCase):

    def test_model_collection_field_creation(self):
        class IsASubModel(micromodels.Model):
            first = micromodels.CharField()

        class HasAModelCollectionField(micromodels.Model):
            first = micromodels.ModelCollectionField(IsASubModel)

        data = {'first': [{'first': 'somevalue'}, {'first': 'anothervalue'}]}
        instance = HasAModelCollectionField(data)
        self.assertTrue(isinstance(instance.first, list))
        for item in instance.first:
            self.assertTrue(isinstance(item, IsASubModel))
        self.assertEqual(instance.first[0].first, data['first'][0]['first'])
        self.assertEqual(instance.first[1].first, data['first'][1]['first'])

    def test_model_collection_field_with_no_elements(self):
        class IsASubModel(micromodels.Model):
            first = micromodels.CharField()

        class HasAModelCollectionField(micromodels.Model):
            first = micromodels.ModelCollectionField(IsASubModel)

        data = {'first': []}
        instance = HasAModelCollectionField(data)
        self.assertEqual(instance.first, [])


class FieldCollectionFieldTestCase(unittest.TestCase):

    def test_field_collection_field_creation(self):
        class HasAFieldCollectionField(micromodels.Model):
            first = micromodels.FieldCollectionField(micromodels.CharField)

        data = {'first': ['one', 'two', 'three']}
        instance = HasAFieldCollectionField(data)
        self.assertTrue(isinstance(instance.first, list))
        self.assertTrue(len(data['first']), len(instance.first))
        for index, value in enumerate(data['first']):
            self.assertEqual(instance.first[index], value)


if __name__ == "__main__":
    unittest.main()

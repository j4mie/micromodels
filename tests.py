from datetime import date
import unittest

import micromodels
from micromodels.models import json

class ClassCreationTestCase(unittest.TestCase):

    def setUp(self):
        class SimpleModel(micromodels.Model):
            name = micromodels.CharField()
            field_with_source = micromodels.CharField(source='foo')
        self.model_class = SimpleModel
        self.instance = SimpleModel()

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


class BaseFieldTestCase(unittest.TestCase):

    def test_field_without_provided_source(self):
        """If no source parameter is provided, the field's source attribute should be None"""
        field = micromodels.fields.BaseField()
        self.assertTrue(hasattr(field, 'source'))
        self.assertTrue(field.source is None)

    def test_field_with_provided_source(self):
        """If a source parameter is provided, the field's source attribute should be set to the value of this parameter"""
        field = micromodels.fields.BaseField(source='customsource')
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

    def test_float_conversion(self):
        self.field.populate(123.4)
        self.assertEqual(self.field.to_python(), 123)

    def test_string_conversion(self):
        self.field.populate('123')
        self.assertEqual(self.field.to_python(), 123)

    def test_none_conversion(self):
        """IntegerField should convert None to 0"""
        self.field.populate(None)
        self.assertEqual(self.field.to_python(), 0)


class FloatFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = micromodels.FloatField()

    def test_float_conversion(self):
        self.field.populate(123.4)
        self.assertEqual(self.field.to_python(), 123.4)

    def test_integer_conversion(self):
        self.field.populate(123)
        self.assertEqual(self.field.to_python(), 123.0)

    def test_string_conversion(self):
        self.field.populate('123.4')
        self.assertEqual(self.field.to_python(), 123.4)

    def test_none_conversion(self):
        """FloatField should convert None to 0.0"""
        self.field.populate(None)
        self.assertEqual(self.field.to_python(), 0.0)


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

    def test_iso8601_conversion(self):
        import datetime
        from micromodels.packages.PySO8601 import Timezone
        
        field = micromodels.DateTimeField()
        field.populate("2010-07-13T14:01:00Z")
        result = field.to_python()
        expected = datetime.datetime(2010, 7, 13, 14, 1, 0,
                                     tzinfo=Timezone())
        self.assertEqual(expected, result)


        field = micromodels.DateTimeField()
        field.populate("2010-07-13T14:02:00-05:00")
        result = field.to_python()
        expected = datetime.datetime(2010, 7, 13, 14, 2, 0,
                                     tzinfo=Timezone("-05:00"))

        self.assertEqual(expected, result)


        field = micromodels.DateTimeField()
        field.populate("20100713T140200-05:00")
        result = field.to_python()
        expected = datetime.datetime(2010, 7, 13, 14, 2, 0,
                                     tzinfo=Timezone("-05:00"))

        self.assertEqual(expected, result)


    def test_iso8601_to_serial(self):
        import datetime
        
        field = micromodels.DateTimeField()
        field.populate("2010-07-13T14:01:00Z")
        native = field.to_python()
        expected = "2010-07-13T14:01:00+00:00"
        result = field.to_serial(native)

        self.assertEqual(expected, result)

        field = micromodels.DateTimeField()
        field.populate("2010-07-13T14:02:00-05:00")
        native = field.to_python()
        expected = "2010-07-13T14:02:00-05:00"
        result = field.to_serial(native)

        self.assertEqual(expected, result)


class DateFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.format = "%Y-%m-%d"
        self.datestring = "2010-12-28"
        self.field = micromodels.DateField(format=self.format)

    def test_format_conversion(self):
        import datetime
        self.field.populate(self.datestring)
        converted = self.field.to_python()
        self.assertTrue(isinstance(converted, datetime.date))
        self.assertEqual(converted.strftime(self.format), self.datestring)

    def test_iso8601_conversion(self):
        import datetime
        field = micromodels.DateField()
        field.populate("2010-12-28")
        result = field.to_python()
        expected = datetime.date(2010,12,28)
        self.assertEqual(expected, result)

        field = micromodels.DateField()
        field.populate("20101228")
        result = field.to_python()
        expected = datetime.date(2010,12,28)
        self.assertEqual(expected, result)


class TimeFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.format = "%H:%M:%S"
        self.timestring = "09:33:30"
        self.field = micromodels.TimeField(format=self.format)

    def test_format_conversion(self):
        import datetime
        self.field.populate(self.timestring)
        converted = self.field.to_python()
        self.assertTrue(isinstance(converted, datetime.time))
        self.assertEqual(converted.strftime(self.format), self.timestring)

    def test_iso8601_conversion(self):
        import datetime
        field = micromodels.TimeField()
        field.populate("09:33:30")
        result = field.to_python()
        expected = datetime.time(9,33,30)
        self.assertEqual(expected, result)

        field = micromodels.TimeField()
        field.populate("093331")
        result = field.to_python()
        expected = datetime.time(9,33,31)
        self.assertEqual(expected, result)


class InstanceTestCase(unittest.TestCase):

    def test_basic_data(self):
        class ThreeFieldsModel(micromodels.Model):
            first = micromodels.CharField()
            second = micromodels.CharField()
            third = micromodels.CharField()

        data = {'first': 'firstvalue', 'second': 'secondvalue'}
        instance = ThreeFieldsModel.from_dict(data)

        self.assertEqual(instance.first, data['first'])
        self.assertEqual(instance.second, data['second'])

    def test_custom_data_source(self):
        class CustomSourceModel(micromodels.Model):
            first = micromodels.CharField(source='custom_source')

        data = {'custom_source': 'somevalue'}
        instance = CustomSourceModel.from_dict(data)

        self.assertEqual(instance.first, data['custom_source'])


class ModelFieldTestCase(unittest.TestCase):

    def test_model_field_creation(self):
        class IsASubModel(micromodels.Model):
            first = micromodels.CharField()

        class HasAModelField(micromodels.Model):
            first = micromodels.ModelField(IsASubModel)

        data = {'first': {'first': 'somevalue'}}
        instance = HasAModelField.from_dict(data)
        self.assertTrue(isinstance(instance.first, IsASubModel))
        self.assertEqual(instance.first.first, data['first']['first'])

    def test_model_field_to_serial(self):
        class User(micromodels.Model):
            name = micromodels.CharField()

        class Post(micromodels.Model):
            title = micromodels.CharField()
            author = micromodels.ModelField(User)

        data = {'title': 'Test Post', 'author': {'name': 'Eric Martin'}}
        post = Post.from_dict(data)
        self.assertEqual(post.to_dict(serial=True), data)

    def test_failing_modelfield(self):
        class SomethingExceptional(Exception):
            pass

        class User(micromodels.Model):
            name = micromodels.CharField()

            @classmethod
            def from_dict(cls, *args, **kwargs):
                raise SomethingExceptional("opps.")

        class Post(micromodels.Model):
            title = micromodels.CharField()
            author = micromodels.ModelField(User)

        data = {'title': 'Test Post', 'author': {'name': 'Eric Martin'}}
        self.assertRaises(SomethingExceptional, Post.from_dict,
                          data)
                           

class ModelCollectionFieldTestCase(unittest.TestCase):

    def test_model_collection_field_creation(self):
        class IsASubModel(micromodels.Model):
            first = micromodels.CharField()

        class HasAModelCollectionField(micromodels.Model):
            first = micromodels.ModelCollectionField(IsASubModel)

        data = {'first': [{'first': 'somevalue'}, {'first': 'anothervalue'}]}
        instance = HasAModelCollectionField.from_dict(data)
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
        instance = HasAModelCollectionField.from_dict(data)
        self.assertEqual(instance.first, [])

    def test_model_collection_to_serial(self):
        class Post(micromodels.Model):
            title = micromodels.CharField()

        class User(micromodels.Model):
            name = micromodels.CharField()
            posts = micromodels.ModelCollectionField(Post)

        data = {
                'name': 'Eric Martin',
                'posts': [
                            {'title': 'Post #1'},
                            {'title': 'Post #2'}
                ]
        }

        eric = User.from_dict(data)
        processed = eric.to_dict(serial=True)
        self.assertEqual(processed, data)

class FieldCollectionFieldTestCase(unittest.TestCase):

    def test_field_collection_field_creation(self):
        class HasAFieldCollectionField(micromodels.Model):
            first = micromodels.FieldCollectionField(micromodels.CharField())

        data = {'first': ['one', 'two', 'three']}
        instance = HasAFieldCollectionField.from_dict(data)
        self.assertTrue(isinstance(instance.first, list))
        self.assertTrue(len(data['first']), len(instance.first))
        for index, value in enumerate(data['first']):
            self.assertEqual(instance.first[index], value)

    def test_field_collection_field_to_serial(self):
        class Person(micromodels.Model):
            aliases = micromodels.FieldCollectionField(micromodels.CharField())
            events = micromodels.FieldCollectionField(micromodels.DateField('%Y-%m-%d',
                                        serial_format='%m-%d-%Y'), source='schedule')

        data = {
                    'aliases': ['Joe', 'John', 'Bob'],
                    'schedule': ['2011-01-30', '2011-04-01']
        }

        p = Person.from_dict(data)
        serial = p.to_dict(serial=True)
        self.assertEqual(serial['aliases'], data['aliases'])
        self.assertEqual(serial['events'][0], '01-30-2011')

class ModelTestCase(unittest.TestCase):

    def setUp(self):
        class Person(micromodels.Model):
            name = micromodels.CharField()
            age = micromodels.IntegerField()

        self.Person = Person
        self.data = {'name': 'Eric', 'age': 18}
        self.json_data = json.dumps(self.data)

    def test_model_creation(self):
        instance = self.Person.from_dict(self.json_data, is_json=True)
        self.assertTrue(isinstance(instance, micromodels.Model))
        self.assertEqual(instance.name, self.data['name'])
        self.assertEqual(instance.age, self.data['age'])

    def test_model_reserialization(self):
        instance = self.Person.from_dict(self.json_data, is_json=True)
        self.assertEqual(instance.to_json(), self.json_data)
        instance.name = 'John'
        self.assertEqual(json.loads(instance.to_json())['name'],
                         'John')

    def test_model_type_change_serialization(self):
        class Event(micromodels.Model):
            time = micromodels.DateField(format="%Y-%m-%d")

        data = {'time': '2000-10-31'}
        json_data = json.dumps(data)

        instance = Event.from_dict(json_data, is_json=True)
        output = instance.to_dict(serial=True)
        self.assertEqual(output['time'], instance.time.isoformat())
        self.assertEqual(json.loads(instance.to_json())['time'],
                         instance.time.isoformat())

    def test_model_add_field(self):
        obj = self.Person.from_dict(self.data)
        obj.add_field('gender', 'male', micromodels.CharField())
        self.assertEqual(obj.gender, 'male')
        self.assertEqual(obj.to_dict(), dict(self.data, gender='male'))

    def test_model_late_assignment(self):
        instance = self.Person.from_dict(dict(name='Eric'))
        self.assertEqual(instance.to_dict(), dict(name='Eric'))
        instance.age = 18
        self.assertEqual(instance.to_dict(), self.data)
        instance.name = 'John'
        self.assertEqual(instance.to_dict(), dict(name='John', age=18))
        instance.age = '19'
        self.assertEqual(instance.to_dict(), dict(name='John', age=19))

        format = '%m-%d-%Y'
        today = date.today()
        today_str = today.strftime(format)

        instance.add_field('birthday', today_str,
                           micromodels.DateField(format))
        self.assertEqual(instance.to_dict()['birthday'], today)
        instance.birthday = today
        self.assertEqual(instance.to_dict()['birthday'], today)


if __name__ == "__main__":
    unittest.main()

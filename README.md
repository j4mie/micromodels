# micromodels

A simple library for building model classes based on dictionaries of data.

Perfect for (amongst other things) wrapping Python objects around JSON data returned from web-based APIs.

**Authors**: Jamie Matthews (<https://github.com/j4mie>) and Eric Martin (<https://github.com/lightcatcher>).

## Installation

    pip install micromodels

## Really simple example

    import micromodels

    class Author(micromodels.Model):
        first_name = micromodels.CharField()
        last_name = micromodels.CharField()
        date_of_birth = micromodels.DateField(format="%Y-%m-%d")

        @property
        def full_name(self):
            return "%s %s" % (self.first_name, self.last_name)


    douglas_data = {
        "first_name": "Douglas",
        "last_name": "Adams",
        "date_of_birth": "1952-03-11",
    }

    douglas = Author.from_dict(douglas_data)
    print "%s was born in %s" % (douglas.full_name, douglas.date_of_birth.strftime("%Y"))

## Slightly more complex example

    import json
    from urllib2 import urlopen

    import micromodels

    class TwitterUser(micromodels.Model):
        id = micromodels.IntegerField()
        screen_name = micromodels.CharField()
        name = micromodels.CharField()
        description = micromodels.CharField()

        def get_profile_url(self):
            return 'http://twitter.com/%s' % self.screen_name


    class Tweet(micromodels.Model):
        id = micromodels.IntegerField()
        text = micromodels.CharField()
        created_at = micromodels.DateTimeField(format="%a %b %d %H:%M:%S +0000 %Y")
        user = micromodels.ModelField(TwitterUser)


    json_data = urlopen('http://api.twitter.com/1/statuses/show/20.json').read()
    tweet = Tweet.from_dict(json_data, is_json=True)

    print tweet.user.name
    print tweet.user.get_profile_url()
    print tweet.id
    print tweet.created_at.strftime('%A')

    #new fields can also be added to the model instance
    #a method needs to be used to do this to handle serialization

    tweet.add_field('retweet_count', 44, micromodels.IntegerField())
    print tweet.retweet_count

    #the data can be cast to a dict (still containing time object)
    print tweet.to_dict()

    #it can also be cast to JSON (fields handle their own serialization)
    print tweet.to_json()

    #tweet.to_json() is equivalent to this call
    json.dumps(tweet.to_dict(serial=True))


## Field reference

### Field options

The following optional argument is available for all field types.

#### `source`

By default, a model class will look for a key in its source data with the same name as each of its fields. For example:

    class ExampleModel(micromodels.Model):
        myfield = micromodels.CharField()

    >>> e = ExampleModel({'myfield': 'Some Value'})
    >>> e.myfield
    u'Some Value'

If you wish to change this, you can pass the 'source' argument to each field instance:

    class ExampleModel(micromodels.Model):
        myfield = micromodels.CharField()
        anotherfield = micromodels.CharField(source='some_other_field')

    >>> e = ExampleModel({'myfield': 'Some Value', 'some_other_field': 'Another Value'})
    >>> e.anotherfield
    u'Another Value'

### Field types

#### BaseField

The simplest type of field - this simply passes through whatever is in the data dictionary without changing it at all.

#### CharField

A field for string data. **Will attempt to convert its supplied data to Unicode.**

#### IntegerField

Attempts to convert its supplied data to an integer.

#### BooleanField

Attempts to convert its supplied data to a boolean. If the data is a string, `"true"` (case insensitive) will be converted to `True` and all other strings will be converted to `False`. If the supplied data is an integer, positive numbers will become `True` and negative numbers or zero will become `False`.

#### DateTimeField

Converts its supplied data to a Python `datetime.datetime` object using the format given in the required `format` argument. See [the Python documentation](http://docs.python.org/library/datetime.html#strftime-strptime-behavior) for details of the format string. For example:

    class MyModel(micromodels.Model):
        created_at = micromodels.DateTimeField(format="%a %b %d %H:%M:%S +0000 %Y")

#### DateField

Converts its supplied data to a Python `datetime.date` object using the format given in the required `format` argument (see `DateTimeField` for details).

#### TimeField

Converts its supplied data to a Python `datetime.time` object using the format given in the required `format` argument (see `DateTimeField` for details).

#### FieldCollectionField

Use this field when your source data dictionary contains a list of items of the same type. It takes a single required argument, which is the field type that should be used to convert each item in the list. For example:

    some_data = {
        'first_list': [0, 34, 42],
        'second_list': ['first_item', 'second_item', 'third_item'],
    }

    class MyModel(micromodels.Model):
        first_list = micromodels.FieldCollectionField(micromodels.IntegerField)
        second_list = micromodels.FieldCollectionField(micromodels.CharField)

    >>> m = MyModel(some_data)
    >>> m.first_list
    [0, 34, 42]
    >>> m.second_list
    [u'first_item', u'second_item', u'third_item']

#### ModelField

Use this field when you wish to nest one object inside another. It takes a single required argument, which is the nested class. For example, given the following dictionary:

    some_data = {
        'first_item': 'Some value',
        'second_item': {
            'nested_item': 'Some nested value',
        },
    }

You could build the following classes (note that you have to define the inner nested models first):

    class MyNestedModel(micromodels.Model):
        nested_item = micromodels.CharField()

    class MyMainModel(micromodels.Model):
        first_item = micromodels.CharField()
        second_item = micromodels.ModelField(MyNestedModel) # pass the class of the nested model

Then you can access the data as follows:

    >>> m = MyMainModel(some_data)
    >>> m.first_item
    u'Some value'
    >>> m.second_item.__class__.__name__
    'MyNestedModel'
    >>> m.second_item.nested_item
    u'Some nested value'

#### ModelCollectionField

Use this field when your source data dictionary contains a list of dictionaries. It takes a single required argument, which is the name of the nested class that each item in the list should be converted to. For example:

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


## (Un)license

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this software, either in source code form or as a compiled binary, for any purpose, commercial or non-commercial, and by any means.

In jurisdictions that recognize copyright laws, the author or authors of this software dedicate any and all copyright interest in the software to the public domain. We make this dedication for the benefit of the public at large and to the detriment of our heirs and successors. We intend this dedication to be an overt act of relinquishment in perpetuity of all present and future rights to this software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>

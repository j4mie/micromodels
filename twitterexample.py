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
tweet = Tweet(json_data, is_json=True)

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



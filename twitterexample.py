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
    user = micromodels.ModelField(TwitterUser)

json_data = urlopen('http://api.twitter.com/1/statuses/show/20.json').read()
tweet = Tweet(json.loads(json_data))

print "Tweet was posted by %s (%s)" % (tweet.user.name, tweet.user.get_profile_url())

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

json_data = urlopen('http://api.twitter.com/1/statuses/show/20.json')
tweet = Tweet(json.load(json_data))

print "Tweet was posted by %s (%s) on a %s" % (
    tweet.user.name,
    tweet.user.get_profile_url(),
    tweet.created_at.strftime("%A")
)

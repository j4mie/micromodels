# micromodels

A simple library for building read-only model classes based on dictionaries of data.

Perfect for wrapping Python objects around JSON data returned from web-based APIs.

## Example

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

## (Un)license

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this software, either in source code form or as a compiled binary, for any purpose, commercial or non-commercial, and by any means.

In jurisdictions that recognize copyright laws, the author or authors of this software dedicate any and all copyright interest in the software to the public domain. We make this dedication for the benefit of the public at large and to the detriment of our heirs and successors. We intend this dedication to be an overt act of relinquishment in perpetuity of all present and future rights to this software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>

from tweets import tweets_collection
from datetime import datetime, timedelta

MARGIN = timedelta(hours=0.5)

def _time_for_display(time):
    return datetime.strftime(time, '%H:%M')

def _tweet_for_display(tweet):
    return {
        'time': _time_for_display(tweet['created_at']),
        'screenname': tweet['screen_name'],
        'profile_pic': tweet['user']['profile_image_url'],
        'body': tweet['text'],
    }

def tweets_between(start, end):
    start -= MARGIN
    end += MARGIN
    tweets = tweets_collection.find({'created_at': {'$gt': start, '$lt': end}}).sort('created_at')
    return [_tweet_for_display(tweet) for tweet in tweets]

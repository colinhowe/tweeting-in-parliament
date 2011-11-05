from tweets import tweets_collection
from datetime import timedelta

MARGIN = timedelta(hours=2)

def tweets_between(start, end):
    start -= MARGIN
    end += MARGIN
    return tweets_collection.find('created_at': {'$gt': start, '$lt': end}})

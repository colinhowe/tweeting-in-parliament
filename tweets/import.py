import pymongo
from tweepy import api

DATABASE = 'parliament'
TWEET_COLLECTION = 'tweets'

connection = pymongo.Connection()
db = connection[DATABASE]
tweets = db[TWEET_COLLECTION]



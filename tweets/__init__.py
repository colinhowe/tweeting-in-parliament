import pymongo

DATABASE = 'parliament'
TWEET_COLLECTION = 'tweets'

connection = pymongo.Connection()
db = connection[DATABASE]
tweets_collection = db[TWEET_COLLECTION]

tweets_collection.ensure_index([("screen_name", pymongo.ASCENDING), ("created_at", pymongo.ASCENDING)])
tweets_collection.ensure_index([("id", pymongo.ASCENDING)], unique=True)

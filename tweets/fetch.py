# -*- coding: utf-8 -*-
import pymongo
from tweepy import OAuthHandler, API, TweepError
from members.documents import Member, _sanitize_screen_name
from twitter_credentials import *

DATABASE = 'parliament'
TWEET_COLLECTION = 'tweets'

connection = pymongo.Connection()
db = connection[DATABASE]
tweets_collection = db[TWEET_COLLECTION]
tweets_collection.ensure_index([("screen_name", pymongo.ASCENDING), ("created_at", pymongo.ASCENDING)])
tweets_collection.ensure_index([("id", pymongo.ASCENDING)], unique=True)

auth_handler = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth_handler.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = API(auth_handler)

def _status_to_dict(status):
    # I have done a bad thing. I have modified tweepy.models.Status.parse()
    # to add an attribute 'json' to each status. json will contain the
    # json object with all the original tweet data
    status_dict = dict(status.json.items())

    # convert created_at to a datetime for simplicity
    status_dict['created_at'] = status.created_at

    # add an attribute screen_name at the top level for easy indexing
    # and retrieval
    status_dict['screen_name'] = _sanitize_screen_name(status.user.screen_name)
    return status_dict

def fetch_member_tweets(member, page):
    try:
        member_tweets = api.user_timeline(screen_name=member.screen_name,
              page=page, count=200, include_entities=True)
    except TweepError, e:
        if e.message == 'Not found':
            print 'member %s does not exist, deleting', m.screen_name
            member.delete()
            return
        else:
            print e
            return

    member_tweets = [_status_to_dict(status) for status in member_tweets]
    for t in member_tweets:
        tweets_collection.insert(t)

def fetch_all():
    for page in (1, 2, 3):
        for m in Member.objects.all():
            print 'fetching page %s of tweets for %s' % (page, m.name)
            fetch_member_tweets(m, page)


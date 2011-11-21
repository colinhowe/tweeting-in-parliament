# -*- coding: utf-8 -*-
from tweets import tweets_collection
from tweepy import OAuthHandler, API, TweepError
from members.documents import Member, _sanitize_screen_name
from twitter_credentials import *
import time

auth_handler = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth_handler.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = API(auth_handler)

def _tweet_to_dict(status):
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

def save_member_twitter_id(member):
    try:
        user = api.get_user(member.screen_name,
                headers={'User-Agent': 'conversocial.com'})
    except TweepError, e:
        if e.reason == 'Not found':
            print 'member %s not found, setting not active.', member.screen_name
            member.active = False
            member.save()
        raise
    else:
        member.twitter_id = str(user.id)
        member.save()

def fetch_member_tweets(member, page):
    try:
        if not member.twitter_id:
            save_member_twitter_id(member)
    except Exception, e:
        print e
        return

    try:
        member_tweets = api.user_timeline(screen_name=member.screen_name,
            uid=member.twitter_id, page=page, count=100, include_entities=True,
            headers={'User-Agent': 'conversocial.com'})
    except TweepError, e:
        print e
        return

    if member_tweets:
        member.active = True
        member.save()

    for tweet in member_tweets:
        tweets_collection.insert(_tweet_to_dict(tweet))

def fetch_all(pages, start_at=None):
    for m in Member.objects.all().order_by('screen_name'):
        for page in pages:
            if start_at and m.screen_name < start_at:
                print 'skipping %s' % m.name
                continue
            print 'fetching page %s of tweets for %s, id:%s' % (page, m.name, m.id)
            fetch_member_tweets(m, page)
        time.sleep(8)

import tweepy
import json
from pymongo import MongoClient
from bson import json_util
from tweepy.utils import import_simplejson
from boto.sqs.message import Message
import boto.sqs
import uuid
import os


#Twitter auth

# Get the keys from your env variables
TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET') 
TWITTER_ACCESS_TOKEN_KEY = os.environ.get('TWITTER_ACCESS_TOKEN_KEY')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

auth1 = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth1.set_access_token(TWITTER_ACCESS_TOKEN_KEY, TWITTER_ACCESS_TOKEN_SECRET)


#Mongo Connection
MONGO_DB_URL = os.environ.get('MONGO_DB_URL')
mongocon = MongoClient(MONGO_DB_URL)
db = mongocon.twitter_final
col = db.tweets
print "Number of tweets in the db: ", col.count()
    

#AWS auth
REGION = 'us-east-1'
conn = boto.sqs.connect_to_region(REGION)
tweets_queue = conn.get_queue('tweets_queue')



class StreamListener(tweepy.StreamListener):
    json = import_simplejson()

    def on_status(self, tweet):
        print 'Ran on_status'

    def on_error(self, status_code):
        return False

    def on_data(self, data):
        if data[0].isdigit():
            pass
        else:
            d = json.loads(data)

        # Get only tweets with coordinates
        if d.get("geo") and d.get("text"):
            result = dict()
            # Set by default all the tweets to "neutral", they will be processed after
            result['sentiment'] = 'neutral'
            result['coordinates'] = [d['coordinates']['coordinates'][0], d['coordinates']['coordinates'][1]]
            col.insert(result)
            print("Inserted new tweet in database")

            # Insert the extracted tweet to SQS
            m = Message()
            body = {'text': d['text'], 'coordinates': [d['coordinates']['coordinates'][0], d['coordinates']['coordinates'][1]]}
            print body
            m.set_body(json.dumps(body))
            tweets_queue.write(m)
            print("Inserted new tweet in Queue")

l = StreamListener()
streamer = tweepy.Stream(auth=auth1, listener=l)
streamer.filter(locations=[-180,-90,180,90])


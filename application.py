#!/bin/env python
# encoding: utf-8
import json
import time
import math
import threading
import signal
import sys
import os
from flask import Flask
from flask import request
from flask import redirect
from flask import abort
from flask import url_for
from flask import make_response
from flask import Response
from pymongo import MongoClient
from bson import json_util
from pymongo import CursorType
import boto.sns
import requests
import ast


# Get the url of my mongo database where the tweets are stored
MONGO_DB_URL = os.environ.get('MONGO_DB_URL')

# Connect to the collection twitter_final where the tweets are stored
db = MongoClient(MONGO_DB_URL).twitter_final


# Define a function that will yield the tweets to a given endpoint
def event_stream():
    print "Begins to retrieve tweets from the Mongo database..."
    global db
    coll = db.tweets
    cursor = coll.find({}, cursor_type = CursorType.TAILABLE_AWAIT)
    ci=0
    while cursor.alive:
        try:
            doc = cursor.next()
            ci += 1
            message = json.dumps(doc, default=json_util.default)
            yield 'data: %s\n\n' % message  
        except StopIteration:
            pass


   
application = Flask(__name__)
@application.route('/')
def hello_world():
    return redirect(url_for('static', filename='tweets_map.html'))


@application.route('/tweets')
def tweets():  
    url_for('static', filename='tweets_map.html')
    url_for('static', filename='jquery-1.7.2.min.js')
    url_for('static', filename='jquery.eventsource.js')
    url_for('static', filename='jquery-1.7.2.js')
    return Response(event_stream(), headers={'Content-Type':'text/event-stream', 'X-UA-Compatible':'IE=Edge,chrome=1', 'Cache-Control':'public, max-age=0'})


@application.route('/notify', methods = ['GET', 'POST'])
def sns():
    global db
    coll = db.tweets

    if request.method == 'POST':
        print request.method
        header = request.headers.get('x-amz-sns-message-type')
        print header
        message = json.loads(request.data)

        # Confirm the subscription to the topic if it is not already done
        if header == "SubscriptionConfirmation" and "SubscribeURL" in message:
            r = requests.get(message['SubscribeURL'])
            return "Subscription done"

        # If the subscription is confirmed push the sentiment tweet in mongoDB
        if header == "Notification":
            d = ast.literal_eval(message['Message'])
            print d
            coll.insert(d)
            return 'Ok'
        else:
            return "Error"
    else:
        return "get method to notify"



if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', threaded=True)  
    

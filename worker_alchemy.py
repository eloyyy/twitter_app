from alchemyapi import AlchemyAPI
import time
import boto
import boto.sqs
from boto.sqs.message import Message
from threading import Thread
import requests
import ast
from boto import sns
import multiprocessing


#AWS Auth
REGION = 'your_region'
conn = boto.sqs.connect_to_region(REGION)
tweets_queue = conn.get_queue('your_sqs_queue')
c_sns = boto.sns.connect_to_region(REGION)

#Monkeylearn Auth
alchemyapi = AlchemyAPI()

def process_message(tweets_queue, topicarn, alchemy=False):
    """ Reads a message in the queue (long polling), makes a call to alchemy sentiment API and publish the result to 
    your SNS topic """

    while 1:
        m = tweets_queue.read() 
        if m is not None:
            message = ast.literal_eval(m.get_body())
            m.delete()
            myText = message['text']
            print "Processing the tweet: ", myText
            #Call to the sentiment API
            if alchemy:
                response = alchemyapi.sentiment("text", myText)
                if response['status'] == 'OK':
                    print "Sentiment: ", response["docSentiment"]["type"], ' \n'

                    result = dict()
                    result['coordinates'] = message['coordinates']
                    result['sentiment'] = response["docSentiment"]["type"]

                    #Publish to the SNS topic
                    publication = c_sns.publish(topicarn, result)
            else:
                print message, ' \n'
        else:
            time.sleep(3)


        
if __name__ == "__main__":

    processes = 1   # Number of processes to create
    topicarn = "your_topic_arn"
    
    jobs = []
    for i in range(0, processes):
        out_list = list()
        process = multiprocessing.Process(target=process_message, args=(tweets_queue, topicarn, True))
        jobs.append(process)

    # Start the processes
    for j in jobs:
        j.start()


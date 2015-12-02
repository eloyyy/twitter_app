# twitter_app

Complete web app built with the Python Flask framework. Displays a map of the tweets in real time, each tweet is asynchronously sent to the Alchemy API and has a sentiment attached: "Neutral", "Positive" or "Negative". We use a MongoDB database for storing the tweets. This app can easily be highly scalable when deployed on AWS using ElasticBeanstalk, SNS notifications and SQS queue. Here is a quick overview of the architecture chosen:

#### Cloud architecture of the twitter app
![alt tag](https://github.com/eloyyy/twitter_app/blob/master/cloud_architecture.jpg)
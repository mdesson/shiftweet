#! /usr/bin/python3
import json
import tweepy
import re
from datetime import datetime, timezone
import smtplib

with open("config.json", "r") as file:
    config = json.load(file)

# Twitter config
api_key = config['twitter']["API_KEY"]
api_secret_key = config['twitter']["API_SECRET_KEY"]
access_token = config['twitter']["ACCESS_TOKEN"]
access_token_secret = config['twitter']["ACCESS_TOKEN_SECRET"]

# email config
email_from = config['gmail']['FROM_ADDRESS']
email_password = config['gmail']['APP_PASSWORD']
email_to = config['gmail']['TO_ADDRESSES']

account_name = 'DuvalMagic'
max_hours_in_past = 1000  # max age of tweet, in hours

# Connect to Twitter
auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Get Randy's timeline
randy = api.get_user(account_name, tweet_mode='extended')
timeline = randy.timeline(tweet_mode='extended')

# Output Tweets
shift_tweets = []

# Append any relevant tweets to shift_tweets
for status in timeline:
    # get date difference
    date = datetime.strptime(
        status._json['created_at'], '%a %b %d %H:%M:%S %z %Y')
    diff = datetime.now(timezone.utc) - date
    is_shift_tweet = re.search(
        '(shift|[a-z0-9]{5}-[a-z0-9]{5}-[a-z0-9]{5}-[a-z0-9]{5}-[a-z0-9]{5})',
        status._json['full_text'].lower())

    if diff.seconds / 60 <= max_hours_in_past and is_shift_tweet:
        shift_tweets.append(
            f'https://twitter.com/{account_name}/status/{status.id}')


stringified_shift_tweets = '\n'.join(shift_tweets)

full_email = f"""\
From: {email_from}
To: {', '.join(email_to)}
Subject: New Shift Code Detected!


Click the links below to access the shift codes:
{stringified_shift_tweets}
"""

# NOTE: There's no subject line if we build full_email inside a conditional
# I was unable to figure out why, but building it outside the conditional
# seems to work.
if len(shift_tweets) != 0:
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(email_from, email_password)
        server.sendmail(email_from, email_to, full_email)
    except:
        print('Somethign went wrong...')

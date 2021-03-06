import logging
import os
import tweepy

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(funcName)s |%(message)s')

TWITTER_CONSUMER_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.environ.get('TWITTER_ACCESS_SECRET')


def authenticate():
    consumer_key = TWITTER_CONSUMER_KEY
    consumer_secret = TWITTER_CONSUMER_SECRET
    access_token = TWITTER_ACCESS_TOKEN
    access_token_secret = TWITTER_ACCESS_SECRET
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
        logging.info("Verified. Logging ins")
    except Exception as e:
        logging.error("Error creating API", exc_info=True)
        raise e
    print("API created")

    return api

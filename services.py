from __future__ import unicode_literals

import logging
import random
import time

from config import authenticate
from constants import MIN_INTERVAL, ONE, TEN, ZERO, NON_ENGAGED_FRIENDS_LIST
from utils import has_enough_retweets, rate_limit_ok, rate_limit_too_low

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(funcName)s |%(message)s')
_get_tags = lambda search_terms: random.choice(search_terms)


class TweetService:
    api = authenticate()

    def __init__(self):
        self.ids_cache = []
        self.tweets_cache = {}
        self.users_cache = {}
        self.dont_engage_list = self.api.get_list(owner_screen_name='sole_hunt', slug='sneaker-friends')

        self._get_ids_for_users_followed()
        # self.store_users(self.ids_cache)

    def _get_ids_for_users_followed(self, ids=None):
        if not ids or self.ids_cache:
            logging.info("Collecting ids for users I follow")
            ids = self.api.friends_ids()
        self.ids_cache.extend(ids)
        logging.info("Returning {} ids".format(len(ids)))
        return ids

    def _store_user(self, user_id=None):
        user = self.api.get_user(user_id)
        self.users_cache[user_id] = user

    def store_users(self, ids):
        for user_id in ids:
            self._store_user(user_id)

    def get_followed_by_followers_count(self, count=50000):
        # final store for desired users to return
        users_with_desired_followers_count = []
        # ensure ids_cache exists
        if not self.ids_cache:
            self._get_ids_for_users_followed()
        if not self.users_cache:
            self.store_users(self.ids_cache)
        for i in self.ids_cache:
            user = self.users_cache[i]
            logging.info("Getting tweets from {}".format(user.screen_name))
            if user.followers_count >= count:
                logging.info("Adding {} to return list".format(user.screen_name))
                users_with_desired_followers_count.append(user)
        return users_with_desired_followers_count

    def get_relevant_tweets_from_followed(self):
        """
        Gets tweet that mentioned a tag from followed list
        """
        users = self.get_followed_by_followers_count()
        rate_limit = self.get_rate_limit('users', '/users/show/:id')
        logging.info("followed_ids count: {}".format(len(users)))
        logging.info("monitoring rate limit: {}".format(rate_limit))

        while rate_limit_ok(rate_limit):
            logging.info("rate limit ok: {}".format(rate_limit_ok(rate_limit)))
            for _user in users:
                user = self.users_cache[_user.id]
                logging.info("Collecting user {}".format(user.screen_name))
                if not user.status.favorited:
                    self.tweets_cache[user.status.id] = {"tweet": user.status.text, 'status': user.status}
                    logging.info("Updated cache with tweet from {}".format(user.screen_name))
                    time.sleep(1)
                    rate_limit = self.get_rate_limit('users', '/users/show/:id')
                if rate_limit_too_low(rate_limit):
                    logging.warn("Rate limit met")
                    break
            break
        return self.tweets_cache

    def get_rate_limit(self, *args):
        """
        example call: self.get_rate_limits('users', '/users/show/:id')
        """
        query = "self.api.rate_limit_status()['resources']"
        for arg in args:
            query += "['{}']".format(arg)
        rate_limit_data = eval(query)
        return rate_limit_data

    def _engage_tweet(self, tweet):
        if tweet['status'].favorited:
            logging.info("Already liked")
            return
        logging.info("engaging tweet_id {}".format(tweet['status'].id))
        if has_enough_retweets(tweet['status'].retweet_count):
            if not tweet['status'].retweeted:
                try:
                    tweet['status'].retweet()
                    logging.info("Retweeted")
                except:
                    pass
        if not tweet['status'].favorited:
            try:
                tweet['status'].favorite()
                logging.info("Liked!")
            except:
                pass

    def engage_tweets(self, tweets=None):
        """
        query for all tweets in cache
        engage with a subset of tweets
        """
        limit = TEN
        if not self.tweets_cache or tweets:
            # create cache if it does not exist
            self.get_relevant_tweets_from_followed()
        for tweet_id, tweet in self.tweets_cache.iteritems():
            if self.should_engage(tweet['status']):
                if tweet['status'].entities['urls']:
                    url = tweet['status'].entities['urls'][0]['url']
                    logging.info("Engaging tweet {}".format(url))
                self._engage_tweet(tweet)
                limit -= ONE
                time.sleep(ONE)
                if limit <= ZERO:
                    limit = TEN
                    time.sleep(MIN_INTERVAL * 2)
                    continue

    def _reset(self):
        self.ids_cache = []
        self.tweets_cache = {}
        self.users_cache = {}
        self._get_ids_for_users_followed()

    def should_engage(self, tweet):
        member_screen_names = [member.screen_name for member in self.dont_engage_list.members()]
        if tweet.user.screen_name in member_screen_names:
            return False
        return True

    def follow_retweeter(self, tweet):
        """
        follow users that retweet
        :param tweet:
        :return:
        """
        is_retweeted = tweet.retweeted
        if is_retweeted:
            retweets = tweet.retweets()
            if len(retweets) > 16:
                retweets = retweets[:17]
            for retweet in retweets:
                # follow user and add to list
                user = retweet.user
                if not user.following:
                    user.follow()
                self.api.add_list_member(NON_ENGAGED_FRIENDS_LIST, user.id)
                logging.info("Added {} to non engaged list".format(user.screen_name))

    def follow_retweeters(self):
        followed = []
        for tweet in self.tweets_cache:
            self.follow_retweeter(tweet)
        logging.info("Followed users: {}".format(followed))
        return followed

# is retweeted
# follow retweeters
# add to list
# timestamp the follow
# 16 follows every 4 hours
tweetService = TweetService()

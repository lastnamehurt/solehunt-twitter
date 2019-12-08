from __future__ import unicode_literals

import logging
import random
import time

from config import authenticate
from constants import MIN_INTERVAL, ONE, TEN, ZERO
from utils import has_enough_retweets, rate_limit_ok, rate_limit_too_low

log = logging.getLogger("solehunt-twitter-bot")
_get_tags = lambda search_terms: random.choice(search_terms)


class TweetService:
    api = authenticate()

    def __init__(self):
        self.ids_cache = []
        self.tweets_cache = {}
        self.users_cache = {}
        self._get_ids_for_users_followed()
        # self.store_users(self.ids_cache)

    def _get_ids_for_users_followed(self, ids=None):
        if not ids or self.ids_cache:
            log.info("Collecting ids for users I follow")
            ids = self.api.friends_ids()
        self.ids_cache.extend(ids)
        log.info("Returning {} ids".format(len(ids)))
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
            log.info("Getting tweets from {}".format(user.screen_name))
            if user.followers_count >= count:
                log.info("Adding {} to return list".format(user.screen_name))
                users_with_desired_followers_count.append(user)
        return users_with_desired_followers_count

    def get_relevant_tweets_from_followed(self):
        """
        Gets tweet that mentioned a tag from followed list
        """
        users = self.get_followed_by_followers_count()
        rate_limit = self.get_rate_limit('users', '/users/show/:id')
        log.info("followed_ids count: {}".format(len(users)))
        log.info("monitoring rate limit: {}".format(rate_limit))

        while rate_limit_ok(rate_limit):
            log.info("rate limit ok: {}".format(rate_limit_ok(rate_limit)))
            for _user in users:
                user = self.users_cache[_user.id]
                log.info("Collecting user {}".format(user.screen_name))
                self.tweets_cache[user.status.id] = {"tweet": user.status.text, 'status': user.status}
                log.info("Updated cache with tweet from {}".format(user.screen_name))
                time.sleep(1)
                rate_limit = self.get_rate_limit('users', '/users/show/:id')
                if rate_limit_too_low(rate_limit):
                    log.warn("Rate limit met")
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
            log.info("Already liked")
            return
        log.info("engaging tweet_id {}".format(tweet['status'].id))
        if has_enough_retweets(tweet['status'].retweet_count):
            if not tweet['status'].retweeted:
                try:
                    tweet['status'].retweet()
                    log.info("Retweeted")
                except:
                    pass
        if not tweet['status'].favorited:
            try:
                tweet['status'].favorite()
                log.info("Liked!")
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
            log.info("Engaging tweet {}".format(tweet['status'].text))
            self._engage_tweet(tweet)
            limit -= ONE
            time.sleep(ONE)
            if limit <= ZERO:
                limit = TEN
                time.sleep(MIN_INTERVAL * 2)
                continue

    # def build_hashtags_list(self):
    #     """
    #     builds list of hashtags from default list
    #     """
    #     query = _get_tags(DEFAULT_TAGS)
    #     try:
    #         response = requests.get(RELATED_HASHTAGS_API.format(query))
    #         if response.status_code == RATE_LIMIT_EXCEEDED:
    #             log.info("Cant fetch. Waiting some time\n{}".format(response.text))
    #             time.sleep(60 * 2)
    #             response = requests.get(RELATED_HASHTAGS_API.format(query))
    #         res = json.loads(response.text)['result']
    #         return [r['hashtag'] for r in res]
    #     except Exception as (e):
    #         log.info("Exception: {}".format(e))
    #
    # def get_most_influenced_tweet(self, query=None):
    #     """
    #     I want the tag with the most tweets ->
    #     [tagToLike['tag'] for tagToLike in result if tagToLike['tweets'] == max([data['tweets'] for data in result])] -> [jordanretro]
    #     :param query:
    #     :return:
    #     """
    #     tags = self.build_hashtags_list()
    #     while True:
    #         if not query:
    #             query = random.choice(tags)
    #             # remove tag from tags list just in case this doesn't return good results
    #             tags.remove(query)
    #             log.info("Hashtag: {}".format(query))
    #         tweets = self.api.search(q=query, lang='en')
    #         try:
    #             post, user = [(tweet, tweet.user) for tweet in tweets if
    #                           tweet.user.followers_count == max([tweet.user.followers_count for tweet in tweets])][0]
    #             log.info("Liking Tweet: <{}>\nUser: {}".format(post.text, user.screen_name))
    #             return post, user
    #         except Exception as (e):
    #             log.info ("Issue with tag {}\n{}".format(query, e))
    #             continue
    #
    # def like_most_influenced_tweet(self, query=None):
    #     """
    #     Creates saved searches that can be used for automatic likes
    #     :param query:
    #     :return:
    #     """
    #     if not query:
    #         post, user = self.get_most_influenced_tweet()
    #     else:
    #         post, user = self.get_most_influenced_tweet(query=query)
    #     log.info("Liking Tweet: <{}>\nUser: {}".format(post.text, user.screen_name))
    #
    #     if not post.retweeted and user.followers_count >= MAX_FOLLOWERS_COUNT:
    #         post.retweet()
    #         post.favorite()
    #     if post.retweet_count >= RETWEET_THRESHOLD and user.followers_count >= MAX_FOLLOWERS_COUNT:
    #         user.follow()
    #     # if not post.favorited and user.followers_count >= MIN_FOLLOWERS_COUNT:
    #     #     post.favorite()
    #
    #     return post, user


tweetService = TweetService()

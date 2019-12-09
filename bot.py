from __future__ import absolute_import

import logging
import time

import schedule

from services import tweetService

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(funcName)s |%(message)s')


class SoleHuntBot(object):

    # execute in run() instead
    # def __init__(self):
    #     tweetService.engage_tweets()

    def schedule_engage_tweets(self, interval=45):
        schedule.every(interval).minutes.do(tweetService.engage_tweets)

    def schedule_reset(self, interval=20):
        schedule.every(interval).minutes.do(tweetService._reset)

    def run(self):
        """
        Runs scheduled jobs
        :return:
        """
        self.schedule_reset()
        # set schedule
        self.schedule_engage_tweets()
        logging.info(schedule.jobs)
        # run now
        tweetService.engage_tweets()


if __name__ == '__main__':
    logging.info('Starting Twitter Bot')
    SoleHuntBot().run()
    while True:
        schedule.run_pending()
        time.sleep(1)

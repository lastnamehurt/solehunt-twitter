from __future__ import absolute_import

import logging
import sys

import schedule

from services import tweetService

log = logging.getLogger("solehunt-twitter-bot")


class SoleHuntBot(object):

    # execute in run() instead
    # def __init__(self):
    #     tweetService.engage_tweets()

    def schedule_engage_tweets(self, interval=50):
        schedule.every(interval).minutes.do(tweetService.engage_tweets)

    def run(self):
        """
        Runs scheduled jobs
        :return:
        """
        # set schedule
        self.schedule_engage_tweets()
        log.info(schedule.jobs)
        # run now
        tweetService.engage_tweets()
        # start schedule
        while True:
            try:
                schedule.run_pending()
                log.info("Jobs: {}".format(schedule.jobs))
            except KeyboardInterrupt:
                sys.exit()


if __name__ == '__main__':
    log.info("Starting Twitter-Solehunt Bot")
    SoleHuntBot().run()

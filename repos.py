# twitter repo
from config import authenticate

class TwitterRepo(object):
    """
    This class serves as the interface for twitter data
    """

    def __init__(self):
        self.api = authenticate()

    def get_tweets(self, **filters):
        pass

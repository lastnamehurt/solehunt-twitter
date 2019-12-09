RELATED_HASHTAGS_API = 'https://ritetag.com/api/v1/search/hashtags/{}'

DEFAULT_TAGS = [
    'jordanretro',
    'nikeairmax',
    'yeezy',
    'jumpman',
    'hypebeast',
    'sneakerheads',
    'adidashumanmade',
    'checkyafootwork',
    'adidasoriginals',
    'offwhite',
    'guccishoes',
    'moncler',
    'ralphlauren',
    'armaniexchange',
]

# get tags -> 1 tag
# search tweets with tag
# find matching user with most followers
# like the tweet
NON_ENGAGED_FRIENDS_LIST = 'sneaker-friends'
RETWEET_THRESHOLD = 20
MAX_FOLLOWERS_COUNT = 500
MIN_FOLLOWERS_COUNT = 500
MIN_INTERVAL = 30

RATE_LIMIT_RESET_COUNT = 100 # needs to be high enough to not exceed the limit

RATE_LIMIT_EXCEEDED = 429

ZERO = 0
TEN = 10
ONE = 1
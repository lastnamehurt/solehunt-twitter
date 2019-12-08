from constants import RATE_LIMIT_RESET_COUNT, RETWEET_THRESHOLD

# TODO: convert these to defs
get_limit_reset = lambda limit: limit['reset']
get_rate_limit = lambda limit: limit['limit']
get_remaining_calls = lambda limit: limit['remaining']
rate_limit_ok = lambda limit: get_remaining_calls(limit) >= RATE_LIMIT_RESET_COUNT
rate_limit_too_low = lambda limit: get_remaining_calls(limit) < RATE_LIMIT_RESET_COUNT
has_enough_retweets = lambda retweet_count: retweet_count >= RETWEET_THRESHOLD

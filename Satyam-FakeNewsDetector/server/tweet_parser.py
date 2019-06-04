import re
import functools

import tweepy
from apikey import ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)

api = tweepy.API(auth)

pattern = "https://twitter.com/\w+/status/(\d+)"
compiled = re.compile(pattern=pattern)


def get_relevant_tweet_data(tweet):
    print(tweet)
    relevant_data = dict(
        tweet_id=[tweet["id"]],
        created_at=[tweet["created_at"]],
        retweet_count=[tweet["retweet_count"]],
        text=[tweet["text"]],
        user_screen_name=[tweet["user"]["screen_name"]],
        user_verified=[tweet["user"]["verified"]],
        user_friends_count=[tweet["user"]["friends_count"]],
        user_followers_count=[tweet["user"]["followers_count"]],
        user_favourites_count=[tweet["user"]["favourites_count"]],
        num_hashtags=[len(tweet["entities"]["hashtags"])],
        num_mentions=[len(tweet["entities"]["user_mentions"])],
        num_urls=[len(tweet["entities"]["urls"])]
    )

    return relevant_data


def get_replies(tweet):
    user = tweet.user.screen_name
    tweet_id = tweet.id
    max_id = None
    logging.info("looking for replies to: %s" % tweet_url(tweet))
    while True:
        q = urllib.parse.urlencode({"q": "to:%s" % user})
        try:
            replies = t.GetSearch(raw_query=q, since_id=tweet_id, max_id=max_id, count=100)
        except twitter.error.TwitterError as e:
            logging.error("caught twitter api error: %s", e)
            time.sleep(60)
            continue
        for reply in replies:
            logging.info("examining: %s" % tweet_url(reply))
            if reply.in_reply_to_status_id == tweet_id:
                logging.info("found reply: %s" % tweet_url(reply))
                yield reply
                # recursive magic to also get the replies to this reply
                for reply_to_reply in get_replies(reply):
                    yield reply_to_reply
            max_id = reply.id
        if len(replies) != 100:
            break


@functools.lru_cache(maxsize=128)
def get_tweet(url):
    tweet_id = compiled.findall(url)
    if not tweet_id:
        raise ValueError()
    tweet_id = tweet_id[0]
    tweet = api.get_status(tweet_id)._json
    replies = get_replies(tweet)

    return get_relevant_tweet_data(tweet),replies


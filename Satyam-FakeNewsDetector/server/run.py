import functools
import flask
from flask import request, jsonify

from tweet_parser import get_tweet,get_replies
from source.FakeNewsDetector import check_tweet as FakeNewsDetector_checkTweet

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Fake News Detector</h1>"


@functools.lru_cache(maxsize=128)
def _check_tweet(url):
    response = dict()
    response["url"] = url

    tweet_data, tweet_replies = get_tweet(url)
    response["tweet"] = tweet_data
    print(tweet_replies)

    response["fake_news"] = float(FakeNewsDetector_checkTweet(tweet_data))

    return jsonify(response)


@app.route('/api/v1/checkTweet', methods=['GET'])
def check_tweet():
    url = request.args['url']
    return _check_tweet(url)


app.run()

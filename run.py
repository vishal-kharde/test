import functools
import flask
from flask import request, jsonify


from rumoureval.__main__ import main


from server.tweet_parser import get_tweet,get_replies
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


    """
    # Predicting classes for tweets_eval
    start_time = time()
    base_predictions = base_pipeline.predict(tweets_eval)
    query_predictions = query_pipeline.predict(tweets_eval)

    # Boosting
    predictions = []
    for i in range(len(base_predictions)):
        if query_predictions[i] == 'query':
            predictions.append('query')
        else:
            predictions.append(base_predictions[i])
     """
       
    return jsonify(response)


@app.route('/api/v1/checkTweet', methods=['GET'])
def check_tweet():
    url = request.args['url']
    return _check_tweet(url)


def _run_on_start():
    global base_pipeline
    global query_pipeline
    pipeline_result = main(None)
    base_pipeline = pipeline_result[0]
    query_pipeline = pipeline_result[1]
    print('_run_on_stat_ invoked')
    

global base_pipline
global query_pipeline
base_pipeline = None
query_pipeline = None
if __name__ == '__main__':
    _run_on_start()
    app.run()

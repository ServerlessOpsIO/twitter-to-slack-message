'''Twitter to Slack formatted message'''

import json
import logging
import os
import time

import boto3

log_level = os.environ.get('LOG_LEVEL', 'INFO')
logging.root.setLevel(logging.getLevelName(log_level))  # type: ignore
_logger = logging.getLogger(__name__)

TWITTER_URL_BASE = 'https://twitter.com'

AWS_SNS_TOPIC_ARN = os.environ.get('AWS_SNS_TOPIC_ARN')
SNS = boto3.client('sns')

def _format_slack_media_attachment(media: dict) -> dict:
    '''Format a media attachment for slack'''
    url = media.get('media_url_https')
    a = {
        'text': url,
        'image_url': url
    }

    return a


def _format_slack_message_from_tweet(tweet: dict) -> dict:
    '''Given a tweet, format a slack message'''

    msg = {}
    msg['attachments'] = []

    author_info = _get_tweet_author_info(tweet)
    tweet_data = {
        "author_name": author_info['author_name'],
        "author_subname": author_info['author_subname'],
        "author_icon": author_info['author_icon'],
        "text": tweet.get('text'),
        "service_name": "twitter #awswishlist",
        "service_url": "https://twitter.com/search?q=%23awswishlist&src=typd",
        "footer": "Twitter #AWSWishlist",
        "footer_icon": "https://a.slack-edge.com/6e067/img/services/twitter_pixel_snapped_32.png",  # noqa
        "ts": _get_tweet_time(tweet),
        "mrkdwn": True
    }

    tweet_url = _get_tweet_url(tweet)

    # XXX: Only Author link is showing up in tweet
    tweet_data['author_link'] = tweet_url
    tweet_data['from_url'] = tweet_url
    tweet_data['original_url'] = tweet_url

    tweet_data['fallback'] = _get_fallback_text(tweet)
    msg['attachments'].append(tweet_data)

    if tweet.get('extended_entities') and tweet.get('extended_entities').get('media'):
        media_attachments = tweet.get('extended_entities').get('media')
        for media in media_attachments:
            slack_attachment = _format_slack_media_attachment(media)
            msg['attachments'].append(slack_attachment)

    _logger.debug('Slack message: {}'.format(json.dumps(msg)))

    return msg


def _get_fallback_text(tweet: dict) -> str:
    '''Return a fallback test string'''
    screen_name = tweet.get('user').get('screen_name')
    s = '<{author_link}|@{screen_name}>: {text}'.format(
        author_link=_get_tweet_author_url(screen_name),
        screen_name='@{}'.format(screen_name),
        text=tweet.get('text')
    )

    return s


def _get_tweet_time(tweet: dict) -> int:
    '''Return tweet time suitable as a Slack timestamp'''
    time_format = '%a %b %d %H:%M:%S +0000 %Y'
    time_string = tweet.get('created_at')
    return int(time.mktime(time.strptime(time_string, time_format)))


def _get_tweet_author_url(screen_name: str, base: str=TWITTER_URL_BASE) -> str:
    '''Return the Tweet URL based on Id.'''
    return '/'.join([base, screen_name])


def _get_tweet_url(tweet: dict, base: str=TWITTER_URL_BASE) -> str:
    '''Return the Tweet URL based on Id.'''
    tweet_author = tweet.get('user').get('screen_name')
    tweet_id = tweet.get('id_str')
    return '/'.join([base, tweet_author, 'status', tweet_id])


def _get_tweet_author_info(tweet: dict) -> dict:
    '''Return the Tweet author info.'''
    author_info = {}
    author_info['author_name'] = tweet.get('user').get('name')
    author_info['author_subname'] = '@{}'.format(tweet.get('user').get('screen_name'))
    author_info['author_icon'] = tweet.get('user').get('profile_image_url_https')
    return author_info


def _publish_sns_message(sns_topic_arn: str, message: dict) -> None:
    '''Publish message to SNS topic'''
    _logger.debug('SNS message: {}'.format(json.dumps(message)))
    r = SNS.publish(
        TopicArn=sns_topic_arn,
        Message=json.dumps(message)
    )

    return r


def handler(event: list, context: dict):
    '''Function entry'''
    _logger.debug('Event received: {}'.format(event))
    for tweet in event:
        tweet_data = json.loads(tweet)
        slack_message = _format_slack_message_from_tweet(tweet_data)
        r = _publish_sns_message(AWS_SNS_TOPIC_ARN, slack_message)

    resp = {'status': 'OK'}
    _logger.debug('Response: {}'.format(json.dumps(resp)))
    return resp


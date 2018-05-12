# twitter-to-slack-message
[![Serverless](http://public.serverless.com/badges/v3.svg)](http://www.serverless.com)
[![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)

Convert a Twitter tweet into a Slack API _chat.postMessage_ message.

![System Architecture](/diagram.png?raw=true "System Architecture")

## Service Interface

* __Event Type:__ AWS Lambda invocation payload
* __Event Message:__ The message shape is a list of Twitter message JSON strings.

Example event:
```
[
  '{"id": 210462857140252672, "text": "An opnion that is obviously wrong", ... }',
]
```

## Example system

This nanoservice is intended to be used to construct a functional application.

### Twitter To Slack Publisher Application

This application searches the Twitter stream and publishes tweets matching a search term to Slack.

The application requires the following services.  Deploy them in the order listed below.

1. twitter-to-slack-message: This service
2. [aws-serverless-twitter-event-source](https://serverlessrepo.aws.amazon.com/applications/arn:aws:serverlessrepo:us-east-1:077246666028:applications~aws-serverless-twitter-event-source): Searched the Twitter event stream.
3. aws-sns-to-slack-publisher: Publishes messages to Slack.

The final application will be as follows:

![System Architecture](/twitter-to-slack-publisher.png?raw=true "Application Architecture")


## Deployment

This application is intended to be deployed using [AWS Serverless Application Repository](https://aws.amazon.com/serverless/serverlessrepo/).  However, [Serverless Framework](https://www.serverless.com) is also supported.

## Exports

* __${AWS::StackName}-SlackMessageSnsTopicArn__: AWS SNS topic ARN where health events are published to.

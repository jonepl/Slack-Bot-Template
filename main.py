from slackclient import SlackClient
import time;

import config.creds as config

slack_client = SlackClient(config.slack['token'])

def slackConnect():
    return slack_client.rtm_connect();

def another():
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            print(user.get('name'));

def readReadRTM():
    print(slack_client.rtm_read());
    time.sleep(1);


# https://www.youtube.com/watch?v=QFPT37NoALA

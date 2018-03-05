from slackclient import SlackClient
import config.creds

slack_client = SlackClient()

def slackConnect():
    return slack_client.rtm_connect(config.slack['token']);

def another():
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        users = api_call.get('members')
        for user in users:
            print(user.get('name'));

another();
# https://www.youtube.com/watch?v=QFPT37NoALA

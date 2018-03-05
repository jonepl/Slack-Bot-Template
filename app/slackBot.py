from slackclient import SlackClient
import config.creds


# For all Slack bot methods
class SlackBot():

    def __init__(self, token):
        self.slack_client = SlackClient()

    def readReadRTM():
        print(self.slack_client.rtm_read());
        time.sleep(1);

    def getBotID():
        pass;

    def getSlackInput():
        pass;

    def writeToSlack(channel, message):
        pass;

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

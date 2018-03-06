import sys;
from slackclient import SlackClient

# For all Slack bot methods
class SlackBot():

    def __init__(self, token=None):
        if(token is None) :
            print("Error occured!")
            sys.exit(-1);
        self.slack_client = SlackClient(token)

    def connectToSlack(token):
        slack_client.rtm_connect(token);

    def readReadRTM(self):
        print(self.slack_client.rtm_read());
        time.sleep(1);

    def getListofMembers():
        api_call = slack_client.api_call("users.list")
        if api_call.get('ok'):
            users = api_call.get('members')
            for user in users:
                print(user.get('name'));

    def getBotID(self):
        print("Geting bot ID");

    def retrieveSlackInput(self):
        print("Retrieving input from slack");

    def writeToSlack(self, channel, message):
        print(f"Writing message: {message} to channel {channel}");

    def getListofUsers(self):
        print("Getting the list of users from slack");

if __name__ == '__main__':
    pass;

# https://www.youtube.com/watch?v=QFPT37NoALA

import sys;
from abc import ABCMeta, abstractmethod;
import time;
from slackclient import SlackClient

class SlackBot():

    def __init__(self, token=None):
        if(token is None) :
            print("A valid token must be past as a parameter");
            sys.exit(-1);
        #self.botId = self.getBotId();
        self.token = token;
        self.slack_client = SlackClient(self.token);

    # Connects to slack
    def connect(self, token=None):
        return self.slack_client.rtm_connect(self.token);

    # Reads all channels and return raw input
    def readChannels(self):
        return self.slack_client.rtm_read();

    # Writes the message to specified slack  channel
    def writeToSlack(self, channel, message):
        return self.slack_client.api_call('chat.postMessage', channel=channel, text = message, as_user=True);

    # Retrieves a detailed list of all members in slack group
    def getMemberList(self):
        userList = [];
        api_call = self.slack_client.api_call("users.list");
        if api_call.get('ok'):
            return api_call.get('members');

    # Retrieves a detailed list of all channels in slack
    def getChannelList(self) :
        channelList = []
        api_call = self.slack_client.api_call("channels.list");
        if api_call.get('ok'):
            print(api_call);
            return api_call;

    # Handles raw input slack and determines what action to take
    def parseRawInput(self, input):
        raise NotImplementedError("Please Implement this method.")

    # TODO: Implement this for debugging
    def userIdToUserName(self):
        pass;

    # TODO: Implement this
    def getBotInfo(self) :
        pass;

    # TODO Implement this for debugging
    def getBotName(self) :
        pass;

    # TODO Implement this for debugging
    def getBotID(self, botName):
        pass;
        # api_call = self.slack_client.api_call('users.list');
        # users = api_call['members'];
        # result = None;
        # for user in users :
        #     if 'name' in user and botName in user.get('name') and not user.get('deleted') :
        #         result = user.get('id');
        #         break;
        # return result;

if __name__ == '__main__':
    pass;

# https://www.youtube.com/watch?v=QFPT37NoALA

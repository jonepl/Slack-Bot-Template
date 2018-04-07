from slackclient import SlackClient;

import sys;
from abc import ABCMeta, abstractmethod;
import time;

class SlackBot():
    def __init__(self, token=None):
        if(token is None) :
            print("A valid token must be past as a parameter");
            sys.exit(-1);
        self.token = token;
        self.botId = None
        self.botName = None;
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
        api_call = self.slack_client.api_call("users.list");
        if api_call.get('ok'):
            return api_call.get('members');

    # Retrieves a detailed list of all channels in slack
    def getChannelList(self) :
        api_call = self.slack_client.api_call("channels.list");
        if api_call.get('ok'):
            print(api_call);
            return api_call;

    # Handles raw input slack and determines what action to take
    def parseRawInput(self, input):
        raise NotImplementedError("Please Implement this method.");

    # TODO: Implement this for debugging
    def userIdToUserName(self):
        pass;

    # TODO: Implement this
    def getBotInfo(self) :
        pass;

    # TODO Implement this for debugging
    def getBotName(self) :
        if(self.botName is None) :
            self.botName = self.slack_client.server.login_data['self']['name'];
        return self.botName

    # TODO Implement this for debugging
    def getBotID(self):
        if(self.botId is None) :
            print("initializing BOTID");
            self.botId = self.slack_client.server.login_data['self']['id'];
        return self.botId

if __name__ == '__main__':
    pass;

# https://www.youtube.com/watch?v=QFPT37NoALA

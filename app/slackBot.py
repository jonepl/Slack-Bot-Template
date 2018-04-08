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

    # Retrieves channel information
    def getChannelInfo(self, channel) :
        api_call = self.slack_client.api_call("channels.info", channel=channel)
        return api_call;

    # Retrieves group information
    def getGroupInfo(self, channel) :
        api_call = self.slack_client.api_call("groups.info", channel=channel)
        return api_call

    # TODO: Implement this
    def getBotInfo(self) :
        pass;

    # Retrieves the name of the bot
    def getBotName(self) :
        if(self.botName is None) :
            self.botName = self.slack_client.server.login_data['self']['name'];
        return self.botName

    # Retrieves the bot's ID
    def getBotID(self):
        if(self.botId is None) :
            self.botId = self.slack_client.server.login_data['self']['id'];
        return self.botId

    def postFile(self, channel, filePath, filename) :
        api_call = self.slack_client.api_call("files.upload", channel=channel, file=filePath, filename=filename);

if __name__ == '__main__':
    pass;

'''
For those who're still experiencing this,

Instead of following,

files = {'file': open('test.png', 'rb')}
client.api_call('files.upload', channels=[...], filename='pic.png', files=files)

Try this:

client.api_call('files.upload', channels=[...], filename='pic.png', files=open('test.png', 'rb'))

channels param requires a single string, not a list
files param should be a file object, not a dict
For example, I successfully uploaded a plain text file through:

self.sc.api_call("files.upload", filename='result.txt', channels='#somechannel', file= io.BytesIO(str.encode(content)))
'''
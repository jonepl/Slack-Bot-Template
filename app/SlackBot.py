'''
File: SlackBot.py
Description: Abstraction of a Slackbot implementation. This class should have all general functionality
             for an instance of a Slackbot.
'''
import sys
import logging

from slackclient import SlackClient
from abc import ABCMeta, abstractmethod

try :
    import Queue
except:
    import queue as Queue

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s : %(name)s : %(message)s')

file_handler = logging.FileHandler('logs/SlackBot.log')
stream_handler = logging.StreamHandler()

file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

file_handler.setLevel(logging.INFO)
stream_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

class SlackBot():
    def __init__(self, token=None, debug=False):
        if(token is None) :
            if(debug) : logger.error('A valid token must be past as a parameter')
            sys.exit(-1)
        self.debug = debug
        self.requestQueue = None
        self.responseQueue = None
        self.token = token
        self.botId = None
        self.botName = None
        self.slack_client = SlackClient(self.token)
        if(self.debug) : logger.debug('SlackBot instance successfully created.')

    # Connects to slack
    def connect(self):
        if(self.debug) : logger.info('Connection to Slack via token')
        return self.slack_client.rtm_connect(self.token)

    # Reads all channels and return raw input
    def readChannels(self):
        return self.slack_client.rtm_read()

    # Writes the message to specified slack channel
    def writeToSlack(self, channel, message):
        return self.slack_client.api_call('chat.postMessage', channel=channel, text = message, as_user=True)

    # Attaches a file or a code snippet to slack channel
    def writeToFile(self, channel, filePath) :
        return self.slack_client.api_call("files.upload", channels=channel, file=open(filePath, 'rb'))

    def writeToSharedFile(self, channel, filePath):
        return self.slack_client.api_call('files.upload', channels=channel, file=open(filePath, 'rb'), filename="Lorem.docx", title="Dat Boi", filetype="space")


    # Retrieves a detailed list of all members in slack group
    def getMemberList(self):
        api_call = self.slack_client.api_call("users.list")
        if api_call.get('ok'):
            return api_call.get('members')
        else :
            if(self.debug) : logger.error("Issue occurred when getting member list")

    # Retrieves a detailed list of all channels in slack
    def getChannelList(self) :
        api_call = self.slack_client.api_call("channels.list")
        if api_call.get('ok'):
            return api_call
        else :
            if(self.debug) : logger.error("Issue occurred when getting channel list")

    # Handles raw input slack and determines what action to take
    def parseRawInput(self, input):
        raise NotImplementedError("Please Implement this method.")

    # TODO: Implement this for debugging
    def userIdToUserName(self):
        pass

    # Retrieves channel information
    def getChannelInfo(self, channel) :
        api_call = self.slack_client.api_call("channels.info", channel=channel)
        return api_call

    # Retrieves group information
    def getGroupInfo(self, channel) :
        api_call = self.slack_client.api_call("groups.info", channel=channel)
        return api_call

    # TODO: Implement this
    def getBotInfo(self) :
        pass

    # Retrieves the name of the bot
    def getBotName(self) :
        if(self.botName is None) :
            self.botName = self.slack_client.server.login_data['self']['name']
        return self.botName

    # Retrieves the bot's ID
    def getBotID(self):
        if(self.botId is None) :
            self.botId = self.slack_client.server.login_data['self']['id']
        return self.botId

if __name__ == '__main__':
    pass
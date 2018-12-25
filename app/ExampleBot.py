'''
File: ExampleBot.py
Description: Implementation of a Slackbot Abstract Class. This class should have all bot specific functionality
             for an instance of a Slackbot.
'''

from SlackBot import SlackBot
from MessageHandler import MessageHandler

import time
try :
    import Queue
except:
    import queue as Queue
import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s : %(name)s : %(message)s')

file_handler = logging.FileHandler('logs/ExampleBot.log')
stream_handler = logging.StreamHandler()

file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

class ExampleBot(SlackBot) :

    def __init__(self, token, debug=False):
        super().__init__(token, debug)
        self.users = {}
        self.running = False
        self.messageResponseQueue = Queue.Queue()
        self.messageRequestQueue = Queue.Queue()
        self.MessageHandler = None
        self.debug = debug
        if(self.debug) : logger.debug('ExampleBot successfully created')

    # Entry method for Program
    def run(self) :
        self.running = True
        if(self.connect()) :
            # Starts thread and passes BotID
            self.setUpThreads()
            while(self.running) :
                try:    
                    rawInput = self.readChannels()
                    if(self.debug) : logger.debug(rawInput)
                    if (not self.isEmpty(rawInput) and self.notSelf(rawInput) and (self.botMentioned(rawInput) or self.directMessaged(rawInput)) ) :

                        self.messageRequestQueue.put(rawInput)
                        if(self.debug) : logger.info("Added message to queue: {}".format(str(rawInput)))

                    self.checkResponseQueue()
                    time.sleep(0.5)
                except (KeyboardInterrupt, SystemError) :
                    if(self.debug) : logger.info("KeyboardInterrupt Exception Found. Killing MessageHandler Thread")
                    self.MessageHandler.kill()
                    self.running = False
        else :
            if(self.debug) : logger.error("Unable to connect to Slack.")   

    def setUpThreads(self) :
        self.MessageHandler = MessageHandler(self.messageRequestQueue, self.messageResponseQueue, self.getBotID(), self.debug)
        self.MessageHandler.setName("MessageHandler Thread 1")
        self.MessageHandler.daemon = True
        self.MessageHandler.start()
        if(self.debug) : logger.info("Started thread: {}".format("MessageHandler Thread 1"))

    # Check Queue to see if any messages are ready to be sent
    def checkResponseQueue(self) :
        
        if(not self.messageResponseQueue.empty()) :
            response = self.messageResponseQueue.get()
            if(self.debug) : logger.info("Response found, handling response: \n{}\n".format(str(response)))
            self.messageResponseQueue.task_done()
            self.handleResponse(response)

    # Utilizes response object to response to user
    def handleResponse(self, response) :
        if(response['action'] == "writeToSlack") :
            # TODO: Handle unsuccess result and log failures
            if(self.debug) : logger.info("Writing message {} to slack channel {}".format(str(response), str(response['channel'])))
            result = self.writeToSlack(response['channel'], response['response'])
        elif(response['action'] == "writeToFile") :
            # TODO: Make dynamic
            if(self.debug) : logger.info("Writing file {} to slack channel {}".format(str(response), str(response['channel'])))
            result = self.writeToFile(response['channel'], response['response'])
        elif(response['action'] == "writeToSharedFile") :
            if(self.debug) : logger.debug("Writing shared file {} to slack channel {}".format(str(response), str(response['channel'])))
            result = self.writeToSharedFile(response['channel'], response['response'])
        else :
            if(self.debug) : logger.warning("Error has occured while handling response {} to channel {}".format(str(response), str(response['channel'])))

    # Determines if the bot is being DMed
    def directMessaged(self, rawInput) :
        if('channel' in rawInput[0]): 
            if (not self.getGroupInfo(rawInput[0]['channel']).get('ok')) and (not self.getChannelInfo(rawInput[0]['channel']).get('ok')) :
                return True
            else :
                return False
        else :
            return False
    
    # Determines if the bot is mentioned in the raw input
    def botMentioned(self, rawInput) :
        if('text' in rawInput[0]) :
            if(self.getBotID() in rawInput[0]['text']) : return True
        else : return False

    # Detects if raw input is Empty
    def isEmpty(self, rawInput) :
        if not rawInput : return True
        else : return False

    # Determines if the raw input was sent by this bot
    def notSelf(self, rawInput) :
        if(rawInput[0].get('user') == self.getBotID()) : return False
        else : return True

if __name__ == '__main__':
    from slackBot import SlackBot
    xBot = ExampleBot("place_token_here")
'''
File: ExampleBot.py
Description: Implementation of a Slackbot Abstract Class. This class should have all bot specific functionality
             for an instance of a Slackbot.
'''
from app.SlackBot import SlackBot;
from app.MessageHandler import MessageHandler;

import time;
try :
    import Queue
except:
    import queue as Queue

class ExampleBot(SlackBot) :

    def __init__(self, token, debug=True):
        super().__init__(token);
        self.users = {};
        self.debug = debug;
        self.running = False;
        self.responseQueue = Queue.Queue();
        self.requestQueue = Queue.Queue();
        self.MessageHandler = None;

    # Entry method for Program
    def run(self) :
        self.running = True;
        if(self.connect(self.token)) :
            # Starts thread and passes BotID
            self.setUpThreads();

            while(self.running) :
                try:    
                    rawInput = self.readChannels();
                    print(rawInput);
                    # DEBUG print("Request Queue: " + str(self.requestQueue.qsize()))
                    if (not self.isEmpty(rawInput) and self.notSelf(rawInput) and (self.botMentioned(rawInput) or self.directMessaged(rawInput)) ) :
                        self.requestQueue.put(rawInput);

                    self.checkResponseQueue();
                    time.sleep(0.5);
                except (KeyboardInterrupt, SystemError) :
                    print("\n~~~~~~~~~~~KeyboardInterrupt Exception Found~~~~~~~~~~~\n");
                    self.MessageHandler.kill();
                    self.running = False;                

    def setUpThreads(self) :
        self.MessageHandler = MessageHandler(self.requestQueue, self.responseQueue, self.getBotID());
        self.MessageHandler.setName("Thread 1");
        self.MessageHandler.daemon = True;
        self.MessageHandler.start();

    # Check Queue to see if any messages are ready to be sent
    def checkResponseQueue(self) :
        if(not self.responseQueue.empty()) :
            response = self.responseQueue.get();
            self.responseQueue.task_done()
            # DEBUG print("~~~~~~~~~~~~~~~ CHECK QUEUE ~~~~~~~~~~~~~~~")
            # DEBUG print(response)
            self.handleResponse(response);

    # Utilizes response object to response to user
    def handleResponse(self, response) :
        if(response['action'] == "writeToSlack") :
            # TODO: Handle unsuccess result and log failures
            result = self.writeToSlack(response['channel'], response['response'])
        elif(response['action'] == "writeToFile") :
            # TODO: Handle unsuccess result and log failures
            result = self.writeToFile(response['channel']);
        else :
            print("Error has occured");

    # Determines if the bot is being DMed
    def directMessaged(self, rawInput) :
        if('channel' in rawInput[0]): 
            if (not self.getGroupInfo(rawInput[0]['channel']).get('ok')) and (not self.getChannelInfo(rawInput[0]['channel']).get('ok')) :
                return True;
            else :
                return False;
        else :
            return False;
    
    # Determines if the bot is mentioned in the raw input
    def botMentioned(self, rawInput) :
        if('text' in rawInput[0]) :
            if(self.getBotID() in rawInput[0]['text']) : return True;
        else : return False;

    # Detects if raw input is Empty
    def isEmpty(self, rawInput) :
        if not rawInput : return True;
        else : return False

    # Determines if the raw input was sent by this bot
    def notSelf(self, rawInput) :
        if(rawInput[0].get('user') == self.getBotID()) : return False;
        else : return True;

if __name__ == '__main__':
    from slackBot import SlackBot;
    xBot = ExampleBot("place_token_here");
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
        self.MessageHandler = None

    # Entry method for Program
    def run(self) :
        self.running = True;
        if(self.connect(self.token)) :
            counter = 0
            while(self.running) :
                try:    
                    rawInput = self.readChannels();
                    print(rawInput);
                    if (not self.isEmpty(rawInput)) :
                        
                        # if max thread not exceed.
                        mhandler = MessageHandler(self.responseQueue, rawInput, self.directMessaged(rawInput),  self.getBotID());
                        mhandler.setName('Thread ' + str(counter))
                        mhandler.daemon = True
                        counter = counter + 1;
                        print("Deploying: " + mhandler.getName())
                        mhandler.start();
                        print(mhandler.active_count())
                        
                        # DEBUG print("STATUS: " + str(status))
                    self.checkResponseQueue();
                    time.sleep(1);
                except (KeyboardInterrupt, SystemError) :
                    print("\n~~~~~~~~~~~KeyboardInterrupt Exception Found~~~~~~~~~~~\n");
                    self.running = False;                

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
            self.writeToSlack(response['channel'], response['response'])
        elif(response['action'] == "writeToFile") :
            pass;
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
    
    # Detects if raw input is Empty
    def isEmpty(self, rawInput) :
        if not rawInput : return True;
        else : return False

if __name__ == '__main__':
    from slackBot import SlackBot;
    xBot = ExampleBot("");

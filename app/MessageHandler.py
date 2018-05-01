'''
File: MessageHandler.py
Description: Handles raw input and determines an appropriate response to send back to the user
'''
import random
from threading import Thread
try :
    import Queue
except:
    import queue as Queue

# Sentences we'll respond with if the user greeted us
SUCCESS = 0;
FAILURE = -1;
GREETING_KEYWORDS = ["hey", "hi", "greetings", "sup", "hello"]
SERVICE_KEYWORDS = ["give", "file"]
GREETING_RESPONSES = ["Sup bro.", "Hey.", "What it do!", "What up homie?", "Howdy."]

class MessageHandler(Thread):
    
    def __init__(self, requestQueue, responseQueue, botID) :
        Thread.__init__(self)
        self.running = True;
        self.requestQueue = requestQueue;
        self.responseQueue = responseQueue;
        self.botID = botID

    # NOTE: Will be used for threading
    def run(self) :
        # Blocking will cause this thread to sleep
        while(self.running) :
            rawInput = self.requestQueue.get();
            self.handle(rawInput);      

    # Parses all raw input
    ### Assumptions: All rawInput sent to this message should be of type Array and not empty
    def handle(self, rawInput):
        response = None
        if (not self.isEmpty(rawInput)) :
            # Verify if rawInput is valid 
            if(self.isAMessage(rawInput)) :
                response = self.parseInput(rawInput);
                # DEBUG print("~~~~~~~~~~~~~~~~ RESPONSE ~~~~~~~~~~~~~~")
                # DEBUG print(response)
                self.responseQueue.put(response);
                # DEBUG print("Completed SUCCESS");
                return SUCCESS;
            else :
                # DEBUG print("Completed FAILURE");
                return FAILURE;
    
    def kill(self) :
        self.running = False;

    # Parses the raw slack input into parts
    def parseInput(self, rawInput) :

        responseObject = {};
        user = rawInput[0]['user'];
        message = rawInput[0]['text'];
        channel = rawInput[0]['channel'];

        action, response = self.determineAction(message, responseObject);
        
        responseObject['action'] = action;
        responseObject['response'] = response
        responseObject["user"] = str(user);
        responseObject['message'] = str(self.stripTag(message));
        responseObject['channel'] = str(channel);
        
        return responseObject;

    # Determine what action to take depending on the message
    def determineAction(self, message, responseObject) :
        if(self.isGreeting(message)) :
            return ("writeToSlack",random.choice(GREETING_RESPONSES));
        elif(self.isServiceRequest(message)) :
            # TODO: Improve to handle all types of services
            return ("writeToFile", "Writing this junk to a file");
        else :
            return ("writeToSlack", "Im not sure how to decipher \"" + self.stripTag(message) + "\".")

    # Determines if a message contains a greeting word
    def isGreeting(self, message) :
        for greeting in GREETING_KEYWORDS :
            if(greeting in message.lower()) :
                return True;
        return False;

    # TODO Implement to interact Service Manager
    def isServiceRequest(self, message) :
        for command in SERVICE_KEYWORDS :
            if(command in message.lower()) :
                return True;
        return False;

    # Removes the Slack bot ID from a message
    def stripTag(self, message) :
        botTag = "<@" + self.botID + ">"
        return message.replace(botTag, '');

    # Determines if the raw input was sent by this bot
    def notSelf(self, rawInput) :
        if(rawInput[0].get('user') == self.botID) : return False;
        else : return True; 
    
    # Detect if a users is typing
    def isTyping(self, rawInput) :
        if(rawInput[0].get('type') == 'user_typing') : return True;
        else : return False

    # Detects if raw input is Empty
    def isEmpty(self, rawInput) :
        if not rawInput : return True;
        else : return False

    # Detects if the raw input is a message
    def isAMessage(self, rawInput) :
        if(rawInput[0].get('type') == 'message') : return True;
        else : return False;

    # Determines if the bot is mentioned in the raw input
    def botMentioned(self, rawInput) :
        if('text' in rawInput[0]) :
            if(self.getBotID() in rawInput[0]['text']) : return True;
        else : return False;
    

    '''Example Message Handling using Textblob'''
    #  def filter_response(self, response):
    #     """Don't allow any words to match our filter list"""
    #     tokenized = response.split(' ')
    #     for word in tokenized:
    #         if '@' in word or '#' in word or '!' in word:
    #             raise UnacceptableUtteranceException()
    #         for s in FILTER_WORDS:
    #             if word.lower().startswith(s):
    #                 raise UnacceptableUtteranceException()   

    #     cleaned = preprocess_text(sentence)
    #     parsed = TextBlob(cleaned)

    #     pronoun, noun, adjective, verb = find_candidate_parts_of_speech(parsed)

    #     resp = check_for_comment_about_bot(pronoun, noun, adjective)
        
    #     if not resp:
    #         resp = check_for_greeting(parsed)

    #     if not resp :
    #         resp = random.choice(NONE_RESPONSES)
    #     elif pronoun == 'I' and not verb :
    #         resp = random.choice(COMMENTS_ABOUT_SELF)
    #     else:
    #         resp = construct_response(pronoun, noun, verb)
        
    #     if not resp:
    #         resp = random.choice(NONE_RESPONSES)

    #     logger.info("Returning phrase '%s'", resp)

    #     filter_response(resp)

    #     return resp

if __name__ == '__main__' :
    reqQ = Queue.Queue(3);
    resQ = Queue.Queue(3);
    text = input("Enter message for message Handler Class:\n> ")
    rInput = [{'text': text, 'user': 'U9H1FCNG4', 'team': 'T9GMMDTPG', 'channel': 'D9GCAPGNL', 'bot_id': 'B9H5NKUHK', 'ts': '1524798523.000234', 'type': 'message', 'event_ts': '1524798523.000234'}]
    mh = MessageHandler(reqQ, resQ, "R2D2");
    mh.handle(rInput);


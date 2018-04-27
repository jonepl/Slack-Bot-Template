import random
try :
    import Queue
except:
    import queue as Queue

# Sentences we'll respond with if the user greeted us
GREETING_KEYWORDS = ("hello", "hi", "greetings", "sup", "what's up",)

GREETING_RESPONSES = ["Sup bro", "Hey", "*nods*", "What up homie?"]

class MessageHandler(object):
    
    def __init__(self, responseQueue, botID, directMessaged) :
        self.botID = botID;
        self.directMessaged = directMessaged;
        self.responseQueue = responseQueue;

    def start(self, rawInput) :
        result = self.parse(rawInput);
        return result;

    # Parses all raw input
    ### Assumptions: All rawInput sent to this message should be of type Array and not empty
    def parse(self, rawInput):
        response = None
        if (not self.isEmpty(rawInput)) :
            # Handles message
            if(self.isMessage(rawInput) and self.notSelf(rawInput)) :
                response = self.parseMessage(rawInput);
                self.responseQueue.put(response);
                return response;
            else :
                print("Something went wrong");
                print(rawInput);
                return response;
    
    # Parses the raw slack input
    def parseMessage(self, rawInput) :

        responseObject = {};
        user = rawInput[0]['user'];
        message = rawInput[0]['text'];
        channel = rawInput[0]['channel'];

        self.determineAction(message, responseObject);

        # Bot has been mentioned in a chat or direct messaged
        if(self.botMentioned or self.directMessaged) :
            responseObject["user"] = str(user);
            responseObject['message'] = str(self.stripTag(message));
            responseObject['channel'] = str(channel);
            return responseObject;
        else :
            return {}

    # Determine what action to take depending on the message
    def determineAction(self, message, responseObject) :
        if('Hey' in message) :
            responseObject['action'] = "writeToSlack";

    # Determines if the bot is mentioned in the raw input
    def botMentioned(self, rawInput) :
        if(self.botID in rawInput[0]['text']) : return True;
        else : return False;

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
    def isMessage(self, rawInput) :
        if(rawInput[0].get('type') == 'message') : return True;
        else : return False;
    
    # def respond(self, userInput) :

    #     for word in userInput.split():
    #         if word.lower() in GREETING_KEYWORDS:
    #             return random.choice(GREETING_RESPONSES)

    #         if word.lower() in FILE_WORDS :
    #             pass;

    # def filter_response(self, response):
    #     """Don't allow any words to match our filter list"""
    #     tokenized = response.split(' ')
    #     for word in tokenized:
    #         if '@' in word or '#' in word or '!' in word:
    #             raise UnacceptableUtteranceException()
    #         for s in FILTER_WORDS:
    #             if word.lower().startswith(s):
    #                 raise UnacceptableUtteranceException()   

        # cleaned = preprocess_text(sentence)
        # parsed = TextBlob(cleaned)

        # pronoun, noun, adjective, verb = find_candidate_parts_of_speech(parsed)

        # resp = check_for_comment_about_bot(pronoun, noun, adjective)
        
        # if not resp:
            # resp = check_for_greeting(parsed)

        # if not resp :
            # resp = random.choice(NONE_RESPONSES)
        # elif pronoun == 'I' and not verb :
            # resp = random.choice(COMMENTS_ABOUT_SELF)
        # else:
            # resp = construct_response(pronoun, noun, verb)
        
        # if not resp:
            # resp = random.choice(NONE_RESPONSES)

        # logger.info("Returning phrase '%s'", resp)

        # filter_response(resp)

        # return resp

    


    

if __name__ == '__main__' :
    rq = Queue.Queue(3);
    print(rq.qsize());
    mh = MessageHandler(rq,"R2D2", True);
    response = mh.parse([{'text': 'Hey welcome-bot', 'user': 'U9H1FCNG4', 'team': 'T9GMMDTPG', 'channel': 'D9GCAPGNL', 'bot_id': 'B9H5NKUHK', 'ts': '1524798523.000234', 'type': 'message', 'event_ts': '1524798523.000234'}]);
    print(rq.get());
    print(rq.qsize());
    print(response);


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

if not __name__ == '__main__':
    from app.ServiceHandler import ServiceHandler

# Sentences we'll respond with if the user greeted us
SUCCESS = 0;
FAILURE = -1;
GREETING_KEYWORDS = ["hey", "hi", "greetings", "sup", "hello"]
SERVICE_KEYWORDS = ["give", "file", "service"]
GREETING_RESPONSES = ["Sup bro.", "Hey.", "What it do!", "What up homie?", "Howdy."]
SERVICES_TYPES = [{"tempservice" : "hello_world"}, { "file" : "file_service"}]

class MessageHandler(Thread):
    
    def __init__(self, requestQueue, responseQueue, botID) :
        Thread.__init__(self)
        self.running = True;
        self.requestQueue = requestQueue;
        self.responseQueue = responseQueue;
        self.serviceRequestQueue = Queue.Queue()
        self.serviceResponseQueue = Queue.Queue()
        self.serviceHandler = None
        self.botID = botID

    # Entry point for thread
    def run(self) :
        
        self.setUpThreads()
        # TODO: Figure out multi-threaded solution
        while(self.running) :
            try :
                if(self.requestQueue.qsize() > 0) : 
                    rawInput = self.requestQueue.get()
                    self.handle(rawInput)

                elif(self.serviceResponseQueue.qsize() > 0) :
                    response = self.serviceResponseQueue.get()
                    self.responseQueue.put(response)
            
            except(KeyboardInterrupt, SystemError) :
                print("\n~~~~~~~~~~~ MessageHandler KeyboardInterrupt Exception Found~~~~~~~~~~~\n");
                self.ServiceHandler.kill();
                self.running = False;


    def setUpThreads(self) :
        self.serviceHandler = ServiceHandler(self.serviceRequestQueue, self.serviceResponseQueue);
        self.serviceHandler.setName("Messaging Thread 1");
        self.serviceHandler.daemon = True;
        self.serviceHandler.start();

    # Parses all raw input from Slack
    def handle(self, rawInput):
        
        response = None
        if (not self.isEmpty(rawInput)) :
            if(self.isAValidMessage(rawInput)) :
                response = self.parseInput(rawInput);
                # DEBUG print(response)
                self.responseQueue.put(response);
                # DEBUG print("Completed SUCCESS");

            else :
                print("Error: Invalid non-empty message received.");
    
    # Kills Thread run method
    def kill(self) :
        self.running = False;

    # Parses the raw slack input into parts
    def parseInput(self, rawInput) :

        user = rawInput[0]['user']
        message = rawInput[0]['text']
        channel = rawInput[0]['channel']

        # Muscle logic 
        action, response = self.determineAction(str(user), str(self.stripTag(message)), str(channel))
        responseObject = self.generateMessageResponse(user, message, channel, action, response);

        return responseObject;

    # Determine what action to take depending on the message
    def determineAction(self, userID, message, channel) :
        
        if(self.isGreeting(message)) :
            return ("writeToSlack", random.choice(GREETING_RESPONSES))

        elif(self.isServiceRequest(message)) :
            # TODO: Determine if the two methods should be combined into one
            # TODO: Improve to handle all types of services

            serviceName = self.determineService(message)
            scheduleAction, scheduleType, frequency, interval = self.determineSchedule(message);

            if(serviceName is not None) :
                serviceRequest = self.createServiceRequest(scheduleAction, userID, channel, serviceName, scheduleType, frequency, interval)
                self.serviceRequestQueue.put(serviceRequest)
                return ("writeToSlack", "Working on processing Service for message: " + self.stripTag(message) + " ...");
            else :
                return ("writeToSlack", "Sorry I wasn't able to find a service for message: " + self.stripTag(message) + " ...");

        else :
            return ("writeToSlack", "Im not sure how to decipher \"" + self.stripTag(message) + "\".")

    def generateMessageResponse(self, user, message, channel, action=None, response=None) :
        
        responseObject = {};
        responseObject["user"] = str(user);
        responseObject['message'] = str(self.stripTag(message));
        responseObject['channel'] = str(channel);
        responseObject['action'] = action;
        responseObject['response'] = response

        return responseObject

    def determineSchedule(self, message) :
        #TODO Figure out a way to parse user messages to determine action, scheduleType, frequency, and interval
        return ('add', 'intra-day', 'seconds', 30)

    def createServiceRequest(self, scheduleAction, userId, channel, service, scheduleType, frequency, interval, time = None, day = None ) :
        serviceRequest = {
            'messageInfo' : { 
                'action': None,
                'responseType' : None,      # Text of file
                'slackUserId' : userId,
                'channel' : channel,
                'response' : None
            },
            'scheduleJob' : {
                'action' : scheduleAction,
                'type' : scheduleType,
                'serviceName' : service, # Hello World
                'serviceTag' : None,
                'frequency' : frequency,
                'interval' : interval,
                'time' : time,
                'day' : day   
            }
        }

        return serviceRequest

    #FIXME: make this dynamic
    def determineService(self, message) :
        
        result = None
        # FIXME Determine better way to parse user input and send appropriate service
        for service in SERVICES_TYPES :
            for key, value in service.items():
                if(key in message.lower()) :
                    result = value
                    break

        return result

    def getEmptyJobRequest(self) :
        return {
            'action' : None,
            'job' : { 
                'slackUserId' : None,
                'channel' : None,
                'service' : None,
                'schedule' : {
                    'type' : None,
                    'frequency' : None,
                    'interval' : None,
                    'time' : None,
                    'day' : None   
                }
            }
        }

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
    def isAValidMessage(self, rawInput) :
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


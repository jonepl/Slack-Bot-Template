'''
File: MessageHandler.py
Description: Handles raw input and determines an appropriate response to send back to the user
'''
import random
import logging
from threading import Thread
try :
    import Queue
except:
    import queue as Queue

from SubscriptionHandler import SubscriptionHandler
from ServiceManager import ServiceManager

# if not __name__ == '__main__':
#     from app.SubscriptionHandler import SubscriptionHandler
#     import app.ServiceManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s : %(name)s : %(message)s')

file_handler = logging.FileHandler('logs/MessageHandler.log')
stream_handler = logging.StreamHandler()

file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

GREETING_KEYWORDS = ["hey", "hi", "greetings", "sup", "hello"]
SERVICE_KEYWORDS = ["give", "file", "service", "subscribe"]
GREETING_RESPONSES = ["Sup bro.", "Hey.", "What it do!", "What up homie?", "Howdy."]
SERVICES_TYPES = [{"tempservice" : "hello_world"}, { "file" : "file_service"}]

class MessageHandler(Thread):
    
    def __init__(self, requestQueue, responseQueue, botID, debug=False) :
        Thread.__init__(self)
        self.messageRequestQueue = requestQueue
        self.messageResponseQueue = responseQueue
        self.serviceRequestQueue = Queue.Queue()
        self.serviceResponseQueue = Queue.Queue()
        self.subscriptionHandler = None
        self.botID = botID
        self.debug = debug
        self.serviceManager = ServiceManager()
        if(self.debug) : logger.debug('MessageHandler successfully created')

    # Entry point for thread
    def run(self) :
        self.running = True
        self.setUpThreads()
        # TODO: Figure out multi-threaded solution
        while(self.running) :
            try :
                if(self.messageRequestQueue.qsize() > 0) : 
                    message = self.messageRequestQueue.get()
                    if(self.debug) : logger.debug("Message requested received from Bot {}".format(str(message)))
                    self.handle(message)

                elif(self.serviceResponseQueue.qsize() > 0) :
                    response = self.serviceResponseQueue.get()
                    if(self.debug) : logger.debug("Message response received from SubscriptionHandler {}".format(str(response)))
                    self.messageResponseQueue.put(response)
            
            except(KeyboardInterrupt, SystemError) :
                if(self.debug) : logger.debug("\n~~~~~~~~~~~ MessageHandler KeyboardInterrupt Exception Found~~~~~~~~~~~\n")
                self.subscriptionHandler.kill()
                self.running = False


    def setUpThreads(self) :
        self.subscriptionHandler = SubscriptionHandler(self.serviceRequestQueue, self.serviceResponseQueue, self.debug)
        self.subscriptionHandler.setName("SubscriptionHandler Thread 1")
        self.subscriptionHandler.daemon = True
        self.subscriptionHandler.start()
        if(self.debug) : logger.info("Started thread: {}".format("SubscriptionHandler Thread 1"))

    # Parses all raw input from Slack
    def handle(self, rawInput):
        
        response = None
        if (not self.isEmpty(rawInput)) :
            if(self.isAValidMessage(rawInput) or not self.isTyping(rawInput)) :

                response = self.parseInput(rawInput)
                if(self.debug) : logger.debug("Handling valid message: {}".format(response))
                if(response != None) :
                    self.messageResponseQueue.put(response)

            else :
                if(self.debug) : logger.error("Invalid non-empty message received: {}".format(rawInput))
    
    # Kills Thread run method
    def kill(self) :
        self.running = False
        if(self.debug) : logger.info("Terminating MessageHandler")

    # Parses the raw slack input into parts
    def parseInput(self, rawInput) :

        if('user' in rawInput[0] and 'text' in rawInput[0] and 'channel' in rawInput[0]) :
            user = rawInput[0]['user']
            message = rawInput[0]['text']
            channel = rawInput[0]['channel']

            # Muscle logic 
            action, response = self.determineAction(rawInput[0])
            responseObject = self.generateMessageResponse(user, message, channel, action, response)

            return responseObject
        else :
            logger.warning("rawInput not valid. Modify handle criterion. {}".format(str(rawInput[0])))
            return None

    # Determine what action to take depending on the message
    def determineAction(self, rawInput) :

        userID = rawInput['user']
        message = rawInput['text']
        channel = rawInput['channel']
        userId = rawInput['user']

        if(self.isGreeting(message)) :
            if(self.debug) : logger.debug("Greeting found return random choice")
            return ("writeToSlack", random.choice(GREETING_RESPONSES))

        elif(self.isServiceListRequest(message)) :
            serviceList = self.serviceManager.getServicesNames()
            response = "Available Services\n"
            for index, service in enumerate(serviceList) :
                response += "\t{}. {}\n".format(index+1, service)
            
            if(self.debug) : logger.debug("Service List Request found {}".format(response))

            return ("writeToSlack", response)

        elif(self.isListAvailableServicesRequest(message)) :

            myServices = self.subscriptionHandler.getServicesListForUsersId(userId)
            response = None
            if(len(myServices) == 0) :
                response = "You are not subscribed to any services."
            else :
                response = "You are currently Subscribed to:\n"
                for index, myService in enumerate(myServices) :
                    response += "\t{}. {}\n".format(index+1, myService)

            return("writeToSlack", response)


        elif(self.isServiceRequest(message)) :
            # TODO: Determine if the two methods should be combined into one
            # TODO: Improve to handle all types of services
            
            serviceName = self.extractServiceName(message)

            if(self.serviceManager.isRunnableService(serviceName)) :
                    
                scheduleAction, scheduleType, frequency, interval = self.determineSchedule(message)

                if(self.debug) : logger.debug("Service Request for serviceName: {} scheduleAction: {}, scheduleType: {}, frequency: {}, interval {}".format(serviceName, scheduleAction, scheduleType, frequency, interval))

                if(serviceName is not None) :
                    serviceRequest = self.createServiceRequest(scheduleAction, userID, channel, serviceName, scheduleType, frequency, interval)
                    self.serviceRequestQueue.put(serviceRequest)
                    return ("writeToSlack", "Working on processing Service for message: " + self.stripTag(message) + " ...")
                else :
                    return ("writeToSlack", "Sorry I wasn't able to find a service for message: " + self.stripTag(message) + " ...")
            else :
                return ("writeToSlack", "Unable to retrieve requested service from message {}.".format(message))
        else :
            return ("writeToSlack", "Im not sure how to decipher \"" + self.stripTag(message) + "\".")

    def generateMessageResponse(self, user, message, channel, action=None, response=None) :
        
        responseObject = {}
        responseObject["user"] = str(user)
        responseObject['message'] = str(self.stripTag(message))
        responseObject['channel'] = str(channel)
        responseObject['action'] = action
        responseObject['response'] = response

        if(self.debug) : logger.debug("Generating responseObject: {}".format(str(responseObject)))
        return responseObject

    # FIXME Determine better way to parse user input and send appropriate service
    def determineSchedule(self, message) :
        
        result = None
        serviceNames = self.serviceManager.getServicesNames()
        for serviceName in serviceNames :

                if(serviceName.lower() in message.lower()) :
                    if("new" in message.lower()) :
                        result = "add"
                    elif("remove" in message.lower()) :
                        result = "remove"
                    elif("update" in message.lower()) :
                        result = "update"
                    break

        #TODO Figure out a way to parse user messages to determine action, scheduleType, frequency, and interval
        if(result == "update") :
            return (result, 'intra-day', 'minutes', 1)
        return (result, 'intra-day', 'seconds', 30)

    def createServiceRequest(self, scheduleAction, userId, channel, service, scheduleType, frequency, interval, time = None, day = None ) :

        if(self.debug) : logger.debug("Create service request with scheduleAction {} userId {} channel {} service {} schedultType {} frequency {} interval {}time {}  day {}".format(scheduleAction, userId, channel, service, scheduleType, frequency, interval, time, day))

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

        if(self.debug) : logger.info("Created ServiceRequest {}".format(serviceRequest))

        return serviceRequest

    # FIXME Determine better way to parse user input and send appropriate service
    def extractServiceName(self, message) :
        
        result = None
        serviceNameList = self.serviceManager.getServicesNames()

        for serviceName in serviceNameList :
            if( serviceName.lower() in message.lower() ) :
                result = serviceName
                break

        return result

    # Determines if a message contains a greeting word
    def isGreeting(self, message) :
        for greeting in GREETING_KEYWORDS :
            if(greeting in message.lower()) :
                return True
        return False

    # #TODO: Improve this
    def isServiceListRequest(self, message) :
        if('list' in message.lower() and 'services' in message.lower()) : return True
        else : return False

    def isListAvailableServicesRequest(self, message) :
        if('my' in message.lower() and 'services' in message.lower()) : return True
        else : return False
    

    # TODO Implement to interact Service Manager
    def isServiceRequest(self, message) :
        for command in SERVICE_KEYWORDS :
            if(command in message.lower()) :
                return True
        return False

    # Removes the Slack bot ID from a message
    def stripTag(self, message) :
        botTag = "<@" + self.botID + ">"

        return message.replace(botTag, '').rstrip()

    # Determines if the raw input was sent by this bot
    def notSelf(self, rawInput) :
        if(rawInput[0].get('user') == self.botID) : return False
        else : return True 
    
    # Detect if a users is typing
    def isTyping(self, rawInput) :
        if(rawInput[0].get('type') == 'user_typing') : return True
        else : return False

    # Detects if raw input is Empty
    def isEmpty(self, rawInput) :
        if not rawInput : return True
        else : return False

    # Detects if the raw input is a message
    def isAValidMessage(self, rawInput) :
        if(rawInput[0].get('type') == 'message') : return True
        else : return False

    # Determines if the bot is mentioned in the raw input
    def botMentioned(self, rawInput) :
        if('text' in rawInput[0]) :
            if(self.botID in rawInput[0]['text']) : return True
        else : return False
    

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
    reqQ = Queue.Queue(3)
    resQ = Queue.Queue(3)
    text = input("Enter message for message Handler Class:\n> ")
    rInput = [{'text': text, 'user': 'U9H1FCNG4', 'team': 'T9GMMDTPG', 'channel': 'D9GCAPGNL', 'bot_id': 'B9H5NKUHK', 'ts': '1524798523.000234', 'type': 'message', 'event_ts': '1524798523.000234'}]
    mh = MessageHandler(reqQ, resQ, "R2D2")
    mh.handle(rInput)


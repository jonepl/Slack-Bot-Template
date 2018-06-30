'''
File: SubscriptionHandler.py
Description: A thread class responsible for handling the users subscriptions to services

'''

from threading import Thread

import os, time, sys, pymongo, subprocess, schedule, logging, json

import creds as config

try :
    import Queue
except:
    import queue as Queue

from ServiceManager import ServiceManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s : %(name)s : %(message)s')

file_handler = logging.FileHandler('logs/SubscriptionHandler.log')
stream_handler = logging.StreamHandler()

file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

SERVICE_FUNCTION = {}

class SubscriptionHandler(Thread) :

    def __init__(self, serviceRequestQueue, serviceResponseQueue, debug=False) :
        Thread.__init__(self)
        # Set up Mongo DB
        client = pymongo.MongoClient( config.slack['mongoDB']['uri'] )
        db = client[ config.slack['mongoDB']['dbName'] ]
        self.collection = db[ config.slack['mongoDB']['collectionName'] ]

        self.running = True
        self.debug = debug
        self.serviceRequestQueue = serviceRequestQueue
        self.serviceResponseQueue = serviceResponseQueue
        self.serviceManager = ServiceManager()
        self.serviceFunctions = self.setUpServiceFunctions()
        self.usersSubscriptions = {} # Determine which users have access to which services 
        if(self.debug) : logger.debug('SubscriptionHandler successfully created')

    # Entry point for thread
    def run(self) :

        self.loadScheduledJobs()
        
        while (self.running) :
            try:

                schedule.run_pending()
                self.checkJobQueue()
            except(KeyboardInterrupt, SystemError) :
                print("\n~~~~~~~~~~~ SubscriptionHandler KeyboardInterrupt Exception Found~~~~~~~~~~~\n")
                self.running = False

    # Checks for updates of jobs
    def checkJobQueue(self) :
        
        if(not self.serviceRequestQueue.empty()) :
            
            request = self.serviceRequestQueue.get()
            self.serviceRequestQueue.task_done()

            serviceName = request['scheduleJob']['serviceName']
            tag = self.produceTag(request)

            if(self.debug) : logger.info("SubscriptionHandler request found {}".format(request))

            if(request['scheduleJob']['action'] == 'add') :

                scheduleSuccessful = self.scheduleJob(request)
                dbSaveSuccessful = self.saveJob(request)

                if(scheduleSuccessful and dbSaveSuccessful) :

                    self.addUserToSubscription(tag)

                    response = "Successfully scheduled and saved {} service request of type {} every {} {}.".format(serviceName, request['scheduleJob']['type'], str(request['scheduleJob']['interval']), request['scheduleJob']['frequency'] )
                    slackResponse = self.generateSlackResponse(request['messageInfo']['slackUserId'], 
                                        request['messageInfo']['channel'], 
                                        response)

                    self.serviceResponseQueue.put(slackResponse)

                else :
                    print(request)
                    response = "Unable to subscribe you to {} because you are already subscribe to this serivce.".format(serviceName)

                    slackResponse = self.generateSlackResponse( request['messageInfo']['slackUserId'], 
                                        request['messageInfo']['channel'],
                                        response)

                    self.serviceResponseQueue.put(slackResponse)

            elif(request['scheduleJob']['action'] == 'remove') :

                unscheduleSuccessful = self.unscheduleJob(request)
                dbRemoveSuccessful = self.deleteJob(request)

                if(unscheduleSuccessful and dbRemoveSuccessful) :
                    
                    response = "Successfully unscheduled and removed {} service request of type {} every {} {}.".format(request['scheduleJob']['serviceName'], request['scheduleJob']['type'], str(request['scheduleJob']['interval']), request['scheduleJob']['frequency'] )
                    slackResponse = self.generateSlackResponse(request['messageInfo']['slackUserId'], 
                                                               request['messageInfo']['channel'], 
                                                               response)

                    self.serviceResponseQueue.put(slackResponse)
                else :

                    response = "Unable to unsubscribe you from {} because you are no longer subscribe to this serivce.".format(serviceName)
                    slackResponse = self.generateSlackResponse(request['messageInfo']['slackUserId'], 
                                        request['messageInfo']['channel'], 
                                        response)

                    self.serviceResponseQueue.put(slackResponse)
            
            elif(request['scheduleJob']['action'] == 'update') :
                pass
                # self.updateSchedule(request['job'])
                # self.updateJob(request['job'])
                
            else :
                print("Unknown action for Service request.")

    # Adds to reoccuring job to DB
    def saveJob(self, request):
        #FIXME: Use Mongo Schema to prevent ulgy jobs entrying db
        userId = request['messageInfo']['slackUserId']
        service = request['scheduleJob']['serviceName']

        # tag = self.produceTag(userId, service)
        tag = self.produceTag(request)

        if(not self.subscriptionExists(tag)) :
            request['scheduleJob']['serviceTag'] = tag
            dbResult = self.collection.insert_one(request)
            result = dbResult.acknowledged
        else :
            print("User id {} is already subscribed to service {}".format(userId, service))

            result = False

        return result
    
    # Removes reoccuring job to DB
    def deleteJob(self, request) :

        tag = self.produceTag(request)

        if(self.subscriptionExists(tag)) :

            query = { "scheduleJob.serviceTag" : tag }
            dbStat = self.collection.remove(query)
            
            if(dbStat.nRemoved <= 0) : 
                print("ERROR removing document with tag {}.")
                return False
                
            else :
                print("Mongdo DB document for tag {} has been properly removed.")
                return True
        else :
            print("Unable to removed tag because it does not exist")
            return False

    # Adds a job to Scheduler
    def scheduleJob(self, request) :

        status = True      
        tag = self.produceTag(request)
        serviceName = request['scheduleJob']['serviceName']

        if( not self.subscriptionExists(tag) ) :
              
            if(self.debug) : logger.debug("Scheduling Job ...\n{}".format(request))

            if(self.isIntraDay(request)) :
                status = self.scheduleIntraDayJob(request)
                
            elif(self.isIntraMonth(request)) :
                status = self.scheduleIntraMonthJob(request)

            elif(self.isIntraYear(request)) :
                pass
                # Not Implemented
                # status = self.scheduleIntraYearJob(request)

            else :
                if(self.debug) : logger.error("Unable to schedule Job")
                status = False

        else :
            print("You are already Subscribe to {} service".format(serviceName))
            status = False
        return status

    # Removes schedule jobs from schedule
    def unscheduleJob(self, job) :

        status = True

        if(self.debug) : logger.debug("Unscheduling Job ...")

        tag = job['messageInfo']['slackUserId'] + "_" + job['scheduleJob']['serviceName']
        
        # : Figure out if a status can be evaluated
        schedule.clear(tag)

        return status
    
    # Unschedules a list of users from scheduler
    def unscheduledJobByTag(self, userIds, service) :

        for userId in userIds :
            tag = userId + "_" + service
            # FIXME: Status of removal?
            schedule.clear(tag)

    # Loads all jobs from DB into scheduler
    def loadScheduledJobs(self):

        jobs = self.collection.find( {} )
        if(self.debug) : logger.debug("Found {} logs in db".format(str(jobs)))
        for job in jobs :
            self.addUserToSubscription(self.extractTag(job))
            self.scheduleJob(job)
    
    # loads a tag into local subscription record
    def loadSubscriptions(self, tag) :

        userId, service = tag.split("_")

        if(userId in self.usersSubscriptions) :
            if( not (service in self.usersSubscriptions[userId]) ) :
                self.usersSubscriptions[userId].append(service)
        else :
            self.usersSubscriptions[userId] = [service]

    # Helper method: Adds a new intra-day schedule job
    def scheduleIntraDayJob(self, request) :
        
        status = True
        serviceName = request['scheduleJob']['serviceName']
        func = self.serviceFunctions[serviceName]
        frequency = request['scheduleJob']['frequency']
        interval = request['scheduleJob']['interval']

        args = {}

        args['service'] = self.serviceManager.getServiceDetails(serviceName)
        args['messageInfo'] = request['messageInfo']
        args['scheduleJob'] = request['scheduleJob']

        # NOTE: When would args be None?
        if( args is not None ) :
            #TODO: remove set value from messagehandler and determine serivceName within this file
            tag = request['messageInfo']['slackUserId'] + "_" + request['scheduleJob']['serviceName']

            if frequency == 'minutes':
                schedule.every(interval).minutes.do(func, args).tag(tag)

            elif frequency == 'seconds' :
                schedule.every(interval).seconds.do(func, args).tag(tag)

            elif frequency == 'hours' :
                schedule.every(interval).hours.do(func, args).tag(tag)

            else :
                print("ERROR OCCURRED")
                status = False
        else :
            print("Error Occurred while searching for ServiceDetails")
            status = False

        return status

    # Helper method: Adds a new intra month schedule job
    def scheduleIntraMonthJob(self, job) :
        pass

    # Helper method: Adds a new intra year schedule job
    def scheduleIntraYearJob(self, job) :
        pass

    # Assigns a runnable function to each of the services in the service config
    def setUpServiceFunctions(self) :
        
        serviceFunc = {}

        services = self.serviceManager.getAllServicesDetails()
        
        for service in services :
            serviceName = service['name']
            location = service['path']

            if(location.lower() == "internal") :
                methodName = service['entrypoint']
                function = self.getFunction(methodName)
                if(function is not None) :
                    serviceFunc[serviceName] = function
            else :

                serviceFunc[serviceName] = self.runExternalService

        if(self.debug) : logger.info("Setup Function list as {}".format(serviceFunc))

        return serviceFunc

    # Returns a function for a give serviceName
    def getFunction(self, methodName) :
        if(callable(getattr(self, methodName))) :
            return getattr(self, methodName)
        else :
            return None

    # Determines if there is a user subscription that exists for a given tag
    def subscriptionExists(self, tag) :

        userId, service = tag.split("_")

        if(userId in self.usersSubscriptions) : 
            if(service in self.usersSubscriptions[userId]) :
                return True
        else : return False

    # Adds a user to the local user subscription list
    def addUserToSubscription(self, tag) :

        userId, service = tag.split("_")

        if(self.debug) : logger.debug("service: {} userId: {} userSubscriptions: {}".format(service, userId, self.usersSubscriptions))

        if(userId in self.usersSubscriptions) :

            self.usersSubscriptions[userId].append(service)
            if(self.debug) : logger.debug("Added additional service to {}.".format(userId))
        else :
            self.usersSubscriptions[userId] = []
            if(self.debug) : logger.debug("Adding new userId to usersSubscriptions")
               
            self.usersSubscriptions[userId].append(service)
            if(self.debug) : logger.debug("Service: {} userId: {} added to userSubscriptions: {}".format(service, userId, self.usersSubscriptions))

    # Removes a user to the local user subscription list
    def removeUserFromSubscription(self, tag) :

        userId, service = tag.split("_")

        if(userId in self.usersSubscriptions) :
            
            if(service in self.usersSubscriptions[userId]) :
                self.usersSubscriptions[userId].remove(service)
            else :
                print("Tag {} does not exits. Can't remove".format(tag))

            if(not self.usersSubscriptions[userId]) :
                del self.usersSubscriptions[userId]
        else :
            print("No userId {} exists".format(userId))

    # 
    def getUserIdsForServiceName(self, serviceName) :
        
        result = []

        for userId, serviceNames in enumerate(self.usersSubscriptions) :
            if(serviceName in serviceNames) :
                result.append(userId)

        return result
            
    def getServicesListForUsersId(self, userId) :

        if(userId in self.usersSubscriptions) :
            return self.usersSubscriptions[userId]
        else :
            return []

    def runExternalService(self, args) :

        cmd = args['service']['language']
        filepath = args['service']['path'] + "/"+ args['service']['entrypoint']

        serviceName = args['scheduleJob']['serviceName']
        
        output = subprocess.check_output([cmd, filepath])
        response = self.serviceManager.generateSlackResponseOutput(output, args['messageInfo'])
        
        if(response is not None) :
            if(self.debug) : logger.info("Returning response up to MessageHandler: {}".format(response))
            self.serviceResponseQueue.put(response)
        else :
            print("The external service {} fail. Disable this service".format(serviceName))
            self.serviceManager.makeUnrunnableService(serviceName)
            userIds = self.getUserIdsForServiceName(serviceName)
            self.unscheduledJobByTag(userIds, serviceName)

    # Terminates thread loop
    def kill(self) :
        self.running = False

    # Produces an job identifier
    def produceTag(self, request) :
        return request['messageInfo']['slackUserId'] + "_" + request['scheduleJob']['serviceName']

    #FIXME: Redundant method
    def extractTag(self, job) :
        return  job['scheduleJob']['serviceTag']

    # Determine if job is an intra day
    def isIntraDay(self, request) :
        if(request['scheduleJob']['type'] == 'intra-day') : return True
        else : return False

    # Determine if job is an intra month
    def isIntraMonth(self, request) :
        if(request['scheduleJob']['type'] == 'intra-month') : return True
        else : return False

    # Determine if job is an intra year
    def isIntraYear(self, request) :
        if(request['scheduleJob']['type'] == 'intra-year') : return True
        else : return False

    # Text based job
    def helloJob(self, messageInfo) :
        response = 'Hello World Fool!'

        self.generateSlackResponse(messageInfo['slackUserId'],
        messageInfo['channel'], response)

        self.serviceResponseQueue.put(messageInfo)  

    # File based job
    def fileJob(self, messageInfo) :

        messageInfo['action'] = 'writeToFile'
        messageInfo['responseType'] = 'file'
        messageInfo['response'] = './extras/images/slackdroid.png'

        self.serviceResponseQueue.put(messageInfo)  

    def generateSlackResponse(self, slackUserId, channel, response) :
        messageInfo = {}

        messageInfo['action'] = "writeToSlack"
        messageInfo['responseType'] = "text"
        messageInfo['slackUserId'] = slackUserId
        messageInfo['channel'] = channel
        messageInfo['response'] = response

        return messageInfo
    

if __name__ == '__main__':
    request = {
            'messageInfo' : { 
                'ResponseType' : None,      # text or file
                'slackUserId' : 'UGEI4KLP',
                'channel' : 'DJH39HGL',
                'response' : None           # message or filepath
            },
            'scheduleJob' : {
                'action' : 'add',
                'type' : 'intra-day',
                'serviceName' : 'Interal Service',  # determined in MessageHandler for now
                'frequency' : 'seconds',
                'interval' : 30,
                'time' : None,
                'day' : None   
            }
        }
    serviceRequestQueue = Queue.Queue()
    serviceRequestQueue.put(request)
    scheduler = SubscriptionHandler(serviceRequestQueue, Queue.Queue())
    
    # while True:
    #     schedule.run_pending()
    #     time.sleep(0.5)
    # scheduler.run()

    #scheduler.setUpServiceFunction()
    scheduler.runExternalService(    {
        'name' : 'Picture Service',
        'path' : 'services/scripts/FileService',
        'language' : 'python3',
        'entrypoint' : 'pictureService.py',
        'runnable' : True
    }) 
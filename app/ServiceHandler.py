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

file_handler = logging.FileHandler('logs/ServiceHandler.log')
stream_handler = logging.StreamHandler()

file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)

stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

SERVICE_FUNCTION = {}

class ServiceHandler(Thread) :

    def __init__(self, serviceRequestQueue, serviceResponseQueue, debug=False) :
        Thread.__init__(self)
        client = pymongo.MongoClient( config.slack['mongoDB']['uri'] )
        db = client[ config.slack['mongoDB']['dbName'] ]
        self.collection = db[ config.slack['mongoDB']['collectionName'] ]
        self.running = True
        self.debug = debug
        self.serviceRequestQueue = serviceRequestQueue
        self.serviceResponseQueue = serviceResponseQueue
        self.serviceManager = ServiceManager()
        self.serviceFunctions = self.setUpServiceFunctions()
        if(self.debug) : logger.debug('ServiceHandler successfully created')

    # Entry point for thread
    def run(self) :

        self.loadScheduledJobs()
        
        while (self.running) :
            try:

                schedule.run_pending()
                self.checkJobQueue() 
            except(KeyboardInterrupt, SystemError) :
                print("\n~~~~~~~~~~~ ServiceHandler KeyboardInterrupt Exception Found~~~~~~~~~~~\n")
                self.running = False

    # Checks for updates of jobs
    def checkJobQueue(self) :
        
        if(not self.serviceRequestQueue.empty()) :
            
            request = self.serviceRequestQueue.get()
            self.serviceRequestQueue.task_done()
            
            if(self.debug) : logger.info("ServiceHandler request found {}".format(request))

            if(request['scheduleJob']['action'] == 'add') :

                scheduleStatus = self.scheduleJob(request)
                self.saveJob(request)

                # TODO: Find beter way to confirm that the service was accepted
                if(scheduleStatus == 0) :
                    message = request
                    message['messageInfo']['action'] = 'writeToSlack'
                    message['messageInfo']['responseType'] = 'text'
                    message['messageInfo']['response'] = "Successfully scheduled and saved {} service request of type {} every {} {}.".format(message['scheduleJob']['serviceName'], message['scheduleJob']['type'], str(message['scheduleJob']['interval']), message['scheduleJob']['frequency'] )
                    self.serviceResponseQueue.put(message['messageInfo'])
                

            elif(request['scheduleJob']['action'] == 'remove') :

                scheduleStatus = self.unscheduleJob(request)
                self.deleteJob(request)

                if(scheduleStatus == 0) :
                    message = request
                    message['messageInfo']['action'] = 'writeToSlack'
                    message['messageInfo']['responseType'] = 'text'
                    message['messageInfo']['response'] = "Successfully unscheduled and removed {} service request of type {} every {} {}.".format(message['scheduleJob']['serviceName'], message['scheduleJob']['type'], str(message['scheduleJob']['interval']), message['scheduleJob']['frequency'] )
                    self.serviceResponseQueue.put(message['messageInfo'])
            
            elif(request['scheduleJob']['action'] == 'update') :
                pass
                # self.updateSchedule(request['job'])
                # self.updateJob(request['job'])
                
            else :
                print("Unknown action for Service request.")

    # Adds to reoccuring job to DB
    def saveJob(self, request):
        #FIXME: Use Mongo Schema to prevent ulgy jobs entrying db
        request['scheduleJob']['serviceTag'] = self.produceTag(request)
        result = self.collection.insert(request)
        print(result)
        return result
    
    # Removes reoccuring job to DB
    def deleteJob(self, request) :
        tag = self.produceTag(request)
        query = { "scheduleJob.serviceTag" : tag }
        result = self.collection.remove(query)
        print(result)
        return result

    # Produces an job identifier
    def produceTag(self, request) :
        return request['messageInfo']['slackUserId'] + "_" + request['scheduleJob']['serviceName']

    # Loads all jobs from DB into scheduler
    def loadScheduledJobs(self):

        jobs = self.collection.find( {} )

        for job in jobs :
            self.scheduleJob(job)
    
    # Adds a job to Scheduler
    def scheduleJob(self, request) :
        
        status = 0

        if(self.debug) : logger.debug("Scheduling Job ...")

        if(self.isIntraDay(request)) :
            self.scheduleIntraDayJob(request)

        elif(self.isIntraMonth(request)) :
            self.scheduleIntraMonthJob(request)

        elif(self.isIntraYear(request)) :
            pass
            # Not Implemented
            #self.scheduleIntraYearJob(request)

        else :
            if(self.debug) : logger.error("Unable to schedule Job")
            status = -1

        return status

    # Removes schedule jobs from schedule
    def unscheduleJob(self, job) :

        status = 0

        if(self.debug) : logger.debug("Unscheduling Job ...")

        tag = job['messageInfo']['slackUserId'] + "_" + job['scheduleJob']['serviceName']
        schedule.clear(tag)

        return status
        
    # Helper method: Adds a new intra-day schedule job
    def scheduleIntraDayJob(self, request) :
        
        serviceName = request['scheduleJob']['serviceName']
        func = self.serviceFunctions[serviceName]
        frequency = request['scheduleJob']['frequency']
        interval = request['scheduleJob']['interval']

        args = {}

        args['runnerInfo'] = self.serviceManager.getServiceDetails(serviceName)
        args['messageInfo'] = request['messageInfo']

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
        else :
            print("Error Occurred while searching for ServiceDetails")

    def setUpServiceFunctions(self) :
        
        serviceFunc = {}

        services = self.serviceManager.getAllServices()
        
        for service in services :
            serviceName = service['name']
            location = service['path']

            if(location.lower() == "internal") :
                methodName = service['entrypoint']
                if(self.isValidMethod(methodName)) :
                    function = self.getFunc(methodName)
                    serviceFunc[serviceName] = function
            else :

                serviceFunc[serviceName] = self.runExternalService

        if(self.debug) : logger.info("Setup Function list as {}".format(serviceFunc))

        return serviceFunc

    def runExternalService(self, args) :
        cmd = args['runnerInfo']['language']
        filepath = args['runnerInfo']['path'] + "/"+ args['runnerInfo']['entrypoint']
        
        output = subprocess.check_output([cmd, filepath])
        response = self.serviceManager.generateSlackResponse(output, args['messageInfo'])
        
        if(not response == False) :
            if(self.debug) : logger.info("Returning response up to MessageHandler: {}".format(response))
            self.serviceResponseQueue.put(response)
        else :
            print("~~~~~~~~~~~~~ Error occurred Generating Response~~~~~~~~~~~~~~~")

    # Helper method: Adds a new intra month schedule job
    def scheduleIntraMonthJob(self, job) :
        pass

    # Helper method: Adds a new intra year schedule job
    def scheduleIntraYearJob(self, job) :
        pass

    # NOTE: Probably can simple this method and the one below
    def isValidMethod(self, methodName) :
        return callable(getattr(self, methodName))

    # Possibly can be moved into ServiceManager
    def getFunc(self, methodName) :
        return getattr(self, methodName)

    # Terminates thread loop
    def kill(self) :
        self.running = False

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
        messageInfo['action'] = 'writeToSlack'
        messageInfo['responseType'] = 'text'
        messageInfo['response'] = 'Hello World Fool!'

        self.serviceResponseQueue.put(messageInfo)  

    # File based job
    def fileJob(self, messageInfo) :

        messageInfo['action'] = 'writeToFile'
        messageInfo['responseType'] = 'file'
        messageInfo['response'] = './extras/images/slackdroid.png'

        self.serviceResponseQueue.put(messageInfo)  

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
    scheduler = ServiceHandler(serviceRequestQueue, Queue.Queue())
    
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

  
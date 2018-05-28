from threading import Thread

import os
import schedule
import time
import sys
import pymongo

try :
    import Queue
except:
    import queue as Queue
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import config.creds as config

class ServiceHandler(Thread) :

    def __init__(self, serviceRequestQueue, serviceResponseQueue) :
        Thread.__init__(self)
        client = pymongo.MongoClient( config.slack['mongoDB']['uri'] )
        db = client[ config.slack['mongoDB']['dbName'] ]
        self.collection = db[ config.slack['mongoDB']['collectionName'] ]
        self.running = True
        self.serviceRequestQueue = serviceRequestQueue
        self.serviceResponseQueue = serviceResponseQueue

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

        if(self.isIntraDay(request)) :
            self.scheduleIntraDayJob(request)

        elif(self.isIntraMonth(request)) :
            self.scheduleIntraMonthJob(request)

        elif(self.isIntraYear(request)) :
            pass
            # Not Implemented
            #self.scheduleIntraYearJob(request)

        else :
            pass
        return status

    # Removes schedule jobs from schedule
    def unscheduleJob(self, job) :

        status = 0

        tag = job['messageInfo']['slackUserId'] + "_" + job['scheduleJob']['serviceName']
        schedule.clear(tag)

        return status
        
    # Helper method: Adds a new intra-day schedule job
    def scheduleIntraDayJob(self, request) :
        func = self.getServiceFunction(request['scheduleJob']['serviceName'])
        frequency = request['scheduleJob']['frequency']
        interval = request['scheduleJob']['interval']
        #TODO: remove set value from messagehandler and determine serivceName within this file
        tag = request['messageInfo']['slackUserId'] + "_" + request['scheduleJob']['serviceName']

        if frequency == 'minutes':
            schedule.every(interval).minutes.do(func, request['messageInfo']).tag(tag)

        elif frequency == 'seconds' :
            schedule.every(interval).seconds.do(func, request['messageInfo']).tag(tag)

        elif frequency == 'hours' :
            schedule.every(interval).hours.do(func, request['messageInfo']).tag(tag)

        else :
            print("ERROR OCCURRED")
    
    # FIXME: This is a quick and dirty way to get functionality
    def getServiceFunction(self, serviceName) :
        # FIXME: Need a better way to store service functionality between MessageHandler and ServiceHandler
        SERVICE_FUNC = [{"hello_world" : self.helloJob}, {"file_service" : self.fileJob}]

        result = None
        for service in SERVICE_FUNC :
            for key, value in service.items():
                if(key in serviceName.lower()) :
                    result = value
                    break
        
        return result

    # Helper method: Adds a new intra month schedule job
    def scheduleIntraMonthJob(self, job) :
        pass

    # Helper method: Adds a new intra year schedule job
    def scheduleIntraYearJob(self, job) :
        pass

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
                'action' : 'remove',
                'type' : 'intra-day',
                'serviceName' : 'hello_world',  # determined in MessageHandler for now
                'frequency' : 'minutes',
                'interval' : 30,
                'time' : None,
                'day' : None   
            }
        }
    serviceRequestQueue = Queue.Queue()
    serviceRequestQueue.put(request)
    scheduler = ServiceHandler(serviceRequestQueue, Queue.Queue())
    
    while True:
        schedule.run_pending()
        time.sleep(0.5)
    scheduler.run()
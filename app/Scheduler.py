import schedule
import pymongo
import time
try :
    import Queue
except:
    import queue as Queue

INTRA_DAY = ["seconds", "minutes", "hours"]
INTRA_MONTH = ["daily", "weekly", "bi-weekly"] 

class Scheduler :

    def __init__(self, newJobsQueue) :
        client = pymongo.MongoClient("mongodb://user1:password@ds223760.mlab.com:23760/slack-bot")
        db = client['slack-bot']
        self.collection = db['subscriptions']
        self.running = True
        self.newJobsQueue = newJobsQueue
    
    def run(self) :
        self.loadScheduledJobs()
        
        while (self.running) :
            schedule.run_pending()
            self.checkJobQueue() 
            time.sleep(0.5)

    # Checks for updates of jobs
    def checkJobQueue(self) :

        if(not self.newJobsQueue.empty) :
            request = self.newJobsQueue.get()
            self.newJobsQueue.task_done()

            if(request['action'] == 'add') :
                self.saveJob(request['job'])
                self.scheduleJob(request['job'])

            elif(request['action'] == 'remove') :
                self.deleteJob(request['job'])
                self.unscheduleJob(request['job'])
            
            else :
                print("Nothing")

    # Adds to reoccuring job to DB
    def saveJob(self, job):
        #FIXME: Use Mongo Schema to prevent ulgy jobs entrying db
        result = self.collection.insert(job)
        print(result)
        return result
    
    # Removes reoccuring job to DB
    def deleteJob(self, job) :
        
        result = self.collection.deleteOne(job)
        print(result)
        return result

    # Loads all jobs from DB into scheduler
    def loadScheduledJobs(self):

        jobs = self.collection.find( {} )

        for job in jobs :
            self.scheduleJob(job)
    
    # Adds a job to Scheduler
    def scheduleJob(self,job) :
        if(self.isIntraDay(job)) :
            self.scheduleIntraDayJob(job)

        elif(self.isIntraMonth(job)) :
            self.scheduleIntraMonthJob(job)

        else :
            pass
    
    def unscheduleJob(self, job) :
        tag = job['slackUserId'] + "_" + job['service']
        schedule.clear(tag)
        
    # Helper method: Adds a new intra-day schedule job
    def scheduleIntraDayJob(self, job) :

        frequency = job['schedule']['frequency']
        interval = job['schedule']['interval']
        tag = job['slackUserId'] + "_" + job['service']

        if frequency == 'minutes':
            schedule.every(interval).minutes.do(self.anotherJob).tag(tag)

        elif frequency == 'seconds' :
            schedule.every(interval).seconds.do(self.job).tag(tag)

        elif frequency == 'hours' :
            schedule.every(interval).hours.do(self.anotherJob).tag(tag)

        else :
            print("ERROR OCCURRED")
    
    # Helper method: Adds a new intra month schedule job
    def scheduleIntraMonthJob(self, job) :
        pass

    def kill(self) :
        self.running = False

    # Determine if job is an intra day
    def isIntraDay(self, job) :
        if(job['schedule']['type'] == 'intra-day') : return True
        else : return False

    # Determine if job is an intra day
    def isIntraMonth(self, job) :
        if(job['schedule']['type'] == 'intra-month') : return True
        else : return False

    def job(self):
        print("I'm working...") 

    def anotherJob(self) :
        print("I'm working harder ...")

    def dumbJob(self) :
        print("I'm lazy AF...")

    def update(self):
        pass
    
    def deleteAll(self):
        pass
    
if __name__ == '__main__':
    scheduler = Scheduler(Queue.Queue())
    print(schedule.jobs)
    scheduler.scheduleJob({'schedule': {'time': None, 'day': None, 'interval': 1, 'frequency': 'minutes', 'type': 'intra-day'}, 'channel': 'DJH39HGL', 'slackUserId': 'UGEI4KLP', 'service': 'Hello World'})
    scheduler.scheduleJob({'schedule': {'time': None, 'day': None, 'interval': 1, 'frequency': 'minutes', 'type': 'intra-day'}, 'channel': 'DJH39HGL', 'slackUserId': 'UGEI4KLP', 'service': 'Hello World'})
    print(schedule.jobs)
    scheduler.unscheduleJob("UGEI4KLP_Hello World")
    print(schedule.jobs)
    #scheduler.run()

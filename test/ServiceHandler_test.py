import pytest
import sys, os
try :
    import Queue
except:
    import queue as Queue 

# Adds App, Config directory to sys path for testing
path = os.path.abspath(__file__)
app = path[0:path.find("test")] + "app"
config = path[0:path.find("test")] + "config"
sys.path.append(app)
sys.path.append(config)

from ServiceHandler import ServiceHandler

serviceHandler = None
request = None

def setup_module(module):

    global serviceHandler 
    global request
    serviceHandler = ServiceHandler(Queue.Queue(), Queue.Queue())

    request = {
                'messageInfo' : { 
                    'action': "WriteToFile",
                    'responseType' : "text",
                    'slackUserId' : "someId",
                    'channel' : "someChannel",
                    'response' : "Some Response"
                },
                'scheduleJob' : {
                    'action' : None,
                    'type' : None,
                    'serviceName' : "serviceName",
                    'serviceTag' : None,
                    'frequency' : None,
                    'interval' : None,
                    'time' : None,
                    'day' : None   
                }
            }

def test_unscheduleJob() :
    
    serviceHandler.unscheduleJob(request)

    #assert(schedule.jobs == 0)

# TODO: Decouple ServiceValidatore from Config file
def test_setUpServiceFunction() :
    pass


def test_produceTag():

    expectedTag = request['messageInfo']['slackUserId'] + "_" + request['scheduleJob']['serviceName']
    tag = serviceHandler.produceTag(request)
    
    assert(tag == expectedTag)

def test_isIntraDay_happyPath() :

    request['scheduleJob']['type'] = 'intra-day'
    expectedResult = serviceHandler.isIntraDay(request)

    assert(expectedResult == True)

def test_isIntraDay_sadPath() :

    request['scheduleJob']['type'] = 'intra-hour'
    expectedResult = serviceHandler.isIntraDay(request)

    assert(expectedResult == False)

def test_isIntraMonth_happyPath() :

    request['scheduleJob']['type'] = 'intra-month'
    expectedResult = serviceHandler.isIntraMonth(request)

    assert(expectedResult == True)

def test_isIntraMonth_sadPath() :

    request['scheduleJob']['type'] = 'intra-second'
    expectedResult = serviceHandler.isIntraMonth(request)

    assert(expectedResult == False)

def test_isIntraYear_happyPath() :

    request['scheduleJob']['type'] = 'intra-year'
    expectedResult = serviceHandler.isIntraYear(request)

    assert(expectedResult == True)

def test_isIntraYear_sadPath() :

    request['scheduleJob']['type'] = 'intra-ms'
    expectedResult = serviceHandler.isIntraYear(request)

    assert(expectedResult == False)

def test_fileJob() :

    messageInfo = request['messageInfo']
    serviceHandler.fileJob(messageInfo)

    assert(serviceHandler.serviceResponseQueue.qsize() == 1)

# def test_unsceduleJob() :

#     expectedResult = serviceHandler.unsceduleJob()

#     assert(expectedResult == )
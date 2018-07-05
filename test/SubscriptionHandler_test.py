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

from SubscriptionHandler import SubscriptionHandler

subscriptionHandler = None
request = None

def setup_module(module):

    global subscriptionHandler 
    global request
    subscriptionHandler = SubscriptionHandler(Queue.Queue(), Queue.Queue())

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
    subscriptionHandler.addUserToSubscription("1UFJD2D_Intro Service")
    subscriptionHandler.addUserToSubscription("1UFJD2D_Another Service")
    subscriptionHandler.addUserToSubscription("1UFJD2D_Dumb Service")
    subscriptionHandler.addUserToSubscription("2UFJD2D_Intro Service")
    subscriptionHandler.addUserToSubscription("2UFJD2D_Crazy Service")
    subscriptionHandler.addUserToSubscription("3UFJD2D_Dumb Service")

def test_unscheduleJob() :
    
    subscriptionHandler.unscheduleJob(request)

    #assert(schedule.jobs == 0)

# TODO: Decouple ServiceValidatore from Config file
def test_setUpServiceFunction() :
    pass

def test_produceTag():

    expectedTag = request['messageInfo']['slackUserId'] + "_" + request['scheduleJob']['serviceName']
    tag = subscriptionHandler.produceTag(request)
    
    assert(tag == expectedTag)

def test_isIntraDay_happyPath() :

    request['scheduleJob']['type'] = 'intra-day'
    expectedResult = subscriptionHandler.isIntraDay(request)

    assert(expectedResult == True)

def test_isIntraDay_sadPath() :

    request['scheduleJob']['type'] = 'intra-hour'
    expectedResult = subscriptionHandler.isIntraDay(request)

    assert(expectedResult == False)

def test_isIntraMonth_happyPath() :

    request['scheduleJob']['type'] = 'intra-month'
    expectedResult = subscriptionHandler.isIntraMonth(request)

    assert(expectedResult == True)

def test_isIntraMonth_sadPath() :

    request['scheduleJob']['type'] = 'intra-second'
    expectedResult = subscriptionHandler.isIntraMonth(request)

    assert(expectedResult == False)

def test_isIntraYear_happyPath() :

    request['scheduleJob']['type'] = 'intra-year'
    expectedResult = subscriptionHandler.isIntraYear(request)

    assert(expectedResult == True)

def test_isIntraYear_sadPath() :

    request['scheduleJob']['type'] = 'intra-ms'
    expectedResult = subscriptionHandler.isIntraYear(request)

    assert(expectedResult == False)

def test_fileJob() :

    messageInfo = request['messageInfo']
    subscriptionHandler.fileJob(messageInfo)

    assert(subscriptionHandler.serviceResponseQueue.qsize() == 1)

def test_subscriptionExists_Happy() :
    
    expected = True

    result = subscriptionHandler.subscriptionExists('1UFJD2D_Intro Service')

    assert(expected == result)

def test_subscriptionExists_Sad() :
    
    expected = False

    result = subscriptionHandler.subscriptionExists('13FSUJD_Intro Service')

    assert(expected == result)

def test_addUserToSubscription_Happy() :

    userId_1 = '1UFJD2D'
    userId_2 = '2UFJD2D'
    userId_2 = '3UFJD2D'

    expectedUserCount = 3
    expectedServiceCount = 3

    resultUserCount = len(subscriptionHandler.usersSubscriptions)
    resultServiceCount = len(subscriptionHandler.usersSubscriptions[userId_1])

    assert(resultUserCount == expectedUserCount)
    assert(userId_1 in subscriptionHandler.usersSubscriptions)
    assert(userId_2 in subscriptionHandler.usersSubscriptions)
    assert(resultServiceCount == expectedServiceCount)

def test_addUserToSubscription_Sad() :
    pass

def test_removeUserFromSubscription_Happy() :

    tag1_0 = '1UFJD2D_Intro Service'
    tag1_0 = '1UFJD2D_Dumb Service'
    tag2_0 = '2UFJD2D_Dumb Service'
    userId_1 = '1UFJD2D'

    subscriptionHandler.removeUserFromSubscription(tag1_0)
    subscriptionHandler.removeUserFromSubscription(tag2_0)

    expectedUserCount = 3
    expectedServiceCount = 2

    resultUserCount = len(subscriptionHandler.usersSubscriptions)
    resultServiceCount = len(subscriptionHandler.usersSubscriptions[userId_1])

    assert(resultUserCount == expectedUserCount)
    assert(resultServiceCount == expectedServiceCount)
    assert(userId_1 in subscriptionHandler.usersSubscriptions)

def test_removeUserFromSubscription_Sad() :
    pass

def test_getUserIdsForServiceName() :
    
    userId = '1UFJD2D'
    expected = ['Intro Service', 'Another Service']

    result = subscriptionHandler.getServicesListForUsersId(userId)

    assert(expected == result)
    
def getServicesListForUsersId() :
    pass

# def test_unsceduleJob() :

#     expectedResult = subscriptionHandler.unsceduleJob()

#     assert(expectedResult == )
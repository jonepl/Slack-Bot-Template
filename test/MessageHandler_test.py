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

from MessageHandler import MessageHandler

messageHandler = None
rawInput1 = None
rawInput2 = None
rawInput3 = None
botID = "BotID"

def setup_module(module):

    global messageHandler 
    global rawInput1
    global rawInput2
    global rawInput3
    messageHandler = MessageHandler(Queue.Queue(), Queue.Queue(), botID, False)

    rawInput1 = [{'text': "Hello <@" + botID + "> my name is tester", 'user': 'TESTUSER123', 'team': 'TESTTESM123', 'channel': 'TESTCHANNEL123', 'bot_id': 'TESTBOT123', 'ts': '1524798523.000234', 'type': 'message', 'event_ts': '1524798523.000234'}]
    rawInput2 = [{'event_ts': '1527524745.000005', 'msg': '1527524744.000299', 'imageUri': None, 'content': 'Hello', 'type': 'desktop_notification', 'subtitle': 'J Dolla', 'launchUri': 'slack://channel?id=TESTCHANNEL123&message=123&team=TEAM', 'avatarImage': 'https://avatars.slack-edge.com/file.png', 'ssbFilename': 'knock_brush.mp3', 'title': 'SLACK_NAME', 'channel': 'TESTCHANNEL123','is_shared': False}]
    rawInput3 = [{'avatarImage': 'someImage.png', 'launchUri': 'slack://channel?id=someId', 'imageUri': None, 'subtitle':'J Dolla', 'event_ts': '1527526728.000092', 'channel': 'TESTCHANNEL123', 'title': 'SLACK_NAME', 'ssbFilename': 'file.mp3', 'is_shared': False, 'type': 'desktop_notification', 'content': 'Hello', 'msg': '1527526728.000025'}]

# FIXME: Stub determineAction and generateMessageResponse
def test_parseInput() :

    expected = {
        "user" : "TESTUSER123",
        "message" : "Hello  my name is tester",
        "channel" : "TESTCHANNEL123",
        "action" : "writeToSlack",
        "response" : "Sup bro."
    }
    result = messageHandler.parseInput(rawInput1)

    assert(result["user"] == expected["user"])
    assert(result["message"] == expected["message"])
    assert(result["channel"] == expected["channel"])
    assert(result["action"] == expected["action"])
    assert(not result["response"] == False)

def test_stripTag() :

    message = "What is today's date"
    result = messageHandler.stripTag(message + "<@" +  botID + ">")

    assert(message == result)

def test_determineSchedule_Add_Happy() :

    message = "new intro services"
    expected = ("add", 'intra-day', 'seconds', 30)

    result = messageHandler.determineSchedule(message)

    assert(result == expected)

def test_determineSchedule_Remove_Happy() :

    message = "remove intro services"
    expected = ("remove", 'intra-day', 'seconds', 30)

    result = messageHandler.determineSchedule(message)

    assert(result == expected)

def test_determineSchedule_Update_Happy() :

    message = "update intro services"
    expected = ("update", 'intra-day', 'minutes', 1)

    result = messageHandler.determineSchedule(message)

    assert(result == expected)

def test_botMentioned() :

    result = messageHandler.botMentioned(rawInput1)

    assert(result == True)

    #python3 -m pytest
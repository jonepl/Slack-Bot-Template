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

import ServiceManager
import serviceConfig as sConfig

serviceManager = None
serviceConfig = None
messageInfo = None

# TODO: Figure out how to decouple config file state from this test
def setup_module(module) :

    global serviceManager
    global serviceConfig
    global messageInfo

    serviceManager = ServiceManager.ServiceManager()
    serviceConfig = sConfig.services
    messageInfo = {
        "channel": "ABC123ZYX262524",
        "slackUserId": "BDF246ACE135",
        "action": None,
        "responseType": None,
        "response": None,
        "serviceInfo" : {}
    }

def test_getAllServices() :
    
    result = serviceManager.getAllServices()
    assert(result == serviceConfig)

# Bound to config of 
def test_getServiceNames() :
    expected = prepServiceNames(serviceConfig)
    result = serviceManager.getServicesNames()
    assert(result == expected)

def test_validateConfig_Happy():
    
    try:
        serviceManager.validateConfig()
    except Exception as e:
        pytest.fail(e)

#TODO: Stub out _isValid* methods from being called
#TODO: Expect message to be printed
def test_validateConfig_Sad(capfd) :
    expectedMessage = "Exception:  is an invalid name for service: {'name': '', 'entrypoint': 'helloWorldService.py', 'path': 'services/scripts/textService', 'language': 'python'}"
    config = [
        {
            'name' : '', 
            'path' : 'services/scripts/textService',
            'language' : 'python',
            'entrypoint' : 'helloWorldService.py',
            'runnable' : True
        }
    ]
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        serviceManager.validateConfig(config)


def test_getServiceDetails_Happy() :

    serviceName = serviceConfig[0]['name']
    expected = serviceConfig[0]

    result = serviceManager.getServiceDetails(serviceName)

    assert(result == expected)

def test_getServiceDetails_Sad() :

    serviceName = 'Some non Existing Service'
    expected = None

    result = serviceManager.getServiceDetails(serviceName)

    assert(result == expected)

    # out, err = capfd.readouterr()
    # assert out == expectedMessage

def test_getServicePath_Happy() :
    serviceName = serviceConfig[0]['name']
    expected = serviceConfig[0]['path']
    
    result = serviceManager.getServicePath(serviceName)

    assert(result == expected)

def test_getServicePath_Sad() :
    serviceName = 'Some None Existing Service'
    expected = None
    
    result = serviceManager.getServicePath(serviceName)

    assert(result == expected)

def test_getServiceLanguage_Happy() :
    serviceName = serviceConfig[0]['name']
    expected = serviceConfig[0]['language']
    
    result = serviceManager.getServiceLanguage(serviceName)

    assert(result == expected)

def test_getServiceLanguage_Sad() :
    serviceName = 'Some None Existing Service'
    expected = None
    
    result = serviceManager.getServiceLanguage(serviceName)

    assert(result == expected)

def test_getServiceEntrypoint_Happy() :
    serviceName = serviceConfig[0]['name']
    expected = serviceConfig[0]['entrypoint']
    
    result = serviceManager.getServiceEntrypoint(serviceName)

    assert(result == expected)

def test_getServiceEntrypoint_Sad() :
    serviceName = 'Some None Existing Service'
    expected = None
    
    result = serviceManager.getServiceEntrypoint(serviceName)

    assert(result == expected)

def test_generateSlackResponse_Happy1() :

    expected = {
        "channel": "ABC123ZYX262524",
        "slackUserId": "BDF246ACE135",
        "action": 'writeToFile',
        "responseType": 'file',
        "response": 'test/ServiceManager_test.py',
        "serviceInfo" : {}
    }
    jsonString = '{ "responseType" : "file", "contents" : "test/ServiceManager_test.py" }'
    byteString = jsonString.encode('utf-8')

    result = serviceManager.generateSlackResponse(byteString, messageInfo)

    assert(result == expected)


def test_generateSlackResponse_Happy2() :

    expected = {
        "channel": "ABC123ZYX262524",
        "slackUserId": "BDF246ACE135",
        "action": 'writeToSlack',
        "responseType": 'text',
        "response": 'the cow jumped over the moon',
        "serviceInfo" : {}
    }
    jsonString = '{ "responseType" : "text", "contents" : "the cow jumped over the moon" }'
    byteString = jsonString.encode('utf-8')

    result = serviceManager.generateSlackResponse(byteString, messageInfo)
    
    assert(result == expected)

def test_generateSlackResponse_Sad1() :

    expected = { }
    jsonString = '{ "response" : "text", "contents" : "the cow jumped over the moon" }'
    byteString = jsonString.encode('utf-8')

    result = serviceManager.generateSlackResponse(byteString, messageInfo)

    assert(result == expected)

    # with pytest.raises(Exception, match="Output {} is malformed".format(output)) as excinfo:
    #    serviceManager.isValidServiceOutput(output)

def test_generateSlackResponse_Sad2() :

    expected = { }
    jsonString = '{ "responseType" : "dumbResponseType", "contents" : "the cow jumped over the moon" }'
    byteString = jsonString.encode('utf-8')

    result = serviceManager.generateSlackResponse(byteString, messageInfo)

    assert(result == expected)    
    # with pytest.raises(Exception, match="Invalid responseType") as excinfo:
    #     ServiceManager.ServiceManager.validateServiceOutput(output)


# Assert no exceptions are raised
def test__isValidName_Happy():
    try:
        ServiceManager._isValidName("Some Valid Service Name")
    except Exception as e:
        pytest.fail(e)

def test__isValidName_Sad() :
    name = ''
    with pytest.raises(Exception, match="{} is an invalid name".format(name)) as excinfo:
        ServiceManager._isValidName(name)

def test__hasDuplicatedName_Happy() :

    services = ['one', 'two', 'three', 'four']
    
    try:
        ServiceManager._hasDuplicatedName(services)
    except Exception as e:
        pytest.fail(e)

def test__hasDuplicatedName_Sad() :

    services = ['one', 'two', 'three', 'one']
    
    with pytest.raises(Exception, match="Duplicate Service names found. Please use unique Service Names.") as excinfo:
        ServiceManager._hasDuplicatedName(services)

def test__validateCommands_Happy() :

    service = serviceConfig[0]
    try :
        ServiceManager._validateCommands(service)
    except Exception as e :
        pytest.fail(str(e))

# Helper Function
def prepServiceNames(services) :
    sList = []
    for service in services :
        sList.append(service['name'])
    return sList

# def test__validateCommands_whenPythonNotInstalled() :

#     with pytest.raises(Exception, match="{} is an invalid name".format(name)) as excinfo:
#         ServiceManager._validateCommands(service)

# def test__validateCommands_whenPythonIsWrongVersion() :

#     service = serviceConfig[0]
#     with pytest.raises(Exception, match="{} is an invalid name".format(name)) as excinfo:
#         ServiceManager._validateCommands(service)

        

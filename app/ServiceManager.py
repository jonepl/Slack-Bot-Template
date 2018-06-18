'''
File: ServiceManager
Description: A Singleton Class that handles services state, 
             validates services config list and service output

'''

import sys, os, subprocess, re, json

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import config.serviceConfig as sConfig

SUPPORTED_LANGUAGES = ["python", "python3", "node"]

# TODO: Consider extracting ServiceManager functionality out other classes
class ServiceManager(object) :

    _instance = None

    def __new__(self, services=sConfig.services) :
        if (not self._instance) :

            self._instance = super(ServiceManager, self).__new__(self)
            self.services = services
            self.serviceNames = self.getServicesNames(self)
        return self._instance

    def getAllServices(self):
        return self.services

    def getServicesNames(self) :
        serviceNames = []
        for services in self.services :
            serviceNames.append(services['name'])
        return serviceNames

    def validateConfig(self, configServices=None) :

        services = configServices if configServices != None else self.services
        
        for service in services :
                try:
                    _isValidName(service["name"])
                    _isValidPath(service["path"])
                    _isValidLanguage(service["language"])
                    _isValidEntrypoint(service["path"], service["entrypoint"])
                    _hasDuplicatedName(self.serviceNames)
                    _validateCommands(service)
                except Exception as e:
                    print("Exception: {} for service: {}".format(e, service))
                    sys.exit(1)

    def getServiceDetails(self, serviceName) :
        for service in self.services :
            if(service['name'] ==  serviceName) :
                return service
        return None

    def getServicePath(self, serviceName) :
        for service in self.services :
            if(service['name'] ==  serviceName) :
                return service['path']
        return None

    def getServiceLanguage(self, serviceName):
        for service in self.services :
            if(service['name'] ==  serviceName) :
                return service['language']
        return None

    def getServiceEntrypoint(self, serviceName):
        for service in self.services :
            if(service['name'] ==  serviceName) :
                return service['entrypoint']   
        return None

    def getSupportedLanguages(self) :
        return SUPPORTED_LANGUAGES

    def isValidServiceOutput(self, output) :
        valid = True
        if('responseType' in output and 'contents' in output) :

            if(output['responseType'].lower() == 'file') :
                try:
                    _isValidPath(output['contents'])
                except Exception as e:
                    valid = False
                    print("Invalid Path: " + str(e))

            elif(output['responseType'].lower() == 'text') :
                pass

            elif(output['responseType'].lower() == 'sharedfile') :
                pass
            
            else :
                valid = False
                print("Invalid responseType")
                #raise Exception("Invalid responseType")
        else :
            valid = False
            print("Output {} is malformed".format(output))
            #raise Exception("Output {} is malformed".format(output))
        
        return valid

    def generateSlackResponse(self, output, messageInfo) :
        
        response = {}
        outputJson = json.loads(output.decode('utf-8'))

        if('responseType' in outputJson and 'contents' in outputJson) :
            
            response = messageInfo

            if(outputJson['responseType'].lower() == 'file') :
                try:
                    _isValidPath(outputJson['contents'])
                except Exception as e:
                    print("Invalid Path: " + str(e))
                    return response
                
                response['action'] = 'writeToFile'
                response['responseType'] = 'file'

            elif(outputJson['responseType'].lower() == 'text') :
                
                response['action'] = 'writeToSlack'
                response['responseType'] = 'text'

            elif(outputJson['responseType'].lower() == 'sharedfile') :
                
                response['action'] = 'writeToSharedFile'
                response['responseType'] = 'file'

            elif(outputJson['responseType'].lower() == 'snippet') :

                response['action'] = 'writeToFile'
                response['responseType'] = 'file'
            
            else :
                print("Invalid responseType")
                return { }

            response['response'] = outputJson['contents']

            return response

        else :
            print("Invalid responseType")
            return response
        

def _isValidName(name) :
    if(not name) :
        raise Exception("{} is an invalid name".format(name))

def _isValidPath(path) :
    if(not os.path.exists(path) and 'internal' != path.lower()) :
        raise Exception("{} is an invalid location".format(path))
    
def _isValidLanguage(language) :
    if(not language in SUPPORTED_LANGUAGES) :
        raise Exception("{} is an unsupported language".format(language))

def _isValidEntrypoint(path, entrypoint) :
    fullpath = "{}/{}".format(path, entrypoint)
    if(not os.path.isfile(fullpath) and 'internal' != path.lower()) :
        raise Exception("{} is an invalid entrypoint point".format(fullpath))

def _hasDuplicatedName(services) :
    if(len(services) != len(set(services))) :
        raise Exception("Duplicate Service names found. Please use unique Service Names.")

def _validateCommands(service):

    if('python' in service['language'].lower()) :

        languageVersion = subprocess.check_output(['python3', '--version'])
        version = languageVersion.decode('utf-8')

        if('Python' in version) :

            match = re.match(r'Python 3.[1-9].*', version)

            if(match == None) :
                raise Exception('Python version {} not supported.'.format(version.strip("\n")))
            
            else :
                print("Successfully validated {}".format(service['name']))
        else :
            raise Exception('Python is not supported on this machine')

def _checkFileInfo(service) :

    runnable = service['fileInfo']['runnable']
    dateModified = service['Info']['dateModified']

    if( isinstance(runnable, bool) and isinstance(dateModified, float) ) :
        if(service['path'].lower() != 'internal') :
            modified = os.path.getmtime('{}/{}'.format(service['path'], service['entrypoint']))
            if(modified > service['dateModified']) :
                service['runnable'] = True
                service['dateModified'] = modified
            elif(modified < service['dateModified']) :
                service['dateModified'] = modified
    else :
        raise Exception('Error in services.fileInfo. Set')


        


def main():
    # ServiceManager.validateConfig()
    # sn = ServiceManager.getServicesNames()
    # print(sn)
    # sd = ServiceManager.getServiceDetails(sn[0])
    # print(sd)
    # sl = ServiceManager.getSupportedLanguages()
    # print(sl)

    service = {
        'name' : 'Picture Service',
        'path' : 'services/scripts/FileService',
        'language' : 'python3',
        'entrypoint' : 'pictureService.py',
    }
    _validateCommands(service)

if __name__ == '__main__':
    main()
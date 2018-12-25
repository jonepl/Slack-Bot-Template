'''
Store you script in the service folder and fill out the configuration below

Schema contains:
    name --> Name on Service as you'd like it to appear in Slack
    path --> Path to root directory of script
    language --> language used in script
    entrypoint --> name of file which starts program
'''

services = [
    {
        'name' : 'Hello World Service', 
        'path' : 'services/scripts/textService',    
        'language' : 'python',
        'entrypoint' : 'helloWorldService.py'
    },
    {
        'name' : 'Picture Service',
        'path' : 'services/scripts/FileService',
        'language' : 'python',
        'entrypoint' : 'pictureService.py'
    }
]
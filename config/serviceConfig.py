services = [
    {
        'name' : 'Intro Service', 
        'path' : 'services/scripts/textService',
        'language' : 'python',
        'entrypoint' : 'helloWorldService.py',
        'runnable' : True
    },
    {
        'name' : 'Picture Service',
        'path' : 'services/scripts/FileService',
        'language' : 'python',
        'entrypoint' : 'pictureService.py',
        'runnable' : True
    },
    {
        'name' : 'Internal Service',
        'path' : "Internal",
        'language' : 'python',
        'entrypoint' : 'helloJob',
        'runnable' : True
    }
]

# use import json dump to read in json return typ
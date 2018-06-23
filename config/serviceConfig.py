services = [
    {
        'name' : 'Intro Service', 
        'path' : 'services/scripts/textService',
        'language' : 'python',
        'entrypoint' : 'helloWorldService.py'
    },
    {
        'name' : 'Picture Service',
        'path' : 'services/scripts/FileService',
        'language' : 'python',
        'entrypoint' : 'pictureService.py'
    },
    {
        'name' : 'Internal Service',
        'path' : "Internal",
        'language' : 'python',
        'entrypoint' : 'helloJob'
    }
]

# use import json dump to read in json return typ
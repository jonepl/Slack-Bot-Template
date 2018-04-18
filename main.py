import config.creds as config

from app.SlackBot import SlackBot
from app.ExampleBot import ExampleBot
#from app.ResponseHandler import ResponseHandler

xBot = ExampleBot(config.slack['token'])
xBot.run();

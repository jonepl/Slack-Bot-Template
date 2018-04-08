import config.creds as config

from app.slackBot import SlackBot
from app.exampleBot import ExampleBot

xBot = ExampleBot(config.slack['token'])
xBot.run();

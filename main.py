import config.creds as config

from app.slackBot import SlackBot
from app.growthAnalysisBot import GrowthAnalysisBot

gaBot = GrowthAnalysisBot(config.slack['token'])
gaBot.run();

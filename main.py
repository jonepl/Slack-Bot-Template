import time;
import config.creds as config

from app.slackBot import SlackBot
from app.growthAnalysisBot import GrowthAnalysisBot

growthAnalysisBot = GrowthAnalysisBot(config.slack['token'])

growthAnalysisBot.writeToSlack("#general", "message");


# https://www.youtube.com/watch?v=QFPT37NoALA

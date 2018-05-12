import os
import config.creds as config
import argparse

if not os.path.exists("./logs"): os.makedirs("./logs")

from app.SlackBot import SlackBot
from app.ExampleBot import ExampleBot

def main():

    args = prepCmdArgs();
    xBot = ExampleBot(config.slack['token'], args.debug)
    xBot.run()

def prepCmdArgs() :
    
    parser = argparse.ArgumentParser(description='Kicks off an instance of of a Slackbot')
    parser.add_argument('-d', '--debug', action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    main()

import os, sys

# Adds App, Config directory to sys path for testing
path = os.path.abspath(__file__)

app = path[0:path.find("main.py")] + "app"
config = path[0:path.find("main.py")] + "config"
sys.path.append(app)
sys.path.append(config)

import creds as config
from ServiceManager import ServiceManager
import argparse

if not os.path.exists("./logs"): os.makedirs("./logs")

from SlackBot import SlackBot
from ExampleBot import ExampleBot

def main():

    args = prepCmdArgs()
    try:

        ServiceManager().validateConfig()
        xBot = ExampleBot(config.slack['token'], args.debug)
        xBot.run()
    except Exception as e:
        print("Exception: " + e)
        sys.exit(1)


def prepCmdArgs() :
    
    parser = argparse.ArgumentParser(description='Kicks off an instance of of a Slackbot')
    parser.add_argument('-d', '--debug', action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    main()

import pytest
import sys, os

# Adds App, Config directory to sys path for testing
path = os.path.abspath(__file__)
app = path[0:path.find("test")] + "app"
config = path[0:path.find("test")] + "config"
sys.path.append(app)
sys.path.append(config)

@pytest.fixture
def slackClient() :
    from SlackBot import SlackBot;
    import creds as config
    return SlackBot(config.slack['token']);

def test_connectTest(slackClient):
    pass
    #assert(slackClient.connect() == True);


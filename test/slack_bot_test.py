import pytest
from main import *;

def test_slackConnect():
    assert slackConnect() == True;

@pytest.mark.skip(reason="Not fully implemented")
def test_slackReadRTM():
    print(test_slackReadRTM());

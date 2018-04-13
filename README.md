# Slack Bot Template

## Setup:

### 1. Install slack bot
```sh
$ pip install slackclient
```

### 2. Retrive a Slack API token for your Slack app from:
  https://get.slack.help/hc/en-us/articles/215770388-Create-and-regenerate-API-tokens
  
  NOTE:  Make sure to read the [Slack Documentation](https://api.slack.com/) and look through the available slack apps before developing your custom slack bot. There might be a Slack Apps that already does what you'd like to have done. 

### 3. Add token to config/creds.py

```python
slack = {
    'token' : 'your-token-goes-here'
}
```

### 4. Create Your Custom Slackbot

A bunch of typically usage slack functions can be inherited from the slackBot.py class. Use test example bot as a guide as needed.


## Resources
* Slack Documentation: https://api.slack.com/
* Python Slack documentation: https://python-slackclient.readthedocs.io/en/1.0.2/
* Python Slack git repo: https://github.com/slackapi/python-slackclient

This project was developed using Python 3.5.2 


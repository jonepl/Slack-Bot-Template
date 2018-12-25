<h1 align="center">
  <br>
  <a href="#"><img src="https://www.spaceotechnologies.com/wp-content/themes/spaceotechnologies/images/services/slack-development/slackdroid.png" alt="Markdownify" width="200"></a>
  <br>
  Slack Bot Template
  <br>
</h1>

<h4 align="center">A quick easy to use Slack bot template.</h4>

<p align="center">
  <a href="#">
    <img src="https://img.shields.io/badge/Python-v3.5-blue.svg" alt="Gitter">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/contributions-welcome-orange.svg">
  </a>
</p>

## Setup:

### 1. Install SlackClient
```sh
$ sudo pip install slackclient
```

### 2. Retrive a Slack API token:
Head to this link to get your Slack API token set up for your application : 

```sh
https://get.slack.help/hc/en-us/articles/215770388-Create-and-regenerate-API-tokens
```

  NOTE:  Make sure to read the [Slack Documentation](https://api.slack.com/) and look through the available slack apps before developing your custom slack bot. There might be a Slack Apps that already does what you'd like to have done. 

### 3. Add token to config/creds.py

```python
slack = {
    'token' : 'your-token-goes-here',
    'mongoDB' : {
        'dbName' : 'DBname',
        'uri' : 'mongodb://mongoURI',
        'collectionName' : 'collectionName'
    }
}
```

### 4. Create Your Custom Slackbot

A bunch of typically usage slack functions can be inherited from the slackBot.py class. Use test example bot as a guide as needed.


### 5. Install other dependencies
```sh
$ sudo pip install pymongo
$ sudo pip install schedule
$ sudo pip install pytest
```

## Testing:

```sh
$ pytest -v
```

## Resources
* Slack Documentation: https://api.slack.com/
* Python Slack documentation: https://python-slackclient.readthedocs.io/en/1.0.2/
* Python Slack git repo: https://github.com/slackapi/python-slackclient

This project was developed using Python 3.5.2 


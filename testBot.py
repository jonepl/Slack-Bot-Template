import time;
from slackclient import SlackClient

class slackCommuncation(object):

    def __init__(self, token="put stuff here"):
        super(slackCommuncation, self).__init__()
        self.slack_client = SlackClient(token);
        self.appName = "myawesomeBot"

    def slackConnect(self) :
        return self.slack_client.rtm_connect();

    def slackReadRTM(self) :
        return self.slack_client.rtm_read();

    def parseSlackInput(self, input, botID) :
        botATID = "<"+botID+">"
        print(input)
        if input :
            input = input[0]

            if input['type'] != "hello" or input['type'] != "user_typing" or  input['type'] != "desktop_notification":
                if botATID in input['text']:
                    user = rawInput['user'];
                    message = rawInput['text'];
                    channel = rawInput['channel'];
                    return [str(user), str(message), str(channel)];
                else :
                    return [None,None,None];

    def getBotID(self, botusername) :
        api_call = self.slack_client.api_call('users.list');
        users = api_call["members"]
        for user in users:
            if 'name' in user and botusername in user.get('name') and not user.get('deleted'):
                return user.get('id');

    def writetoSlack(self, channel, message) :
        return self.slack_client.api_call("chat.postMessage", channel=channel, text=message, as_user=True)

class mainFunc(slackCommuncation):

    def __init__(self):
        super(mainFunc, self).__init__()
        BOTID = self.getBotID(self.appName);

    def decideWhethertotakeAction(self, input) :
        if input :
            user, message, channel = input;
            print(input);
            return self.writetoSlack(channel, message);

    def run(self) :
        self.slackConnect();
        BOTID = self.getBotID("welcome-bot");
        while True :
            self.decideWhethertotakeAction(self.parseSlackInput(self.slackReadRTM(), BOTID));
            time.sleep(1);


if __name__ == "__main__":
    instance = mainFunc();
    instance.run();

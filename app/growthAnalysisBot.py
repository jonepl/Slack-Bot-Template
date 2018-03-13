from app.slackBot import SlackBot;

import time;

class GrowthAnalysisBot(SlackBot) :

    def __init__(self, token):
        super().__init__(token);
        super().connect(self.token);

    def run(self) :
        while(True) :
            rawInput = super().readChannels();
            print(rawInput);
            # print("~~~~~~~~~~~~");
            # self.parseRawInput(rawInput);
            time.sleep(1);

    # Overriden method
    def parseRawInput(self, rawInput):
        result = [];
        if (not self.isEmpty(rawInput)) :
            if(self.isMessage(rawInput)) :
                result = self.parseMessage(rawInput);
                self.determineAction(result);
        # if(len(rawInput) > 0 and 'text' in rawInput[0]) :
        #     rawInput = rawInput[0];
        #     user = rawInput['user'];
        #     message = rawInput['text'];
        #     channel = rawInput['channel'];
        #     result = [str(user), str(message), str(channel)]
        #     print(result);

    def isTyping(self, rawInput) :
        if(rawInput[0].get('type') == 'user_typing') : return True;
        else : return False

    def isEmpty(self, rawInput) :
        if not rawInput : return True;
        else : return False

    def isMessage(self, rawInput) :
        if(rawInput[0].get('type') == 'message') : return True;
        else : return False;

    def parseMessage(self, rawInput) :
        rawInput = rawInput[0];
        user = rawInput['user'];
        message = rawInput['text'];
        channel = rawInput['channel'];
        return { 'user' : str(user), 'message' : str(message), 'channel' : str(channel) };

    def determineAction(self, cleanedInput) :
        self.writeToSlack(cleanedInput['channel'], cleanedInput['message']);

if __name__ == '__main__':
    from slackBot import SlackBot;
    gab = GrowthAnalysisBot("");

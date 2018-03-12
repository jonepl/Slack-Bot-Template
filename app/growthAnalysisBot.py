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
            time.sleep(1);

    # Overriden method
    def parseRawInput(self):
        result = [];
        if(len(input) > 0 and 'text' in input[0]) :
            input = input[0];
            print(input);
            user = input['user'];
            message = input['text'];
            channel = input['channel'];
            result = [str(user), str(message), str(channel)]
            print(result);
            return result;
        else :
            return result;

if __name__ == '__main__':
    from slackBot import SlackBot;
    gab = GrowthAnalysisBot("");

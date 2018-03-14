from app.slackBot import SlackBot;

import time;

class GrowthAnalysisBot(SlackBot) :

    def __init__(self, token):
        super().__init__(token);
        self.connect(self.token);

    def run(self) :
        #self.writeToSlack('D9GCAPGNL', 'Testing');
        while(True) :
            rawInput = self.readChannels();
            print(rawInput);
            # print("~~~~~~~~~~~~");
            self.handle(rawInput);
            time.sleep(1);

    # Overriden method
    def handle(self, rawInput):
        result = [];
        if(not self.isEmpty(rawInput)) :
            if(self.isMessage(rawInput)) :
                message = self.parseMessage(rawInput);
                self.writeToSlack(message['channel'], message['message']);
            elif (self.isTyping(rawInput)) :
                pass;
            elif (self.isHello(rawInput)) :
                pass;
            else :
                print("Unknown input type");
        return result;

    def parseMessage(self, rawInput) :
        rawInput = rawInput[0];
        user = rawInput['user'];
        message = rawInput['text'];
        channel = rawInput['channel'];
        return { 'user' : str(user), 'message' : str(message), 'channel' : str(channel) };

    def isTyping(self, rawInput) :
        if(rawInput[0].get('type') == 'user_typing') : return True;
        else : return False

    def isEmpty(self, rawInput) :
        if not rawInput : return True;
        else : return False

    def isMessage(self, rawInput) :
        if(rawInput[0].get('type') == 'message') : return True;
        else : return False;

    def isHello(self, rawInput) :
        if(rawInput[0].get('type') == 'hello') : return True;
        else : return False



if __name__ == '__main__':
    from slackBot import SlackBot;
    gab = GrowthAnalysisBot("");

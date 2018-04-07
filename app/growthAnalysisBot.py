from app.slackBot import SlackBot;

import time;

class GrowthAnalysisBot(SlackBot) :

    def __init__(self, token, debug=True):
        self.users = {};
        self.debug = debug;
        self.running = False;
        super().__init__(token);

    def run(self) :
        self.running = True;
        if(self.connect(self.token)) :
            while(self.running) :
                try:    
                    rawInput = self.readChannels();
                    print(rawInput)
                    self.parseRawInput(rawInput);
                    time.sleep(1);
                except (KeyboardInterrupt, SystemError) :
                    print("\n~~~~~~~~~~~KeyboardInterrupt Exception Found~~~~~~~~~~~\n");
                    self.running = False;                

    # Overriden method
    def handle(self, rawInput):
        result = [];
        if (not self.isEmpty(rawInput) and self.isMessage(rawInput) and self.notSelf(rawInput)) :
            result = self.parseMessage(rawInput);
            self.determineAction(result);

    def parseMessage(self, rawInput) :
        rawInput = rawInput[0];
        user = rawInput['user'];
        message = rawInput['text'];
        channel = rawInput['channel'];
        return { 'user' : str(user), 'message' : str(message), 'channel' : str(channel) };

    def determineAction(self, cleanedInput) :
        self.writeToSlack(cleanedInput['channel'], cleanedInput['message']);

    def reply(self, content) :
        self.writeToSlack(content['channel'], content['message'])

    def notSelf(self, rawInput) :
        if(rawInput[0].get('user') == self.getBotID()) : return False;
        else : return True; 

    def isTyping(self, rawInput) :
        if(rawInput[0].get('type') == 'user_typing') : return True;
        else : return False

    def isEmpty(self, rawInput) :
        if not rawInput : return True;
        else : return False

    def isMessage(self, rawInput) :
        if(rawInput[0].get('type') == 'message') : return True;
        else : return False;

if __name__ == '__main__':
    from slackBot import SlackBot;
    gab = GrowthAnalysisBot("");

from app.SlackBot import SlackBot;

import time;

class ExampleBot(SlackBot) :

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
    # TODO: Need to handle up feature to send message
    def parseRawInput(self, rawInput):
        result = [];
        if (not self.isEmpty(rawInput)) :
            # Handles message
            if(self.isMessage(rawInput) and self.notSelf(rawInput)) :
                result = self.parseMessage(rawInput);
                self.reply(result);
            else :
                print("Something other than a message");
                print(rawInput);

    # Parses the raw slack input
    def parseMessage(self, rawInput) :

        parsedMessage = {};
        user = rawInput[0]['user'];
        message = rawInput[0]['text'];
        channel = rawInput[0]['channel'];
        directMessaged = None;

        # Determine if bot is being direct messaged 
        # Reference: #https://stackoverflow.com/questions/41111227/how-can-a-slack-bot-detect-a-direct-message-vs-a-message-in-a-channel
        if (not self.getGroupInfo(channel).get('ok')) and (not self.getChannelInfo(channel).get('ok')) :
            directMessaged = True 
        else :
            directMessaged = False

        # Bot has been mentioned in a chat or direct messaged
        if(self.getBotID() in rawInput[0]['text'] or directMessaged) :
            parsedMessage = { 'user' : str(user), 'message' : str(self.stripTag(message)), 'channel' : str(channel) };
            return parsedMessage;
        else :
            return {}

    # Removes the Slack bot ID from a message
    def stripTag(self, message) :
        botTag = "<@" + self.getBotID() + ">"
        return message.replace(botTag, '');

    # TODO: Rewrite to handle multiple actions    
    def determineAction(self, cleanedInput) :
        self.writeToSlack(cleanedInput['channel'], cleanedInput['message']);

    # Replays back to users
    def reply(self, content) :
        if(content) : 
            self.writeToSlack(content['channel'], content['message'])

    # Determines if the raw input was sent by this bot
    def notSelf(self, rawInput) :
        if(rawInput[0].get('user') == self.getBotID()) : return False;
        else : return True; 
    
    # Detect if a users is typing
    def isTyping(self, rawInput) :
        if(rawInput[0].get('type') == 'user_typing') : return True;
        else : return False

    # Detects if raw input is Empty
    def isEmpty(self, rawInput) :
        if not rawInput : return True;
        else : return False

    # Detects if the raw input is a message
    def isMessage(self, rawInput) :
        if(rawInput[0].get('type') == 'message') : return True;
        else : return False;

if __name__ == '__main__':
    from slackBot import SlackBot;
    xBot = ExampleBot("");

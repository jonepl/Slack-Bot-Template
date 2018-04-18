import random

# Sentences we'll respond with if the user greeted us
GREETING_KEYWORDS = ("hello", "hi", "greetings", "sup", "what's up",)

GREETING_RESPONSES = ["Sup bro", "Hey", "*nods*", "What up homie?"]

class ResponseHandler(object):
    
    def __init__(self) :
        pass;
    
    def handle(self, sentence) :
        for word in sentence.split():
            if word.lower() in GREETING_KEYWORDS:
                return random.choice(GREETING_RESPONSES)

    

if __name__ == '__main__' :
    rh = ResponseHandler();
    response = rh.handle("Sup welcome_bot");
    print(response);
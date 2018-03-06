from app.slackBot import SlackBot;

class GrowthAnalysisBot(SlackBot) :
    def __init__(self, token):
        super().__init__(token)

if __name__ == '__main__':
    from slackBot import SlackBot;
    gab = GrowthAnalysisBot("");

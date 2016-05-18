# -*- coding: utf-8 -*-
import logging

from skills.alexa import AlexaSkill

APP_ID = 'amzn1.echo-sdk-ams.app.b9944c3a-185d-4669-a202-3702c9b8fd4b'

logger = logging.getLogger()


class SitterfiedSkill(AlexaSkill):
    SESSION_ENDED_MESSAGE = 'As you wish!'
    
    def __init__(self, *args, **kwargs):
        super(SitterfiedSkill, self).__init__(APP_ID, *args, **kwargs)

        self.intents['IntentRequest']['RequestSitterIntent'] = self.request_sitter

    def on_launch(self, request, session, response):
        speech_text = 'Hi. What can I help you with?'
        reprompt_text = 'For instructions, you can say, please help me.'
        return response.ask(speech_text, reprompt=reprompt_text)

    def request_sitter(self, intent, session, response):
        return response.tell(self.SESSION_ENDED_MESSAGE)

# -*- coding: utf-8 -*-
import logging
import six

from utils import camel_to_snake

logger = logging.getLogger(__name__)


def create_speech_object(options):
    if isinstance(options, six.string_types):
        options = {
            'speech': options,
            'type': AlexaSkill.speech_output_type.get('PLAIN_TEXT'),
        }
        
    return {
        'text': options.get('speech', options),
        'type': options.get('type', AlexaSkill.speech_output_type.get('PLAIN_TEXT')),
    }


def create_speechlet_object(
    session,
    speech_output,
    end_session=False,
    reprompt=None,
    title=None,
    content=None,
):
    response = {
        'outputSpeech': create_speech_object(speech_output),
        'shouldEndSession': end_session,
    }

    if reprompt:
        response['reprompt'] = {
            'outputSpeech': create_speech_object(reprompt),
        }

    if title and content:
        response['card'] = {
            'content': content,
            'title': title,
            'type': 'Simple',
        }

    result = {
        'response': response,
        'version': '1.0',
    }

    if session and session.attributes:
        result['sessionAttributes'] = dict(session.attributes)

    return result


def preprocess_event(event):
    from skills.utils import ProtectedDict, tupperware

    session = event.get('session')
    if session:
        session.update({'attributes': ProtectedDict(session.get('attributes', {}))})

    return tupperware(event)


class Response():

    def __init__(self, context, session):
        self.context = context
        self.session = session

    def tell(self, speech_output):
        return create_speechlet_object(
            self.session,
            speech_output,
            end_session=True,
        )

    def tell_with_card(self, speech_output, title, content):
        return create_speechlet_object(
            self.session,
            speech_output,
            end_session=True,
            title=title,
            content=content,
        )

    def ask(self, speech_output, reprompt):
        return create_speechlet_object(
            self.session,
            speech_output,
            reprompt=reprompt,
            end_session=False,
        )

    def ask_with_card(self, speech_output, reprompt, title, content):
        return create_speechlet_object(
            self.session,
            speech_output,
            reprompt=reprompt,
            end_session=False,
            title=title,
            content=content,
        )


class AlexaSkill(object):
    intents = { 'IntentRequest': {} }
    speech_output_type = {
        'PLAIN_TEXT': 'PlainText',
        'SSML': 'SSML',
    }

    def __init__(self, app_id):
        self.app_id = app_id

    def process_intent_request(self, event, context, response):
        return self.on_intent(event.request, event.session, response)

    def process_launch_request(self, event, context, response):
        return self.on_launch(event.request, event.session, response)

    def process_session_ended_request(self, event, context, *args):
        return self.on_session_ended(event.request, event.session)

    def on_intent(self, request, session, response):
        intent = request.intent
        intent_name = intent.name

        if intent_name not in self.intents['IntentRequest']:
            raise NotImplementedError('Unsupported intent: %s' % intent_name)

        return self.intents['IntentRequest'][intent_name](intent, session, response)

    def on_launch(self, request, session, response):
        raise NotImplementedError('`on_launch` should be implemented by a subclass')

    def on_session_ended(self, request, session):
        pass

    def on_session_started(self, request, session):
        pass

    def execute(self, event, context):
        try:
            event = preprocess_event(event)
            session_app_id = event.session.application.applicationId
            logger.info('Session applicationId %s' % session_app_id)

            # Validate that the request originated from an authorized source.
            if self.app_id and session_app_id != self.app_id:
                logger.error('The application ids do not match %s and %s' % (session_app_id, self.app_id))
                raise 'Invalid app_id'

            if event.session.new:
                self.on_session_started(event.request, event.session)

            request_type = 'process_%s' % camel_to_snake(event.request.type)
            request_handler = getattr(self, request_type)
            if not request_handler:
                raise Exception('`%s` request handler not implemented' % request_type)

            return request_handler(event, context, Response(context, event.session))
        except Exception as exc:
            logger.error('Unexpected exception %s' % exc)

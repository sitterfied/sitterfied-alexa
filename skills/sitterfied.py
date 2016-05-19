# -*- coding: utf-8 -*-
import logging

from skills.alexa import AlexaSkill
from skills.utils import (
    format_date,
    format_duration,
    format_time,
    merge_data,
    set_session_data,
)

APP_ID = 'amzn1.echo-sdk-ams.app.b9944c3a-185d-4669-a202-3702c9b8fd4b'

logger = logging.getLogger(__name__)


class SitterfiedSkill(AlexaSkill):
    SESSION_ENDED_MESSAGE = 'As you wish!'

    def __init__(self, *args, **kwargs):
        super(SitterfiedSkill, self).__init__(APP_ID, *args, **kwargs)

        self.intents['IntentRequest'].update({
            'AMAZON.CancelIntent': self.cancel_intent,
            'AMAZON.HelpIntent': self.help_intent,
            'AMAZON.StopIntent': self.stop_intent,
            'DialogRequestSitterIntent': self.dialog_request_sitter,
            'RequestSitterIntent': self.request_sitter,
        })

    def on_launch(self, request, session, response):
        logger.info(
            '[LaunchEvent] request id: %s, session id: %s'
            % (request.requestId, session.sessionId)
        )

        speech_text = 'Hi. When do you need a sitter?'
        reprompt_text = 'For instructions, you can say, please help me.'
        return response.ask(speech_text, reprompt=reprompt_text)

    def on_session_ended(self, request, session):
        logger.info(
            '[SessionEndedEvent] request id: %s, session id: %s'
            % (request.requestId, session.sessionId)
        )

        # Session clenaup logic

    def on_session_started(self, request, session):
        logger.info(
            '[SessionStartedEvent] request id: %s, session id: %s'
            % (request.requestId, session.sessionId)
        )

        # Session initiaion logic

    def cancel_intent(self, intent, session, response):
        return response.tell(self.SESSION_ENDED_MESSAGE)

    def help_intent(self, intent, session, response):
        speech_text = 'This is the help.'
        speech_output = {
            'speech': speech_text,
            'type': AlexaSkill.speech_output_type.get('PLAIN_TEXT'),
        }

        reprompt_text = 'What can I help you with?'
        reprompt_output = {
            'speech': reprompt_text,
            'type': AlexaSkill.speech_output_type.get('PLAIN_TEXT'),
        }

        return response.ask(speech_output, reprompt=reprompt_output)

    def stop_intent(self, intent, session, response):
        return response.tell(self.SESSION_ENDED_MESSAGE)

    def dialog_request_sitter(self, intent, session, response):
        '''
        Process an initial request to start a dialog.

        '''
        date, start, end, duration = merge_data(intent, session)

        if not date:
            return self.process_no_slots_dialog_request(intent, session, response)

        if not start:
            return self.process_date_slot_dialog_request(intent, session, response)

        if not end and not duration:
            return self.process_start_slot_dialog_request(intent, session, response)

        return self.confirm_booking_details(intent, session, response)

    def request_sitter(self, intent, session, response):
        return self.dialog_request_sitter(intent, session, response)

    def process_date_slot_dialog_request(self, intent, session, response):
        '''
        Process a request where only the date slot information was provided.

        '''
        date, start, end, duration = merge_data(intent, session)

        if not start:
            # Store the Date in the session for future requests
            set_session_data(session, 'date', date)

            # Prompt the user for the start time of the booking
            speech = (
                'Please try saying a start time for your request. For example, 7pm.'
            )
            reprompt = (
                'You can also say a start time and end time, or a duration and '
                'start time. For example, 7pm to 11pm or 4 hours starting at 7pm.'
            )
            return response.ask(speech, reprompt)

        if not duration and not end:
            # Prompt the user for the end time or duration of the booking
            return self.process_start_slot_dialog_request(intent, session, response)

        # We have all the information we need to create the request
        return self.confirm_booking_details(intent, session, response)

    def process_start_slot_dialog_request(self, intent, session, response):
        '''
        Process a request where only the start slot informat was provided.

        '''
        date, start, end, duration = merge_data(intent, session)

        if not end and not duration:
            # Store the Start in the session for future requests
            set_session_data(session, 'start', start)

            # Prompt the user for a duration or end time
            speech = (
                'Please try saying a duration for your request. For example, 4 hours.'
            )
            reprompt = (
                'You can also say just an end time. For example, 11pm.'
            )
            return response.ask(speech, reprompt)

        # We have all the information we need to create the request
        return self.confirm_booking_details(intent, session, response)

    def process_end_duration_slot_dialog_request(self, intent, session, response):
        '''
        Process a request containing End or Duration slot values.

        '''
        date, start, end, duration = merge_data(intent, session)

        # Store the values in the session for future requests
        set_session_data(session, 'end', end)
        set_session_data(session, 'duration', duration)

        if date and start and (end or duration):
            # We have all the information we need to create the request
            return self.confirm_booking_details(intent, session, response)

        if not start:
            # No start, prompt the user for a start date
            return self.process_date_slot_dialog_request(intent, session, response)

        return self.process_no_slots_dialog_request(intent, session, response)

    def process_no_slots_dialog_request(self, intent, session, response):
        '''
        Process a request where no slot information was provided.

        '''
        date, start, end, duration = merge_data(intent, session)

        if not date:
            speech = (
                'When do you need a sitter?'
            )
            return response.ask(speech, speech)
        elif not start:
            return self.process_date_slot_dialog_request(intent, session, response)
        elif not end and not duration:
            return self.process_start_slot_dialog_request(intent, session, response)

        return self.help_intent(intent, session, response)

    def confirm_booking_details(self, intent, session, response):
        date, start, end, duration = merge_data(intent, session)

        set_session_data(session, 'End', end)
        set_session_data(session, 'Duration', duration)

        human_date = format_date(date)
        human_start = format_time(start)
        human_duration = format_duration(duration)
        human_end = format_time(end)

        speech = (
            'You need a sitter %s at %s %s. Is that correct?'
            % (
                'on %s' % human_date if human_date not in ['tomorrow', 'today'] else human_date,
                human_start,
                'for %s' % human_duration if human_duration else 'until %s' % human_end
            )
        )

        return response.ask(speech, speech)

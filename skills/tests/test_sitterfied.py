# -*- coding: utf-8 -*-
from copy import deepcopy
from hamcrest import (
    all_of,
    assert_that,
    contains_string as cs,
    has_entries,
    has_entry,
    is_,
)
from unittest import TestCase

from skills.sitterfied import SitterfiedSkill
from skills.tests.utils import load_fixture, set_slot_value


class TestSitterfiedSkill(TestCase):

    def setUp(self):
        self.skill = SitterfiedSkill()

    def test_on_launch(self):
        launch_event = load_fixture('launch_event.json')
        response = self.skill.execute(launch_event, {}).get('response')

        assert_that(response, has_entry('shouldEndSession', is_(False)))
        assert_that(response.get('outputSpeech'), has_entries(
            'text', is_('Hi. When do you need a sitter?'),
            'type', is_('PlainText'),
        ))

    def test_request_sitter_intent(self):
        event = load_fixture('intent_event.json')
        output = self.skill.execute(deepcopy(event), {})

        response = output.get('response')
        assert_that(response, has_entry('shouldEndSession', is_(False)))
        assert_that(response.get('outputSpeech'), has_entries(
            text=all_of(
                cs('need a sitter'),
                cs('at'),
                cs('until'),
                cs('Is that correct?'),
            ),
            type='PlainText'
        ))

    def test_dialog_request_sitter_intent(self):
        event = load_fixture('dialog_intent_event.json')
        output = self.skill.execute(deepcopy(event), {})

        session = output.get('sessionAttributes')
        assert_that(session, is_(None))

        response = output.get('response')
        assert_that(response, has_entry('shouldEndSession', False))
        assert_that(response.get('outputSpeech'), has_entries(
            text=cs('sitter'),
            type='PlainText',
        ))

        date = '2015-05-21'
        event = set_slot_value(event, 'Date', date)
        event.get('session').update(new=False)
        output = self.skill.execute(deepcopy(event), {})

        session = output.get('sessionAttributes')
        assert_that(session, has_entry('date', date))

        response = output.get('response')
        assert_that(response, has_entry('shouldEndSession', False))
        assert_that(response.get('outputSpeech'), has_entries(
            text=cs('start time'),
            type='PlainText'
        ))

        # Update session data
        event.get('session').update(attributes=dict(session))

        start = '18:00'
        event = set_slot_value(event, 'Start', start)
        output = self.skill.execute(deepcopy(event), {})

        session = output.get('sessionAttributes')
        assert_that(session, has_entry('date', date))
        assert_that(session, has_entry('start', start))

        response = output.get('response')
        assert_that(response, has_entry('shouldEndSession', False))
        assert_that(response.get('outputSpeech'), has_entries(
            text=cs('duration'),
            type='PlainText'
        ))

        # Update session data
        event.get('session').update(attributes=dict(session))

        duration = 'PT4H'
        event = set_slot_value(event, 'Duration', duration)
        output = self.skill.execute(deepcopy(event), {})

        session = output.get('sessionAttributes')
        assert_that(session, has_entry('date', date))
        assert_that(session, has_entry('start', start))

        response = output.get('response')
        assert_that(response, has_entry('shouldEndSession', False))
        assert_that(response.get('outputSpeech'), has_entries(
            text=all_of(
                cs('need a sitter'),
                cs('at'),
                cs('for'),
                cs('Is that correct?')
            ),
            type='PlainText'
        ))

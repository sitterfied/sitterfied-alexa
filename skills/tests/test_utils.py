# -*- coding: utf-8 -*-
import json
import os

from hamcrest import assert_that, is_, none

from skills.utils import (
    ProtectedDict,
    get_session_data,
    get_slot_or_none,
    set_session_data,
    merge_data,
    tupperware,
)


fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures')


session = tupperware({
    'attributes': ProtectedDict({
        'date': '2016-05-16',
        'start': '19:00',
        'end': '21:00',
        'duration': 'PT2H',
    })
})


def test_get_session_data():
    date, start, end, duration = get_session_data(session)
    assert_that(date, is_(session.attributes.get('date')))
    assert_that(start, is_(session.attributes.get('start')))
    assert_that(end, is_(session.attributes.get('end')))
    assert_that(duration, is_(session.attributes.get('duration')))


def test_get_slot_or_none():
    with open(os.path.join(fixture_dir, 'intent_event.json')) as f:
        event = tupperware(json.load(f))

    intent = event.request.intent
    assert_that(get_slot_or_none(intent, 'Date'), is_(event.request.intent.slots.Date.value))
    assert_that(get_slot_or_none(intent, 'Duration'), none())
    assert_that(get_slot_or_none(intent, 'DoesNotExist'), none())


def test_merge_data():
    intent = {
        'slots': {
            'Date': {
                'name': 'Date',
                'value': '2016-12-31',
            },
            'Start': {
                'name': 'Start',
                'value': '18:00',
            },
            'End': {
                'name': 'End',
                'value': '22:00',
            },
            'Duration': {
                'name': 'Duration',
                'value': None,
            },
        },
    }

    date, start, end, duration = merge_data(tupperware(intent), session)
    assert_that(date, is_('2016-12-31'))  # Session data overwritten by intent data
    assert_that(start, is_('18:00'))  # Session data overwritten by intent data
    assert_that(end, is_('22:00'))  # Session data overwritten by intent data
    assert_that(duration, is_('PT2H'))  # No intent data, so returns session data

    
def test_set_session_data():
    date = '2017-05-21'
    set_session_data(session, 'date', date)
    assert_that(session.attributes.get('date'), is_(date))

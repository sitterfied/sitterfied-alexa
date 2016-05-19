# -*- coding: utf-8 -*-
import json
import os


def load_fixture(filename):
    fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures', filename)

    with open(fixture_dir, 'r') as f:
        return json.load(f)


def set_slot_value(event, name, value):
    event \
        .get('request') \
        .get('intent') \
        .get('slots') \
        .get(name) \
        .update(value=value)
    return event

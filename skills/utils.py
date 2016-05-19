# -*- coding: utf-8 -*-
import collections
import humanize
import isodate
import re

from datetime import datetime
from UserDict import IterableUserDict


def camel_to_snake(s):
    '''
    Convert a camel or upper-camel case string to snake case.

    >>> camel_to_snake('UpperCamelCase')
    'upper_camel_case'

    '''
    return re.sub("([A-Z])", "_\\1", s).lower().lstrip("_")


def format_date(date):
    '''
    Convert a date in YYYY-MM-DD format to a human readable date.

    Return None if no date is passed, or date is an empty string.

    >>> format_date(None)

    >>> format_date('')

    >>> format_date('2016-12-31')
    'December 31'

    '''
    if not date:
        return None

    return humanize.naturalday(isodate.parse_date(date), '%B %d')


def format_duration(duration):
    '''
    Convert a duration in ISO-8601 format to a human readable duration.

    Return None if duration is empty or None.

    >>> format_duration(None)

    >>> format_duration('')

    >>> format_duration('PT4H')
    '4 hours'

    '''
    if not duration:
        return None

    return humanize.naturaldelta(isodate.parse_duration(duration))


def format_time(time):
    '''
    Convert an ISO-8601 time string in 'hh:mm' format to a human readable time.

    Return None if time is empty or None.

    >>> format_time(None)

    >>> format_time('')

    >>> format_time('19:00')
    '07:00 PM'

    '''
    if not time:
        return None

    return datetime.strptime(time, '%H:%M').strftime('%I:%M %p')


def get_session_data(session):
    '''
    Retrieve all session data from the session and return as a tuple.

    '''
    date = session.attributes.get('date')
    start = session.attributes.get('start')
    end = session.attributes.get('end')
    duration = session.attributes.get('duration')
    return date, start, end, duration


def get_slot_data(intent):
    '''
    Retrieve all slot data from the intent and return as a tuple.

    '''
    date = get_slot_or_none(intent, 'Date')
    start = get_slot_or_none(intent, 'Start')
    end = get_slot_or_none(intent, 'End')
    duration = get_slot_or_none(intent, 'Duration')
    return date, start, end, duration


def merge_data(intent, session):
    '''
    Merge intent data and session data and return a tuple of all values.

    '''
    date, start, end, duration = get_slot_data(intent)
    session_date, session_start, session_end, session_duration = get_session_data(session)

    date = date or session_date
    start = start or session_start
    end = end or session_end
    duration = duration or session_duration

    return date, start, end, duration


def get_slot_or_none(intent, name):
    '''
    Retrieve the value of a slot or return None.

    '''
    if hasattr(intent.slots, name):
        slot = getattr(intent.slots, name)
        return getattr(slot, 'value', None)

    return None


def set_session_data(session, name, value):
    '''
    Set the session data for the given name.

    '''
    session.attributes.update({name: value})


def tupperware(mapping):
    """
    Convert mappings to 'tupperwares' recursively.

    Lets you use dicts like they're JavaScript Object Literals (~=JSON)...
    It recursively turns mappings (dictionaries) into namedtuples.
    Thus, you can cheaply create an object whose attributes are accessible
    by dotted notation (all the way down).

    Use cases:

        * Fake objects (useful for dependency injection when you're making
         fakes/stubs that are simpler than proper mocks)

        * Storing data (like fixtures) in a structured way, in Python code
        (data whose initial definition reads nicely like JSON). You could do
        this with dictionaries, but namedtuples are immutable, and their
        dotted notation can be clearer in some contexts.

    .. doctest::

        >>> t = tupperware({
        ...     'foo': 'bar',
        ...     'baz': {'qux': 'quux'},
        ...     'tito': {
        ...             'tata': 'tutu',
        ...             'totoro': 'tots',
        ...             'frobnicator': ['this', 'is', 'not', 'a', 'mapping']
        ...     }
        ... })
        >>> t # doctest: +ELLIPSIS
        Tupperware(tito=Tupperware(...), foo='bar', baz=Tupperware(qux='quux'))
        >>> t.tito # doctest: +ELLIPSIS
        Tupperware(frobnicator=[...], tata='tutu', totoro='tots')
        >>> t.tito.tata
        'tutu'
        >>> t.tito.frobnicator
        ['this', 'is', 'not', 'a', 'mapping']
        >>> t.foo
        'bar'
        >>> t.baz.qux
        'quux'

    Args:
        mapping: An object that might be a mapping. If it's a mapping, convert
        it (and all of its contents that are mappings) to namedtuples
        (called 'Tupperwares').

    Returns:
        A tupperware (a namedtuple (of namedtuples (of namedtuples (...)))).
        If argument is not a mapping, it just returns it (this enables the
        recursion).

    """
    __author__ = 'github.com/hangtwenty'  # noqa

    if (
        isinstance(mapping, collections.Mapping) and
        not isinstance(mapping, ProtectedDict)
    ):
        for key, value in mapping.iteritems():
            mapping[key] = tupperware(value)
        return namedtuple_from_mapping(mapping)
    return mapping


def namedtuple_from_mapping(mapping, name="Tupperware"):
    this_namedtuple_maker = collections.namedtuple(name, mapping.iterkeys())
    return this_namedtuple_maker(**mapping)


class ProtectedDict(IterableUserDict):
    """
    A class that exists just to tell `tupperware` not to eat it.

    `tupperware` eats all dicts you give it, recursively; but what if you
    actually want a dictionary in there? This will stop it. Just do
    ProtectedDict({...}) or ProtectedDict(kwarg=foo).

    """

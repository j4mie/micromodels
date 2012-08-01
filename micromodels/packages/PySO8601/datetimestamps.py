"""
Years:
    YYYY
Calendar Dates:
    YYYY-MM-DD
    YYYY-MM
    YYYYMMDD
    YYMMDD
Week Dates:
    YYYY-Www-D
    YYYY-Www
    YYYYWwwD
    YYYYWww
Ordinal Dates:
    YYYY-DDD
    YYYYDDD
Times:
    hh:mm:ss
    hh:mm
    hhmmss
    hhmm
    <time>Z
    <time>+|-hh:mm
    <time>+|-hhmm
    <time>+|-hh
"""

from datetime import datetime, date
import re

from utility import *
from timezones import Timezone

FRACTION = r'(?P<fraction>\.\d+)?'

TIMEZONE = r'(?P<timezone>Z|(\+|-)(\d{2})(:?\d{2})?)?$'

DATE_FORMATS = (
    # Extended combined format
    (re.compile(r'^(?P<matched>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})'+FRACTION+TIMEZONE), '%Y-%m-%dT%H:%M:%S'),
    (re.compile(r'^(?P<matched>\d{4}-\d{2}-\d{2}T\d{2}:\d{2})'+TIMEZONE), '%Y-%m-%dT%H:%M'),

    # Extended separate format
    (re.compile(r'^(?P<matched>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'+FRACTION+TIMEZONE), '%Y-%m-%d %H:%M:%S'),
    (re.compile(r'^(?P<matched>\d{4}-\d{2}-\d{2} \d{2}:\d{2})'+TIMEZONE), '%Y-%m-%d %H:%M'),
    (re.compile(r'^(?P<matched>\d{4}-\d{2}-\d{2} \d{2})'+TIMEZONE), '%Y-%m-%d %H'),

    # Basic combined format
    (re.compile(r'^(?P<matched>\d{8}T\d{2}:\d{2}:\d{2})'+FRACTION+TIMEZONE), '%Y%m%dT%H:%M:%S'),
    (re.compile(r'^(?P<matched>\d{8}T\d{2}:\d{2})'+TIMEZONE), '%Y%m%dT%H:%M'),
    (re.compile(r'^(?P<matched>\d{8}T\d{6})'+FRACTION+TIMEZONE), '%Y%m%dT%H%M%S'),
    (re.compile(r'^(?P<matched>\d{8}T\d{4})'+TIMEZONE), '%Y%m%dT%H%M'),
    (re.compile(r'^(?P<matched>\d{8}T\d{2})'+TIMEZONE), '%Y%m%dT%H'),

    # Basic separate format
    (re.compile(r'^(?P<matched>\d{8} \d{2}:\d{2}:\d{2})'+FRACTION+TIMEZONE), '%Y%m%d %H:%M:%S'),
    (re.compile(r'^(?P<matched>\d{8} \d{2}:\d{2})'+TIMEZONE), '%Y%m%d %H:%M'),
    (re.compile(r'^(?P<matched>\d{8} \d{6})'+TIMEZONE), '%Y%m%dT%H%M%S'),
    (re.compile(r'^(?P<matched>\d{8} \d{4})'+TIMEZONE), '%Y%m%dT%H%M'),
    (re.compile(r'^(?P<matched>\d{8} \d{2})'+TIMEZONE), '%Y%m%dT%H'),

    # Week Dates
    (re.compile(r'^(?P<matched>\d{4}-W\d{2}-\d)'+TIMEZONE), '%Y-W%U-%w'),
    (re.compile(r'^(?P<matched>\d{4}-W\d{2})'+TIMEZONE), '%Y-W%U'),
    (re.compile(r'^(?P<matched>\d{4}W\d{3})'+TIMEZONE), '%YW%U%w'),
    (re.compile(r'^(?P<matched>\d{4}W\d{2})'+TIMEZONE), '%YW%U'),

    # Ordinal Dates
    (re.compile(r'^(?P<matched>\d{4}-\d{3})'+TIMEZONE), '%Y-%j'),
    (re.compile(r'^(?P<matched>\d{7})'+TIMEZONE), '%Y%j'),

    # Dates
    (re.compile(r'^(?P<matched>\d{4}-\d{2}-\d{2})'), '%Y-%m-%d'),
    (re.compile(r'^(?P<matched>\d{4}-\d{2})'), '%Y-%m'),
    (re.compile(r'^(?P<matched>\d{8})'), '%Y%m%d'),
    (re.compile(r'^(?P<matched>\d{6})'), '%y%m%d'),
    (re.compile(r'^(?P<matched>\d{4})'), '%Y'),

    )

TIME_FORMATS = (
    # Times
    (re.compile(r'^(?P<matched>\d{2}:\d{2}:\d{2})'+FRACTION+TIMEZONE), '%H:%M:%S'),
    (re.compile(r'^(?P<matched>\d{2}\d{2}\d{2})'+FRACTION+TIMEZONE), '%H%M%S'),
    (re.compile(r'^(?P<matched>\d{2}:\d{2})'+TIMEZONE), '%H:%M'),
    (re.compile(r'^(?P<matched>\d{4})'+TIMEZONE), '%H%M'),

    )


def parse_date(datestring):
    """Attepmts to parse an ISO8601 formatted ``datestring``.

    Returns a ``datetime.datetime`` object.
    """
    datestring = str(datestring).strip()

    if not datestring[0].isdigit():
        raise ParseError()

    if 'W' in datestring.upper():
        try:
            datestring = datestring[:-1] + str(int(datestring[-1:]) -1)
        except:
            pass

    for regex, pattern in DATE_FORMATS:
        if regex.match(datestring):
            found = regex.search(datestring).groupdict()
            dt = datetime.utcnow().strptime(found['matched'], pattern)

            if 'fraction' in found and found['fraction'] is not None:
                dt = dt.replace(microsecond=int(found['fraction'][1:]))

            if 'timezone' in found and found['timezone'] is not None:
                dt = dt.replace(tzinfo=Timezone(found.get('timezone', '')))

            return dt

    return parse_time(datestring)


def parse_time(timestring):
    """Attepmts to parse an ISO8601 formatted ``timestring``.

    Returns a ``datetime.datetime`` object.
    """
    timestring = str(timestring).strip()

    for regex, pattern in TIME_FORMATS:
        if regex.match(timestring):
            found = regex.search(timestring).groupdict()

            dt = datetime.utcnow().strptime(found['matched'], pattern)
            dt = datetime.combine(date.today(), dt.time())

            if 'fraction' in found and found['fraction'] is not None:
                dt = dt.replace(microsecond=int(found['fraction'][1:]))

            if 'timezone' in found and found['timezone'] is not None:
                dt = dt.replace(tzinfo=Timezone(found.get('timezone', '')))

            return dt

    raise ParseError()



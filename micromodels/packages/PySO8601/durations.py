import datetime
import re

from utility import *

WEEK_DURATION = re.compile(r'''# start
^P # duration designator
(\d+) # capture the number of weeks
W$ # week designator
''', re.VERBOSE)

SIMPLE_DURATION = re.compile(r"""# start
^P                               # duration designator
((?P<years>\d*[\.,]?\d+)Y)?      # year designator
((?P<months>\d*[\.,]?\d+)M)?     # month designator
((?P<days>\d*[\.,]?\d+)D)?       # day designator
(?P<time>T)?                     # time designator
(?(time)                         # time designator lookup;
                                 #   skip next section if
                                 #   reference doesn't exist
  ((?P<hours>\d*[\.,]?\d+)H)?    # hour designator
  ((?P<minutes>\d*[\.,]?\d+)M)?  # minute designator
  ((?P<seconds>\d*[\.,]?\d+)S)?  # second designator
)$
""", re.VERBOSE)

COMBINED_DURATION = re.compile(r"""# start
^P                                 # duration designator
(?P<years>\d{4})?                  # year designator
-?                                 # separator
(?P<months>\d{2})?                 # month designator
-?                                 # separator
(?P<days>\d{2})?                   # day designator
(?P<time>[T|\s])?                  # time designator
(?(time)                           # time designator lookup;
                                   #   skip next section if
                                   #   reference doesn't exist
  (?P<hours>\d{2})                 # hour designator
  :?                               # separator
  (?P<minutes>\d{2})?              # minute designator
  (?(minutes)                      # minutes designator lookup
    :?                             # separator
    (?P<seconds>\d{2})?            # second designator
  )
)$
""", re.VERBOSE)

ELEMENTS = {
    'years': 0,
    'months': 0,
    'days': 0,
    'hours': 0,
    'minutes': 0,
    'seconds': 0,
    }


def parse_duration(duration):
    """Attepmts to parse an ISO8601 formatted ``duration``.

    Returns a ``datetime.timedelta`` object.
    """
    duration = str(duration).upper().strip()

    elements = ELEMENTS.copy()

    for pattern in (SIMPLE_DURATION, COMBINED_DURATION):
        if pattern.match(duration):
            found = pattern.match(duration).groupdict()
            del found['time']

            elements.update(dict((k, int(v or 0))
                                 for k, v
                                 in found.iteritems()))

            return datetime.timedelta(days=(elements['days'] +
                                            _months_to_days(elements['months']) +
                                            _years_to_days(elements['years'])),
                                      hours=elements['hours'],
                                      minutes=elements['minutes'],
                                      seconds=elements['seconds'])            
    
    return ParseError()


DAYS_IN_YEAR = 365
MONTHS_IN_YEAR = 12

def _years_to_days(years):
    return years * DAYS_IN_YEAR

def _months_to_days(months):
    return (months * DAYS_IN_YEAR) / MONTHS_IN_YEAR

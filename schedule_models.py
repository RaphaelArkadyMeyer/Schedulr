
from datetime import datetime
from enum import Enum
import re
import logging

class Day(Enum):
    Monday    = 1
    Tuesday   = 2
    Wednesday = 3
    Thursday  = 4
    Friday    = 5
    Other     = 7


day_dict = {
        'Monday':    Day.Monday,
        'Tuesday':   Day.Tuesday,
        'Wednesday': Day.Wednesday,
        'Thursday':  Day.Thursday,
        'Friday':    Day.Friday
    }

def meeting_from_json(obj, course_title):
    logging.info('Created new meeting for ' + course_title)
    days         = obj['DaysOfWeek'].split(', ')
    start_time   = obj['StartTime']
    duration     = obj['Duration']
    meeting_type = obj['Type']

    days       = [day_dict.get(day, Day.Other) for day in days]
    start_time = datetime.strptime(start_time[:19], '%Y-%m-%dT%H:%M:%S')
    start_time = start_time.hour*60 + start_time.minute
    if duration == 'PT0S':
        duration = [50, 50, 65, 110, 110, 110][len(days)]
    else:
        duration = parse_iso8601_duration(duration) / 60

    return Meeting(days, start_time, duration, meeting_type, course_title)


def parse_iso8601_duration(duration_str):
    # https://stackoverflow.com/questions/25296416/how-can-i-parse-and-compare-iso-8601-durations-in-python#35936407
    match = re.match(
        r'P((?P<years>\d+)Y)?((?P<months>\d+)M)?((?P<weeks>\d+)W)?((?P<days>\d+)D)?T((?P<hours>\d+)H)?((?P<minutes>\d+)M)?((?P<seconds>\d+)S)?',
        duration_str
    ).groupdict()
    return int(match['years'] or 0)*365*24*3600 + \
        int(match['months'] or 0)*30*24*3600 + \
        int(match['weeks'] or 0)*7*24*3600 + \
        int(match['days'] or 0)*24*3600 + \
        int(match['hours'] or 0)*3600 + \
        int(match['minutes'] or 0)*60 + \
        int(match['seconds'] or 0)


class Meeting:
    def __init__(self, days=[], start_time=7*60+30, duration=50, meeting_type=None, course_title=''):
        self.days         = list(days)
        self.start_time   = int(start_time)
        self.duration     = int(duration)
        self.meeting_type = str(meeting_type)
        self.course_title = str(course_title)


class Section:
    def __init__(self, meetings=[], section_type=""):
        self.meetings = list(meetings)
        self.section_type = section_type

class Course:
    def __init__(self, sections=[]):
        self.sections = list(sections)


class APIClass:
    def __init__(self, courses=[]):
        self.courses = list(courses)
        pass


class Schedule:
    def __init__(self):
        pass










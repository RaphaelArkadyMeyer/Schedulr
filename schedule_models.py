
from datetime import datetime
from enum import Enum

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

def meeting_from_json(obj):
    days         = obj['DaysOfWeek'].split(', ')
    start_time   = obj['StartTime']
    duration     = obj['Duration']
    meeting_type = obj['Type']

    days       = [day_dict.get(day, Day.Other) for day in days]
    start_time = datetime.strptime(start_time[:-6], '%Y-%m-%dT%H:%M:%S')
    duration   = parse_iso8601_duration(duration)

    return Meeting(days, start_time, duration, meeting_type)


def parse_iso8601_duration(duration_str):
    match = re.match(
        r'P(?P<years>\d+)Y)?(?P<months>\d+)M)?(?P<weeks>\d+)W)?(?P<days>\d+)D)?T((?P<hours>\d+)H)?((?P<minutes>\d+)M)?((?P<seconds>\d+)S)?',
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
    def __init__(self, days=[], start_time=7*60+30, duration=50, meeting_type=None):
        self.days         = list(days)
        self.start_time   = int(start_time)
        self.end_time     = int(end_time)
        self.meeting_type = str(meeting_type)


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










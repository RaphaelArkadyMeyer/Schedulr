

from datetime import datetime
import json
import logging

from read_courses import CourseCache
import schedule_models


def meetings_overlap(meeting1, meeting2):
    if not set(meeting1.days).intersection(meeting2):
        return False  # The meetings don't occur on the same day
    if meeting1.start_time < meeting2.end_time:
        return True   # meeting1 is after meeting2
    if meeting1.end_time > meeting2.start_time:
        return True   # meeting1 is before meeting2
    return False


def max_guess(list_dept_num):
    return next(get_all_schedules(list_dept_num))


def get_all_schedules(list_dept_num):
    s = schedule_models.Schedule()
    list_of_list_of_meetings = []
    for (dept,num) in list_dept_num:
        query = CourseCache.query(dept,num)
        section_meetings = {}
        for api_class in query:
            logging.debug('Making schedule')
            for extra_layer in api_class['DictLists']:
                for dict_list in extra_layer:
                    logging.debug('Heres a section')
                    meetings = dict_list['Meetings']
                    section = dict_list['Section']
                    section_type = section['Type']
                    meeting_list = section_meetings.get(section_type, [])
                    meeting_list += meetings
                    logging.debug(meeting_list)
                    section_meetings[section_type] = meeting_list
                    logging.debug(section_meetings)
            logging.debug(section_meetings)
        list_of_list_of_meetings += section_meetings.values()
    meeting_objects = []
    for list_of_list_of_meetings in list_of_list_of_meetings:
        meeting_objects.append(
                [ schedule_models.meeting_from_json(meeting)
                    for meeting in list_of_list_of_meetings ]
                )
    return _get_schedule_helper(list_of_list_of_meetings)


def _get_schedule_helper(list_of_list_of_meetings, meetings_in_schedule=[]):
    logging.debug('Schedule recusion')
    logging.debug(list_of_list_of_meetings)
    logging.debug(meetings_in_schedule)
    if not list_of_list_of_meetings:
        yield meetings_in_schedule
        return  # Can't add any more because we're done :-)
    head, *tail = list_of_list_of_meetings
    for meeting in head:
        if not any(meetings_overlap(meeting, other) for other in meetings_in_schedule):
            for schedule in _get_schedule_helper(tail, [meeting] + meetings_in_schedule):
                yield schedule




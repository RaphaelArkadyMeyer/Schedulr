from datetime import datetime
import os.path
import json
import threading
import logging

from get_courses import download_all_data


class CourseCache:

    caches = None

    subject_cache = None
    course_cache = None
    section_cache = None
    api_class_cache = None
    meeting_cache = None

    query_table = None

    setup_lock = threading.Event()

    @classmethod
    def __get_caches__(cls, file_path):
        if not os.path.exists(file_path):
            download_all_data(file_path)
        f = open(file_path, 'r')
        text = f.read()
        f.close()
        return json.loads(text)

    @classmethod
    def setup(cls):
        logging.info("Getting caches...")
        cls.caches = cls.__get_caches__('./CourseInfo.json')
        logging.info('Done getting caches!')

        cls.subject_cache = cls.caches['Subjects']
        cls.course_cache = cls.caches['Courses']
        cls.section_cache = cls.caches['Sections']
        cls.api_class_cache = cls.caches['Classes']
        cls.meeting_cache = cls.caches['Meetings']

        cls.query_table = cls.__make_query_table__(cls.subject_cache,
                                                   cls.course_cache)

        # api_class used because class is a keyword
        cls.api_class_lookup_table = \
            cls.__make_lookup_table__(cls.api_class_cache, 'CourseId')
        cls.section_lookup_table = \
            cls.__make_lookup_table__(cls.section_cache, 'ClassId')
        cls.meeting_lookup_table = \
            cls.__make_lookup_table__(cls.meeting_cache, 'SectionId')

        logging.info("Unlocking Caches access")
        cls.setup_lock.set()

    @classmethod
    def wait_for_access(cls):
        cls.setup_lock.wait()

    @classmethod
    def get_subject(cls, abbrev, subjects):
        if abbrev in subjects:
            return subjects[abbrev]
        else:
            logging.error("Subject not found: {}".format(abbrev))
            return None

    @classmethod
    def __make_query_table__(cls, subject_cache, course_cache):
        query_table = dict()
        for subject_id in subject_cache:
            abbrev = subject_cache[subject_id]['Abbreviation']
            query_table[abbrev] = dict()

        for course_id in course_cache:
            course = course_cache[course_id]
            number = course['Number']
            subject_id = course['SubjectId']
            abbrev = subject_cache[subject_id]['Abbreviation']
            subject_dict = query_table[abbrev]
            if number not in subject_dict:
                subject_dict[number] = list()
            subject_dict[number].append(course_id)
            query_table[abbrev] = subject_dict
        return query_table

    @classmethod
    def __make_lookup_table__(cls, cache, odata_id_type):
        lookup_table = dict()
        for odata_id in cache:
            entry = cache[odata_id]
            lookup_id = entry[odata_id_type]
            if lookup_id not in lookup_table:
                lookup_table[lookup_id] = list()
            lookup_table[lookup_id].append(odata_id)
        return lookup_table

    @classmethod
    def get_api_object(cls, odata_id, odata_type):
        if odata_type not in cls.caches:
            logging.error("Unknown known odata type: {}".format(odata_type))
            return None
        cache = cls.caches[odata_type]
        if odata_id not in cache:
            logging.warn("ID not found in {}: {}".format(odata_type, odata_id))
            return None
        return cache[odata_id]

    @classmethod
    def get_course_ids(cls, dept, number):
        if dept not in cls.query_table:
            logging.warn("Department not found: {}".format(dept))
            return list()
        if number not in cls.query_table[dept]:
            logging.warn("Course not found in {}: {}".format(dept, number))
            return list()
        return cls.query_table[dept][number]

    @classmethod
    def get_api_class_ids(cls, course_id):
        if course_id not in cls.api_class_lookup_table:
            logging.warn("Course not found: {}".format(course_id))
            return list()
        return cls.api_class_lookup_table[course_id]

    @classmethod
    def get_section_ids(cls, api_class_id):
        if api_class_id not in cls.section_lookup_table:
            logging.warn("Class not found: {}".format(api_class_id))
            return list()
        return cls.section_lookup_table[api_class_id]

    @classmethod
    def get_meeting_ids(cls, section_id):
        if section_id not in cls.meeting_lookup_table:
            logging.warn("Section not found: {}".format(section_id))
            return list()
        return cls.meeting_lookup_table[section_id]

    @classmethod
    def parse_meeting_time(cls, meeting_time):
        # Removes unneeded timezone from input
        fixed_time = meeting_time[:19]
        logging.debug("Parse Meeting String: {}".format(fixed_time))
        return datetime.strptime(fixed_time, '%Y-%m-%dT%H:%M:%S')

    @classmethod
    def query_meeting_id(cls, meeting_id):
        meeting = cls.get_api_object(meeting_id, 'Meetings')
        if meeting is None:
            return None

        start_time = cls.parse_meeting_time(meeting['StartTime'])
        logging.debug("\t\t\t{}".format(meeting))
        logging.debug("\t\t\t{}".format(start_time))
        return meeting

    @classmethod
    def query_section_id(cls, section_id):
        section = cls.get_api_object(section_id, 'Sections')
        if section is None:
            return list()

        output = list()
        logging.debug("\t\t{}".format(section))
        meeting_id_list = cls.get_meeting_ids(section_id)
        for meeting_id in meeting_id_list:
            meeting = cls.query_meeting_id(meeting_id)
            output.append(meeting)
        return output

    @classmethod
    def query_api_class_id(cls, api_class_id):
        api_class = cls.get_api_object(api_class_id, 'Classes')
        if api_class is None:
            return list()

        logging.debug("\t{}".format(api_class))
        section_id_list = cls.get_section_ids(api_class_id)
        output = list()
        for section_id in section_id_list:
            output += cls.query_section_id(section_id)
        return output

    @classmethod
    def query_course_id(cls, course_id):
        course = cls.get_api_object(course_id, 'Courses')
        if course is None:
            return list()

        output = list()
        logging.debug(course['Title'])
        api_class_id_list = cls.get_api_class_ids(course_id)
        for api_class_id in api_class_id_list:
            output += cls.query_api_class_id(api_class_id)
        return output

    @classmethod
    def query(cls, dept, number):
        print()
        output = list()
        course_ids = cls.get_course_ids(dept, number)
        for course_id in course_ids:
            meeting_list = cls.query_course_id(course_id)
            output += meeting_list
        return output

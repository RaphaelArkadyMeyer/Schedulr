from datetime import datetime
import os.path
import json

from get_courses import download_all_data


class CourseCache:

    caches = None

    subject_cache = None
    course_cache = None
    section_cache = None
    api_class_cache = None
    meeting_cache = None

    query_table = None

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
        print("Getting caches....")
        cls.caches = cls.__get_caches__('./CourseInfo.json')
        print("Done!")
        print("{} bytes read from file.".format(cls.caches.__sizeof__()))

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

        print("End")

    @classmethod
    def get_subject(cls, abbrev, subjects):
        if abbrev in subjects:
            return subjects[abbrev]
        else:
            raise ValueError("Subject does not exists :{}".format(abbrev))

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
            raise ValueError("{} is not a known odata type".format(odata_type))
        cache = cls.caches[odata_type]
        if odata_id not in cache:
            raise ValueError("ID not found in cache")
        return cache[odata_id]

    @classmethod
    def get_course_ids(cls, dept, number):
        if dept not in cls.query_table:
            raise ValueError("Department given is invalid")
        if number not in cls.query_table[dept]:
            raise ValueError("Course not found in deptartment")
        return cls.query_table[dept][number]

    @classmethod
    def get_api_class_ids(cls, course_id):
        if course_id not in cls.api_class_lookup_table:
            raise ValueError("Class not found in the cache")
        return cls.api_class_lookup_table[course_id]

    @classmethod
    def get_section_ids(cls, api_class_id):
        if api_class_id not in cls.section_lookup_table:
            raise ValueError("No class exists")
        return cls.section_lookup_table[api_class_id]

    @classmethod
    def get_meeting_ids(cls, section_id):
        if section_id not in cls.meeting_lookup_table:
            raise ValueError("No such section exists")
        return cls.meeting_lookup_table[section_id]

    @classmethod
    def parse_meeting_time(cls, meeting_time):
        # Removes extra colon from time zone
        fixed_time = meeting_time[:19]
        print("Fixed: {}".format(fixed_time))
        return datetime.strptime(fixed_time, '%Y-%m-%dT%H:%M:%S')

    @classmethod
    def example_query_meeting_id(cls, meeting_id):
        meeting = cls.get_api_object(meeting_id, 'Meetings')
        start_time = cls.parse_meeting_time(meeting['StartTime'])
        print("\t\t\t{}".format(meeting))
        print("\t\t\t{}".format(start_time))

    @classmethod
    def example_query_section_id(cls, section_id):
        section = cls.get_api_object(section_id, 'Sections')
        print("\t\t{}".format(section))
        meeting_id_list = cls.get_meeting_ids(section_id)
        for meeting_id in meeting_id_list:
            cls.example_query_meeting_id(meeting_id)
        print()

    @classmethod
    def example_query_api_class_id(cls, api_class_id):
        api_class = cls.get_api_object(api_class_id, 'Classes')
        print("\t{}".format(api_class))
        section_id_list = cls.get_section_ids(api_class_id)
        for section_id in section_id_list:
            cls.example_query_section_id(section_id)
        print("---")

    @classmethod
    def example_query_course_id(cls, course_id):
        course = cls.get_api_object(course_id, 'Courses')
        print(course['Title'])
        try:
            api_class_id_list = cls.get_api_class_ids(course_id)
        except ValueError as err:
            return
        for api_class_id in api_class_id_list:
            cls.example_query_api_class_id(api_class_id)

    @classmethod
    def example_query(cls, dept, number):
        print()
        course_ids = cls.get_course_ids(dept, number)
        for course_id in course_ids:
            cls.example_query_course_id(course_id)

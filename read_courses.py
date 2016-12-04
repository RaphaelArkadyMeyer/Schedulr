from datetime import datetime
import threading
import logging
import json
import config

from cloudant.client import Cloudant
from cloudant.document import Document
from cloudant.result import Result


class CourseCache:

    api_url = 'https://8f130e0a-0c4f-41f3-abdd-716a84018df8-bluemix' \
              ':8bf2a56a17024e594f342b7c5870b90bb1e669260baecb81462' \
              '85732fdf2ae6f@8f130e0a-0c4f-41f3-abdd-716a84018df8-' \
              'bluemix.cloudant.com'
    api_user = '8f130e0a-0c4f-41f3-abdd-716a84018df8-bluemix'
    api_pass = '8bf2a56a17024e594f342b7c5870b90bb1e669260baecb814628' \
               '5732fdf2ae6f'

    query_table_db = None
    api_class_lookup_db = None
    section_lookup_db = None
    meeting_lookup_db = None

    query_table = dict()
    api_class_lookup_table = dict()
    section_lookup_table = dict()
    meeting_lookup_table = dict()

    db_client = None
    courses_db = None

    setup_lock = threading.Event()

    @classmethod
    def connect_to_db(cls):
        if cls.db_client is not None:
            logging.fatal("Tried to start a new DB connection"
                          " while already connected.")
            raise TypeError("Tried to start a new DB connection"
                            " while already connected.")
        cls.db_client = Cloudant(cls.api_user, cls.api_pass, url=cls.api_url)
        cls.db_client.connect()
        cls.courses_db = cls.db_client['purdue_courses']
        cls.courses_db.all_docs
        logging.info("Cloudant connection is live.")

    @classmethod
    def disconnect_db(cls):
        if cls.db_client is not Cloudant:
            logging.fatal("Tried to close a nonexistant connection")
            raise TypeError("Tried to close a nonexistant connection")
        cls.db_client.disconnect()
        cls.db_client = None
        logging.info("Cloudant connection is dead.")

    @classmethod
    def setup(cls):
        logging.info('Opening Database Connections')
        cls.connect_to_db()

        cls.query_table_db = cls.db_client['query_table']

        # 'api_class' used because 'class' is a keyword
        cls.api_class_lookup_db = cls.db_client['api_class_lookup_table']
        cls.section_lookup_db = cls.db_client['section_lookup_table']
        cls.meeting_lookup_db = cls.db_client['meeting_lookup_table']

        logging.info("Unlocking Caches access")
        cls.setup_lock.set()

        if config.COURSE_CACHE_DOWNLOAD:
            logging.info('Downloading lookup tables from Cloudant...')
            cls.get_table_from_db()

    @classmethod
    def wait_for_access(cls):
        cls.setup_lock.wait()

    @classmethod
    def get_api_object(cls, odata_id, odata_type):
        out = cls.odata_from_db(odata_id)
        if out['odata_type'] != odata_type:
            logging.fatal('Bad reference for odata_type created')
        return out

    @classmethod
    def odata_from_db(cls, odata_id):
        logging.debug("Quering id={}".format(odata_id))

        out = None
        with Document(cls.courses_db, odata_id) as doc:
            out = json.loads(doc.json())

        return out

    @classmethod
    def get_course_ids(cls, dept, number):
        try:
            number_dict = cls.query_table_db[dept]
            if number not in number_dict['dict']:
                logging.warn("Course not found in {}: {}".format(dept, number))
                return list()
            return number_dict['dict'][number]
        except (KeyError):
            logging.warn('Department not found: {}'.format(dept))
            return list()

    @classmethod
    def get_api_class_ids(cls, course_id):
        if course_id in cls.api_class_lookup_table:
            return cls.api_class_lookup_table[course_id]

        logging.warn('PurdueIo API Course object not found in local table.'
                     ' Querying online database: {}'
                     .format(course_id))
        with Document(cls.api_class_lookup_db, course_id) as doc:
            # TODO REUPLOAD API_CLASS_LOOKUP DATABASE TO CLOUDANT
            return doc.get('list', [])

    @classmethod
    def get_section_ids(cls, api_class_id):
        if api_class_id in cls.section_lookup_table:
            return cls.section_lookup_table[api_class_id]

        logging.warn('PurdueIo API Class object not found in local table.'
                     ' Querying online database: {}'
                     .format(api_class_id))
        with Document(cls.section_lookup_db, api_class_id) as doc:
            return doc['list']

    @classmethod
    def get_meeting_ids(cls, section_id):
        if section_id in cls.section_lookup_table:
            return cls.section_lookup_table[section_id]

        logging.warn('PurdueIo API Section object not found in local table.'
                     ' Querying online database: {}'
                     .format(section_id))
        with Document(cls.meeting_lookup_db, section_id) as doc:
            return doc['list']

    @classmethod
    def parse_meeting_time(cls, meeting_time):
        # Removes unneeded timezone from input
        fixed_time = meeting_time[:19]
        logging.debug("Parse Meeting String: {}".format(fixed_time))
        return datetime.strptime(fixed_time, '%Y-%m-%dT%H:%M:%S')

    @classmethod  # Gets the actual meeting for an id
    def query_meeting_id(cls, meeting_id):
        meeting = cls.get_api_object(meeting_id, 'Meetings')
        if meeting is None:
            return None

        start_time = cls.parse_meeting_time(meeting['StartTime'])
        logging.debug("\t\t\t{}".format(meeting))
        logging.debug("\t\t\t{}".format(start_time))
        return meeting

    @classmethod  # Gets the list of meetings for a section
    def query_section_id(cls, section_id):
        section = cls.get_api_object(section_id, 'Sections')
        if section is None:
            return list()

        output_list = list()
        logging.debug("\t\t{}".format(section))
        meeting_id_list = cls.get_meeting_ids(section_id)
        for meeting_id in meeting_id_list:
            meeting = cls.query_meeting_id(meeting_id)
            output_list.append(meeting)
        output = dict()
        output['Section'] = section
        output['Meetings'] = output_list
        return output

    @classmethod  # Gets the dict of section -> list(meetings) for an api_class
    def query_api_class_id(cls, api_class_id):
        # good_campus = '983c3fdc-f3f0-4f0b-a31c-c6f417e186fd'
        api_class = cls.get_api_object(api_class_id, 'Classes')
        if api_class is None:  # or api_class['CampusId'] is not good_campus:
            return list()

        logging.debug("\t{}".format(api_class))
        section_id_list = cls.get_section_ids(api_class_id)
        output = list()
        for section_id in section_id_list:
            # Dictionary value = List of meetings
            output.append(cls.query_section_id(section_id))
        return output

    # Gets the dict of api_class to (dict of section -> list(meetings))
    # for a course
    @classmethod
    def query_course_id(cls, course_id):
        course = cls.get_api_object(course_id, 'Courses')
        if course is None:
            return dict()

        output = dict()
        output['Course'] = course
        output_list = list()
        logging.debug('Course title is {}'.format(course['Title']))
        api_class_id_list = cls.get_api_class_ids(course_id)
        for api_class_id in api_class_id_list:
            output_list.append(cls.query_api_class_id(api_class_id))
        output['DictLists'] = output_list
        return output

    # Gets the dict of api_class to (dict of section -> list(meetings))
    """
    Returns block of meeting information
    @cls    The CourseCache class
    @dept   The department (i.e. "CS")
    @number The course number (i.e. 25200)
    """
    @classmethod
    def query_meeting_times(cls, dept, number):
        q = CourseCache.query(dept, number)
        if not q:
            return []
        output = list()
        for dict_list in q[0]['DictLists']:
            for section_dict in dict_list:
                output += section_dict['Meetings']
        return output

    @classmethod
    def query(cls, dept, number):
        output = list()
        course_ids = cls.get_course_ids(dept, number)
        for course_id in course_ids:
            meeting_dict = cls.query_course_id(course_id)
            output.append(meeting_dict)
        return output

    @classmethod
    def get_table_from_db(cls, package_size=5000):
        results = Result(cls.query_table_db.all_docs,
                         include_docs=True,
                         page_size=package_size)
        cls.query_table = dict()
        for result in results:
            cls.query_table[result['id']] = result['doc']['dict']
        logging.info('Downloaded query_table has {} documents'
                     .format(len(cls.query_table)))

        results = Result(cls.api_class_lookup_db.all_docs,
                         include_docs=True,
                         page_size=package_size)
        cls.api_class_lookup_table = dict()
        for result in results:
            cls.api_class_lookup_table[result['id']] = result['doc']['list']
        logging.info('Downloaded api_class_lookup_table has {} documents'
                     .format(len(cls.api_class_lookup_table)))

        results = Result(cls.section_lookup_db.all_docs,
                         include_docs=True,
                         page_size=package_size)
        cls.section_lookup_table = dict()
        for result in results:
            cls.section_lookup_table[result['id']] = result['doc']['list']
        logging.info('Downloaded section_lookup_table has {} documents'
                     .format(len(cls.section_lookup_table)))

        results = Result(cls.meeting_lookup_db.all_docs,
                         include_docs=True,
                         page_size=package_size)
        cls.meeting_lookup_table = dict()
        for result in results:
            cls.meeting_lookup_table[result['id']] = result['doc']['list']
        logging.info('Downloaded meeting_lookup_table has {} documents'
                     .format(len(cls.meeting_lookup_table)))

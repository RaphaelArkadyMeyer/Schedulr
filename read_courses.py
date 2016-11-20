from datetime import datetime
import os.path
import json

from get_courses import download_all_data

# class courseCache:



#     def __init__(self):

print("Start")


def get_caches(file_path):
    if not os.path.exists(file_path):
        download_all_data(file_path)
    f = open(file_path, 'r')
    text = f.read()
    f.close()
    return json.loads(text)


print("Getting caches....")
caches = get_caches('./CourseInfo.json')
print("Done!")
print("{} bytes read from file.".format(caches.__sizeof__()))


subject_cache = caches['Subjects']
course_cache = caches['Courses']
section_cache = caches['Sections']
api_class_cache = caches['Classes']
meeting_cache = caches['Meetings']


def get_subject(abbrev, subjects=caches['Subjects']):
    if abbrev in subjects:
        return subjects[abbrev]
    else:
        raise ValueError("Subject does not exists :{}".format(abbrev))


def make_query_table(subject_cache, course_cache):
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


query_table = make_query_table(subject_cache, course_cache)


def make_lookup_table(cache, odata_id_type):
    lookup_table = dict()
    for odata_id in cache:
        entry = cache[odata_id]
        lookup_id = entry[odata_id_type]
        if lookup_id not in lookup_table:
            lookup_table[lookup_id] = list()
        lookup_table[lookup_id].append(odata_id)
    return lookup_table


# api_class used because class is a keyword
api_class_lookup_table = make_lookup_table(api_class_cache, 'CourseId')
section_lookup_table = make_lookup_table(section_cache, 'ClassId')
meeting_lookup_table = make_lookup_table(meeting_cache, 'SectionId')


def get_api_object(odata_id, odata_type):
    if odata_type not in caches:
        raise ValueError("{} is not a known odata type".format(odata_type))
    cache = caches[odata_type]
    if odata_id not in cache:
        raise ValueError("ID not found in cache")
    return cache[odata_id]


def get_course_ids(dept, number):
    if dept not in query_table:
        raise ValueError("Department given is invalid")
    if number not in query_table[dept]:
        raise ValueError("Course not found in deptartment")
    return query_table[dept][number]


def get_api_class_ids(course_id):
    if course_id not in api_class_lookup_table:
        raise ValueError("Class not found in the cache")
    return api_class_lookup_table[course_id]


def get_section_ids(api_class_id):
    if api_class_id not in section_lookup_table:
        raise ValueError("No class exists")
    return section_lookup_table[api_class_id]


def get_meeting_ids(section_id):
    if section_id not in meeting_lookup_table:
        raise ValueError("No such section exists")
    return meeting_lookup_table[section_id]


def parse_meeting_time(meeting_time):
    # Removes extra colon from time zone
    fixed_time = meeting_time[:22] + meeting_time[23:]
    return datetime.strptime(fixed_time, '%Y-%m-%dT%H:%M:%S%z')


def example_query_meeting_id(meeting_id):
    meeting = get_api_object(meeting_id, 'Meetings')
    start_time = parse_meeting_time(meeting['StartTime'])
    print("\t\t\t{}".format(meeting))
    print("\t\t\t{}".format(start_time))


def example_query_section_id(section_id):
    section = get_api_object(section_id, 'Sections')
    print("\t\t{}".format(section))
    meeting_id_list = get_meeting_ids(section_id)
    for meeting_id in meeting_id_list:
        example_query_meeting_id(meeting_id)
    print()


def example_query_api_class_id(api_class_id):
    api_class = get_api_object(api_class_id, 'Classes')
    print("\t{}".format(api_class))
    section_id_list = get_section_ids(api_class_id)
    for section_id in section_id_list:
        example_query_section_id(section_id)
    print("---")


def example_query_course_id(course_id):
    course = get_api_object(course_id, 'Courses')
    print(course['Title'])
    try:
        api_class_id_list = get_api_class_ids(course_id)
    except ValueError as err:
        return
    for api_class_id in api_class_id_list:
        example_query_api_class_id(api_class_id)


def example_query(dept, number):
    print()
    course_ids = get_course_ids(dept, number)
    for course_id in course_ids:
        example_query_course_id(course_id)


example_query('CS', '35400')


print("End")

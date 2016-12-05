import requests
import json


def make_url(path=''):
    return 'http://api-dev.purdue.io/odata/' + path


def send_request(payload, path=''):
    resp = requests.get(make_url(path), params=payload)
    print(resp)
    if resp.status_code != 200:
        raise "Failed to get API Information"
    return resp


def request_cache(payload, odata_type, odata_type_name, key):
    resp = send_request(payload, odata_type)
    print('Request URL:{}'.format(resp.url))
    resp_list = resp.json()['value']
    print('We found {} entries matching the query'.format(len(resp_list)))
    cache = dict()
    for item in resp_list:  # Build map by given key
        cache[item[key]] = item  # list(item.values())
        item['_id'] = item[key]
        item['odata_type'] = odata_type_name
    return cache


def print_cache(cache):
    for key in cache:
        print('\t{}   \t{}\n'.format(key, cache[key]))


def describe_cache(cache, name):
    print('Cache \'{}\' has {} elements'.format(name, len(cache)))
    print('It takes up {} bytes of memory'.format(cache.__sizeof__()))
    print()


def write_caches(cache_list, file_path):
    f = open(file_path, 'w')
    f.write(json.dumps(cache_list))
    f.close()


def download_all_data(file_path):
    print("Starting Download from PurdueIo API")

    _term_ids = ["c543a529-fed4-4fd0-b185-bd403106b4ea"]
    _term_payload = {'$filter': 'TermId eq ' + _term_ids[0]}
    print(_term_payload)
    term_cache = request_cache(_term_payload, 'Terms', 'Term', 'TermId')
    describe_cache(term_cache, 'Terms')

    _subject_payload = {}
    subject_cache = request_cache(_subject_payload, 'Subjects', 'Subject', 'SubjectId')
    describe_cache(subject_cache, 'Subjects')

    _course_payload = {}
    course_cache = request_cache(_course_payload, 'Courses', 'Course', 'CourseId')
    describe_cache(course_cache, 'Course')

    _class_payload = {'$filter':
                      'TermId eq ' + _term_ids[0]}
    class_cache = request_cache(_class_payload, 'Classes', 'Class', 'ClassId')
    describe_cache(class_cache, 'Classes')

    _section_payload = {}
    section_cache = request_cache(_section_payload, 'Sections', 'Section', 'SectionId')
    describe_cache(section_cache, 'Sections')

    _meeting_payload = {}
    meeting_cache = request_cache(_meeting_payload, 'Meetings', 'Meeting', 'MeetingId')
    describe_cache(meeting_cache, 'Meetings')

    _instructors_payload = {}
    instructors_cache = request_cache(_instructors_payload,
                                      'Instructors',
                                      'Instructor',
                                      'InstructorId')
    describe_cache(instructors_cache, 'Intructors')

    _campus_payload = {}
    campus_cache = request_cache(_campus_payload, 'Campuses', 'Campus', 'CampusId')
    describe_cache(campus_cache, 'Campus')

    _building_payload = {}
    building_cache = request_cache(_building_payload,
                                   'Buildings',
                                   'Building',
                                   'BuildingId')
    describe_cache(building_cache, 'Buildings')

    _room_payload = {}
    room_cache = request_cache(_room_payload, 'Rooms', 'Room', 'RoomId')
    describe_cache(room_cache, 'Rooms')

    caches = dict()
    caches.update(term_cache)
    caches.update(subject_cache)
    caches.update(course_cache)
    caches.update(class_cache)
    caches.update(section_cache)
    caches.update(meeting_cache)
    caches.update(instructors_cache)
    caches.update(campus_cache)
    caches.update(building_cache)
    caches.update(room_cache)

    sum = 0
    for key in caches:
        sum += caches[key].__sizeof__()

    print('Altogether, we are using {} bytes of memory'.format(sum))

    write_caches(caches, file_path)

    print("End")


download_all_data("CourseInfo.json")

import requests
import json


def make_url(path=''):
    return 'http://api.purdue.io/odata/' + path


def send_request(payload, path=''):
    resp = requests.get(make_url(path), params=payload)
    print(resp)
    if resp.status_code != 200:
        raise "Failed to get API Information"
    return resp


def request_cache(payload, odata_type, key):
    resp = send_request(payload, odata_type)
    print('Request URL:{}'.format(resp.url))
    resp_list = resp.json()['value']
    print('We found {} entries matching the query'.format(len(resp_list)))
    cache = dict()
    for item in resp_list:  # Build map by given key
        cache[item[key]] = item  # list(item.values())  #
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

    _term_ids = ["c230a256-3f5d-4436-a8f8-020cf756b38d"]
    _term_payload = {'$filter': 'TermId eq ' + _term_ids[0]}
    print(_term_payload)
    term_cache = request_cache(_term_payload, 'Terms', 'TermId')
    describe_cache(term_cache, 'Terms')

    _subject_payload = {}
    subject_cache = request_cache(_subject_payload, 'Subjects', 'SubjectId')
    describe_cache(subject_cache, 'Subjects')

    _course_payload = {}
    course_cache = request_cache(_course_payload, 'Courses', 'CourseId')
    describe_cache(course_cache, 'Course')

    _class_payload = {'$filter':
                      'TermId eq c230a256-3f5d-4436-a8f8-020cf756b38d'}
    class_cache = request_cache(_class_payload, 'Classes', 'ClassId')
    describe_cache(class_cache, 'Classes')

    _section_payload = {}
    section_cache = request_cache(_section_payload, 'Sections', 'SectionId')
    describe_cache(section_cache, 'Sections')

    _meeting_payload = {}
    meeting_cache = request_cache(_meeting_payload, 'Meetings', 'MeetingId')
    describe_cache(meeting_cache, 'Meetings')

    _instructors_payload = {}
    instructors_cache = request_cache(_instructors_payload,
                                      'Instructors',
                                      'InstructorId')
    describe_cache(instructors_cache, 'Intructors')

    _campus_payload = {}
    campus_cache = request_cache(_campus_payload, 'Campuses', 'CampusId')
    describe_cache(campus_cache, 'Campus')

    _building_payload = {}
    building_cache = request_cache(_building_payload,
                                   'Buildings', 'BuildingId')
    describe_cache(building_cache, 'Buildings')

    _room_payload = {}
    room_cache = request_cache(_room_payload, 'Rooms', 'RoomId')
    describe_cache(room_cache, 'Rooms')

    caches = dict()
    caches['Terms'] = term_cache
    caches['Subjects'] = subject_cache
    caches['Courses'] = course_cache
    caches['Classes'] = class_cache
    caches['Sections'] = section_cache
    caches['Meetings'] = meeting_cache
    caches['Instructors'] = instructors_cache
    caches['Campuses'] = campus_cache
    caches['Buildings'] = building_cache
    caches['Rooms'] = room_cache

    sum = 0
    for key in caches:
        sum += caches[key].__sizeof__()

    print('Altogether, we are using {} bytes of memory'.format(sum))

    write_caches(caches, file_path)

    print("End")

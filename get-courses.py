import requests
print("Start")


def make_url(path=''):
    return 'http://api.purdue.io/odata/' + path


def send_request(payload, path=''):
    resp = requests.get(make_url(path), params=payload)
    if resp.status_code != 200:
        raise "Failed to get API Information"
    return resp


def request_cache(payload, odata_type, key):
    resp = send_request(payload, odata_type)
    print('Request URL:{}'.format(resp.url))
    print(resp)
    # print(resp.json())
    resp_list = dict(resp.json())['value']
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


_eg_payload = {'$filter': 'contains(Title, \'Algebra \')',
               '$select': 'Title,Number,Classes'}

_term_payload = {}
term_cache = request_cache(_term_payload, 'Terms', 'TermId')
describe_cache(term_cache, 'Terms')

_subject_payload = {}
subject_cache = request_cache(_subject_payload, 'Subjects', 'SubjectId')
describe_cache(subject_cache, 'Subjects')

_course_payload = {}
course_cache = request_cache(_subject_payload, 'Courses', 'Title')
describe_cache(course_cache, 'Course')


_class_payload = {}
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
building_cache = request_cache(_building_payload, 'Buildings', 'BuildingId')
describe_cache(building_cache, 'Buildings')


_room_payload = {}
room_cache = request_cache(_room_payload, 'Rooms', 'RoomId')
describe_cache(room_cache, 'Rooms')


caches = [term_cache, subject_cache, course_cache, class_cache, section_cache,
          meeting_cache, instructors_cache, campus_cache, building_cache,
          room_cache]

sum = 0
for cache in caches:
    sum += cache.__sizeof__()

print('Altogether, we are using {} bytes of memory'.format(sum))

# A course-name is a list of 2 strings
# Eg: ['cs', '39000']

# A course-times is a list of section-lists
# A section-list is a list of time values

# getCourseTimes : Course (CS39000) -> A list of a list of times ()

print("End")

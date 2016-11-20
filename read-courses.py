import json
print("Start")


def getCaches(file_path):
    f = open(file_path, 'r')
    text = f.read()
    f.close()
    return json.loads(text)


print("Getting caches....")
caches = getCaches('CourseInfo.json')
print("Done!")


print("{} bytes read from file.".format(caches.__sizeof__()))


subject_cache = caches['Subjects']
course_cache = caches['Courses']


def getSubject(abbrev, subjects=caches['Subjects']):
    if abbrev in subjects:
        return subjects[abbrev]
    else:
        raise "Subject does not exists :{}".format(abbrev)


course_lookup_cache = dict()
for subjectId in subject_cache:
    abbrev = subject_cache[subjectId]['Abbreviation']
    course_lookup_cache[abbrev] = dict()
    # print('{}\t->\t{}'.format(subjectId, abbrev))


for courseId in course_cache:
    course = course_cache[courseId]
    number = course['Number']
    subjectId = course['SubjectId']
    abbrev = subject_cache[subjectId]['Abbreviation']
    course_lookup_cache[abbrev][number] = courseId
    # print('{}\t->\t{}\t{}'.format(number, abbrev, course['Title']))


def getCourseId(dept, number):
    if dept not in course_lookup_cache:
        raise "Department given is invalid"
    if number not in course_lookup_cache[dept]:
        raise "Course not found in deptartment"
    return course_lookup_cache[dept][number]


def getCourseObject(dept, number):
    return course_cache[getCourseId(dept, number)]


print("End")

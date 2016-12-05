from cloudant.client import Cloudant
import json

# HIDDEN FROM GITHUB. GET YOUR OWN KEY FROM BLUEMIX
api_url = 'https://8f130e0a-0c4f-41f3-abdd-716a84018df8-bluemix' \
          ':8bf2a56a17024e594f342b7c5870b90bb1e669260baecb81462' \
          '85732fdf2ae6f@8f130e0a-0c4f-41f3-abdd-716a84018df8-' \
          'bluemix.cloudant.com'
api_user = '8f130e0a-0c4f-41f3-abdd-716a84018df8-bluemix'
api_pass = '8bf2a56a17024e594f342b7c5870b90bb1e669260baecb814628' \
           '5732fdf2ae6f'


def bulk_upload(cache, database, messageSize=1500):
    i = 1
    conflicts = 0
    size = len(cache.items())
    load = list()
    print("Done\tAmount\tConflicts")
    for item_id, item_json in cache.items():
        if i % messageSize == 0:
            print("{:.1f}%\t{}\t{}".format(100 * i / size, i, conflicts))
            rts = database.bulk_docs(load)
            for rt in rts:
                if 'error' in rt.keys():
                    if rt['error'] == 'conflict':
                        conflicts = conflicts + 1
                    else:
                        print('{} Failed with error: {}'
                              .format(rt['id'], rt['error']))
            load = list()
        load.append(item_json)
        i = i + 1

    # Cleanup last bulk upload
    if len(load) > 0:
        print("100%\t{}".format(size))
        rts = database.bulk_docs(load)
        for rt in rts:
            if 'error' in rt.keys():
                if rt['error'] == 'conflict':
                    conflicts = conflicts + 1
                else:
                    print('{} Failed with error: {}'
                          .format(rt['id'], rt['error']))

    if conflicts > 0:
        print("{} conflicts occured".format(conflicts))


def query_from_db(odata_id):
    client = Cloudant(api_user, api_pass, url=api_url)
    print("Quering all meeting times")

    # Connect to the server
    client.connect()

    # Perform client tasks...
    session = client.session()
    print('Username: {0}'.format(session['userCtx']['name']))
    print('Databases: {0}'.format(client.all_dbs()))

    courses_db = client['testing_db']

    if odata_id not in courses_db:
        out = None
    else:
        out = courses_db[odata_id]

    client.disconnect()
    return out


def __make_query_table__(subject_cache, course_cache):
    query_table = dict()
    for subject_id in subject_cache:
        abbrev = subject_cache[subject_id]['Abbreviation']
        query_table[abbrev] = dict()
        query_table[abbrev]['_id'] = abbrev
        query_table[abbrev]['dict'] = dict()

    for course_id in course_cache:
        course = course_cache[course_id]
        number = course['Number']
        subject_id = course['SubjectId']
        abbrev = subject_cache[subject_id]['Abbreviation']
        subject_dict = query_table[abbrev]['dict']
        if number not in subject_dict:
            subject_dict[number] = list()
        subject_dict[number].append(course_id)
        query_table[abbrev]['dict'] = subject_dict
    return query_table


def __make_lookup_table__(cache, odata_lookup_type):
    lookup_table = dict()
    for odata_id, entry in cache.items():
        lookup_id = entry[odata_lookup_type]
        if lookup_id not in lookup_table:
            lookup_table[lookup_id] = dict()
            lookup_table[lookup_id]['_id'] = lookup_id
            lookup_table[lookup_id]['list'] = list()
        lookup_table[lookup_id]['list'].append(odata_id)
    return lookup_table


# Writes lookup tables to the database
def write_lookup_tables():
    client = Cloudant(api_user, api_pass, url=api_url)
    # or using url
    # client = Cloudant(USERNAME, PASSWORD, url='https://acct.cloudant.com')

    # Connect to the server
    client.connect()

    # Perform client tasks...
    session = client.session()
    print('Username: {0}'.format(session['userCtx']['name']))
    print('Databases: {0}'.format(client.all_dbs()))

    file_path = "CourseInfo.json"
    f = open(file_path, 'r')
    text = f.read()
    f.close()
    caches = json.loads(text)

    query_table_db = client['query_table']
    query_table = __make_query_table__(caches['Subjects'], caches['Courses'])
    bulk_upload(query_table, query_table_db)

    api_class_lookup_table_db = client['api_class_lookup_table']
    api_class_lookup_table = \
        __make_lookup_table__(caches['Classes'], 'CourseId')
    bulk_upload(api_class_lookup_table, api_class_lookup_table_db)

    section_lookup_table_db = client['section_lookup_table']
    section_lookup_table = \
        __make_lookup_table__(caches['Sections'], 'ClassId')
    bulk_upload(section_lookup_table, section_lookup_table_db)

    meeting_lookup_table_db = client['meeting_lookup_table']
    meeting_lookup_table = \
        __make_lookup_table__(caches['Meetings'], 'SectionId')
    bulk_upload(meeting_lookup_table, meeting_lookup_table_db)

    # Disconnect from the server
    client.disconnect()


# Writes all courses to the database
def write_all_to_db():
    client = Cloudant(api_user, api_pass, url=api_url)
    # or using url
    # client = Cloudant(USERNAME, PASSWORD, url='https://acct.cloudant.com')

    # Connect to the server
    client.connect()

    # Perform client tasks...
    session = client.session()
    print('Username: {0}'.format(session['userCtx']['name']))
    print('Databases: {0}'.format(client.all_dbs()))

    courses_db = client['purdue_courses']

    file_path = "CourseInfo.json"
    f = open(file_path, 'r')
    text = f.read()
    f.close()
    caches = json.loads(text)

    bulk_upload(caches, courses_db)

    # Disconnect from the server
    client.disconnect()


# write_lookup_tables()
# write_all_to_db()

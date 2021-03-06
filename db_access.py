from cloudant.adapters import Replay429Adapter
from cloudant.client import Cloudant
from cloudant.result import Result
import json
import logging
from time_profiler import benchmark


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


def bulk_update(cache, database, messageSize=1500):
    rev_dict = dict()
    results = Result(database.all_docs, page_size=5000)
    with benchmark("Building id to rev dictionary"):

        i = 0
        size = len(cache)
        conflicts = 0

        for result in results:
            rev_dict[result['id']] = result['value']['rev']

            if len(rev_dict) >= messageSize:
                i += len(rev_dict)
                load = list()
                for item_id, item_rev in rev_dict.items():
                    item_json = cache[item_id]
                    item_json['_rev'] = item_rev
                    load.append(item_json)

                print("{:.1f}%\t{}\t{}".format(100 * i / size, i, conflicts))
                rts = database.bulk_docs(load)
                for rt in rts:
                    if 'error' in rt.keys():
                        if rt['error'] == 'conflict':
                            conflicts = conflicts + 1
                        else:
                            print('{} failed with error: {}'
                                  .format(rt['id'], rt['error']))

                rev_dict = dict()

        if len(rev_dict) > 0:
            load = list()
            for item_id, item_rev in rev_dict.items():
                item_json = cache[item_id]
                item_json['_rev'] = item_rev
                load.append(item_json)

            print("100%\t{}\t".format(size, conflicts))
            rts = database.bulk_docs(load)
            for rt in rts:
                if 'error' in rt.keys():
                    if rt['error'] == 'conflict':
                        conflicts = conflicts + 1
                    else:
                        print('{} failed with error: {}'
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
    adapter = Replay429Adapter(200, 0.25)
    client = Cloudant(api_user, api_pass, url=api_url, adapter=adapter)
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
    deep_caches = json.loads(text)

    query_table_db = client['query_table']
    query_table = __make_query_table__(deep_caches['Subjects'],
                                       deep_caches['Courses'])
    bulk_upload(query_table, query_table_db)

    api_class_lookup_table_db = client['api_class_lookup_table']
    api_class_lookup_table = \
        __make_lookup_table__(deep_caches['Classes'], 'CourseId')
    bulk_upload(api_class_lookup_table, api_class_lookup_table_db)

    section_lookup_table_db = client['section_lookup_table']
    section_lookup_table = \
        __make_lookup_table__(deep_caches['Sections'], 'ClassId')
    bulk_upload(section_lookup_table, section_lookup_table_db)

    meeting_lookup_table_db = client['meeting_lookup_table']
    meeting_lookup_table = \
        __make_lookup_table__(deep_caches['Meetings'], 'SectionId')
    bulk_upload(meeting_lookup_table, meeting_lookup_table_db)

    # Disconnect from the server
    client.disconnect()


# Writes lookup tables to the database
def update_lookup_tables():
    adapter = Replay429Adapter(200, 0.25)
    client = Cloudant(api_user, api_pass, url=api_url, adapter=adapter)
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
    deep_caches = json.loads(text)

    query_table_db = client['query_table']
    query_table = __make_query_table__(deep_caches['Subjects'],
                                       deep_caches['Courses'])
    bulk_update(query_table, query_table_db)

    api_class_lookup_table_db = client['api_class_lookup_table']
    api_class_lookup_table = \
        __make_lookup_table__(deep_caches['Classes'], 'CourseId')
    bulk_update(api_class_lookup_table, api_class_lookup_table_db)

    section_lookup_table_db = client['section_lookup_table']
    section_lookup_table = \
        __make_lookup_table__(deep_caches['Sections'], 'ClassId')
    bulk_update(section_lookup_table, section_lookup_table_db)

    meeting_lookup_table_db = client['meeting_lookup_table']
    meeting_lookup_table = \
        __make_lookup_table__(deep_caches['Meetings'], 'SectionId')
    bulk_update(meeting_lookup_table, meeting_lookup_table_db)

    # Disconnect from the server
    client.disconnect()


# Writes all courses to the database
def write_all_to_db():
    adapter = Replay429Adapter(200, 0.25)
    client = Cloudant(api_user, api_pass, url=api_url, adapter=adapter)
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
    deep_caches = json.loads(text)

    cache = dict()
    for cache_type, cache in deep_caches.items():
        cache.update(cache)

    bulk_upload(cache, courses_db)

    # Disconnect from the server
    client.disconnect()


# Writes all courses to the database
def update_all_to_db():
    adapter = Replay429Adapter(200, 0.25)
    client = Cloudant(api_user, api_pass, url=api_url, adapter=adapter)
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
    deep_caches = json.loads(text)

    cache = dict()
    for cache_type, cache in deep_caches.items():
        cache.update(cache)

    bulk_update(cache, courses_db)

    # Disconnect from the server
    client.disconnect()


logging.basicConfig(level=logging.INFO)
write_lookup_tables()
update_lookup_tables()
# write_all_to_db()
# update_all_to_db()

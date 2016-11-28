from cloudant.client import Cloudant
import json

# HIDDEN FROM GITHUB. GET YOUR OWN KEY FROM BLUEMIX
api_url  = 'https://8f130e0a-0c4f-41f3-abdd-716a84018df8-bluemix:8bf2a56a17024e594f342b7c5870b90bb1e669260baecb8146285732fdf2ae6f@8f130e0a-0c4f-41f3-abdd-716a84018df8-bluemix.cloudant.com'
api_user = '8f130e0a-0c4f-41f3-abdd-716a84018df8-bluemix'
api_pass = '8bf2a56a17024e594f342b7c5870b90bb1e669260baecb8146285732fdf2ae6f'


def queryFromDB(odata_id):
    client = Cloudant(api_user, api_pass, url=api_url)
    print("Quering all meeting times")
    client.disconnect()

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


queryFromDB('8bee1343-3e01-42e0-bcbb-410a3c24bd77')


def writeAllToDB():
    client = Cloudant(api_user, api_pass, url=api_url)
    # or using url
    # client = Cloudant(USERNAME, PASSWORD, url='https://acct.cloudant.com')

    # Connect to the server
    client.connect()

    # Perform client tasks...
    session = client.session()
    print('Username: {0}'.format(session['userCtx']['name']))
    print('Databases: {0}'.format(client.all_dbs()))

    courses_db = client['testing_db']

    file_path = "CourseInfo.json"
    f = open(file_path, 'r')
    text = f.read()
    f.close()
    caches = json.loads(text)

    messageSize = 100
    for cache_type, cache in caches.items():
        print("Uploading {}...".format(cache_type))
        i = 1
        size = len(cache.items())
        load = list()
        for item_id, item_json in cache.items():
            if i % messageSize == 0:
                print("{:.1f}%\t{}".format(100 * i / size, i))
                rts = courses_db.bulk_docs(load)
                for rt in rts:
                    if 'error' in rt.keys():
                        print('{} Failed with error: {}'.format(rt['id'], rt['error']))
                load = list()
            # print("id:{}\n\tjson:{}".format(item_id, item_json))
            load.append(item_json)
            # new_document = courses_db.create_document(item_json)
            # if not new_document.exists():
            #     print("{} failed to upload".format(item_id))
            i = i + 1

    # Disconnect from the server
    client.disconnect()

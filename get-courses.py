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
    print(resp.json())
    resp_list = dict(resp.json())['value']
    print('We found {} entries matching the query'.format(len(resp_list)))
    cache = dict()
    for item in resp_list:  # Build map by given key
        cache[item[key]] = list(item.values())
    return cache


_eg_payload = {'$filter': 'contains(Title, \'Algebra \')',
               '$select': 'Title,Number,Classes'}

_term_payload = {'$select': 'Name,StartDate,EndDate,Classes'}
term_cache = request_cache(_term_payload, 'Terms', 'Name')

for key in term_cache:
    print('\t{}   \t{}'.format(key, term_cache[key]))

print("End")

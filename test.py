import json

import requests

res = requests.get('http://192.168.225.198:8080/readpinall')
string = ''
if res.status_code == 200:
    data_dict = json.loads(res.text)
    print(data_dict)
else:
    string = f'status code = {res.status_code}'

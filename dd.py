import requests
import json
import os

url = "https://api.logz.io/v1/search"
headers = {
    'x-user-token': os.environ['LOGZ_TOKEN'],
    'content-type': "application/json",
    'cache-control': "no-cache"
    }

payload_stats = "{\n\t\"size\": 0,\n\t\"query\": {\n\t\t\"bool\": {\n\t\t\t\"must\": [{\n\t\t\t\t\"range\": {\n\t\t\t\t\t\"@timestamp\": {\n\t\t\t\t\t\t\"gte\": \"now-1h\",\n\t\t\t\t\t\t\"lte\": \"now\"\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}]\n\t\t}\n\t},\n\t\"aggs\": {\n            \"extendedstats_cpu\": {\"extended_stats\" : { \"field\" :\"cpu__load__avg1\" } }\n\t}\n}"
response_stats = requests.request("POST", url, data=payload_stats, headers=headers)
print(response_stats.text)
json_response = json.loads(response_stats.text)
average=json_response['aggregations']['extendedstats_cpu']['avg']
stddev=json_response['aggregations']['extendedstats_cpu']['std_deviation']
stddev_multiplier=3
positive_outlier=average + (stddev * stddev_multiplier)
negative_outlier=average - (stddev * stddev_multiplier)
print('Positive outlier = ' + str(positive_outlier))
print('Negative outlier = ' + str(negative_outlier))


payload_query = "{  \n   \"size\":10,\n    \"_source\": [\"@timestamp\",\"cpu__load__avg1\" ],\n   \"query\":{  \n      \"bool\":{  \n         \"must\":[  \n            {  \n               \"query_string\":{  \n                  \"query\":\"cpu__load__avg1:>" + str(positive_outlier) + " OR cpu__load__avg1:<" + str(negative_outlier) + "\",\n                  \"analyze_wildcard\":true\n               }\n            },\n            {  \n               \"range\":{  \n                  \"@timestamp\":{  \n                     \"gte\":\"now-1h\",\n                     \"lte\":\"now\"\n                  }\n               }\n            }\n         ]\n      }\n   }\n}"
print(payload_query)
response_query = requests.request("POST", url, data=payload_query, headers=headers)
print(response_query.text)



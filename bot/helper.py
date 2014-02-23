import json

def loadJson(filename):
    json_file = open(filename)
    json_data = json_file.read()
    data = json.loads(json_data)
    return data
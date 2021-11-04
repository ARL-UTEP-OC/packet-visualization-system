import json

def parser():
    jsonFile = open(r'C:\Users\timmy\PycharmProjects\packet-visualize\packetvisualization\backend_components\sampleJson.json')
    jsonData = json.load(jsonFile)
    properties = list()
    for x in jsonData[0]['_source']['layers']:
        for y in jsonData[0]['_source']['layers'][x]:
            # keys = x.keys()
            print(y)
            properties.append(y)
            # values = x.values()
            # print(values)
    return properties

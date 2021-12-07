import json
import traceback


def parser(jsonString: list):

    properties = list()
    pktIds = list()
    propMap = dict({})

    gotFields = False
    try:
        for w in jsonString:
            print(w['_id'])
            pktIds.append(w['_id'])
            if gotFields is False:
                for x in w['_source']['layers']:
                    for y in w['_source']['layers'][x]:
                        # print(y)
                        propMap[f"{y}"] = [f"_source.layers.{x}.{y}", "False", "True"]
                        properties.append(f"_source.layers.{x}.{y}")
                        gotFields = True
                        value = ""
                        for z in w['_source']['layers'][x][y]:
                            value = value + z
                        if value == "0" or value == "" or value == "0.000000000" or value == "0.000000000":
                            value = "null"
                            propMap[f"{y}"][2] = "False"
                        else:
                            propMap[f"{y}"][1] = "True"

                        # print(value)
            for x in w['_source']['layers']:
                for y in w['_source']['layers'][x]:
                    if y not in propMap:
                        propMap[f"{y}"] = [f"_source.layers.{x}.{y}", "False", "True"]
                    value = ""
                    for z in w['_source']['layers'][x][y]:
                        value = value + z
                    if value == "0" or value == "" or value == "0.000000000" or value == "0.000000000":
                        value = "null"
                        propMap[f"{y}"][2] = "False"
                    else:
                        # print(y)
                        # print(value)

                        propMap[f"{y}"][1] = "True"

        print(propMap)


    except Exception:
        print(traceback.format_exc())

    items = [properties, pktIds, propMap]

    return items

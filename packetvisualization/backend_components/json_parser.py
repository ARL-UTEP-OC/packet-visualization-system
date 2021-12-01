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
                        print(y)
                        # print((x.get(y)))
                        propMap[f"{y}"] = [f"_source.layers.{x}.{y}", False]
                        properties.append(f"_source.layers.{x}.{y}")
                        gotFields = True
                        value = ""
                        for z in w['_source']['layers'][x][y]:
                            value = value + z
                        if value == "0" or value == "" or value == "0.000000000" or value == "0.000000000":
                            value = "null"
                        else:
                            propMap[f"{y}"].remove(False)
                            propMap[f"{y}"].append(True)
                        print(value)

        print(propMap)


    except Exception:
        print(traceback.format_exc())

    items = [properties, pktIds, propMap]

    return items

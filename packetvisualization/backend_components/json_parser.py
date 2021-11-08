import json
import traceback


def parser(jsonString: list):

    properties = list()
    pktIds = list()

    gotFields = False
    try:
        for w in jsonString:
            print(w['_id'])
            pktIds.append(w['_id'])
            if gotFields is False:
                for x in w['_source']['layers']:
                    for y in w['_source']['layers'][x]:
                        print(y)
                        properties.append(f"_source.layers.{x}.{y}")
                        gotFields = True

    except Exception:
        print(traceback.format_exc())

    items = [properties, pktIds]

    return items

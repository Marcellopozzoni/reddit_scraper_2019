import sys
import json

with open("PersonalFinanceCanada.json", errors='ignore') as json_data:
    formatted_json = json.dumps(json.load(json_data, strict=False), sort_keys=True, indent=4)

    with open('Readable.txt', 'w') as outfile:
        outfile.write(formatted_json)

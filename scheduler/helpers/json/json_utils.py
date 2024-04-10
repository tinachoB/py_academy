import json
import jsonschema
from os import path


def validate(json_file):
    json_data = {}
    try:
        if path.exists(json_file):
            with open(json_file, "r") as task:
                json_data = json.load(task)
        else:
            json_data = json.loads(json_file)
        # Validate JSON format and syntax
        _validate_format(json_data)
    except ValueError as error:
        print(f"Unable to load JSON file. Error: {error}")
    except jsonschema.ValidationError as validation_error:
        print(f"The JSON file passed by argument does not match with the expected schema. Error: {validation_error}")

    return json_data


def _validate_format(json_data):
    json_schema = {}
    json_action = json_data["verb"]
    if json_action == "start":
        json_schema = json.load(open("helpers/json/schemas/start.schema"))
    elif json_action == "write":
        json_schema = json.load(open("helpers/json/schemas/write.schema"))
    else:
        # Stop
        json_schema = json.load(open("helpers/json/schemas/stop.schema"))

    jsonschema.validate(instance=json_data, schema=json_schema)


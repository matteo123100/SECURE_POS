import json
import logging
import os
import utility
import jsonschema


# see : https://linkml.io/linkml/_modules/linkml/validator/plugins/jsonschema_validation_plugin.html


def validate_json(json_data: dict, schema: dict) -> bool:
    """
    Validates a json object against a given json schema.
    :param json_data: json object
    :param schema: json schema
    :return: False if any error occurs, otherwise True
    see : https://python-jsonschema.readthedocs.io/en/latest/validate/
    """
    try:
        jsonschema.validate(instance=json_data, schema=schema)
    except jsonschema.exceptions.ValidationError as ex:
        logging.error(ex)
        return False
    return True


def validate_json_data_file(json_data: dict, schema_filename: str) -> bool:
    """
    Validate a json object against a json schema present in the given filename.
    :param json_data: json object
    :param schema_filename: path to the json schema file !!! <relative to the data folder>
    :return: False if any error occurs, otherwise True
    """
    schema_path = os.path.join(utility.data_folder, schema_filename)
    with open(schema_path, "r", encoding="UTF-8") as file:
        json_schema = json.load(file)
    return validate_json(json_data, json_schema)


def validate_json_file_file(json_filename: str, schema_filename: str) -> bool:
    """
    Validate a json file against a json schema in a file.
    :param json_filename: path to the json file !!! <relative to the data folder>
    :param schema_filename: path to the json schema file !!! <relative to the data folder>
    :return: False if any error occurs, otherwise True
    """
    json_path = os.path.join(utility.data_folder, json_filename)
    with open(json_path, "r", encoding="UTF-8") as jFile:
        json_data = json.load(jFile)
    with open(json_path, "r", encoding="UTF-8") as jSchema:
        json_schema = json.load(jSchema)
    return validate_json(json_data, json_schema)

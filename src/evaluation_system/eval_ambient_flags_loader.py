"""
    Module for testing state configuration acquisition
"""
import json
from utility.json_validation import validate_json_file_file
from utility import data_folder

TESTING_CONFIG_PATH_RELATIVE = "evaluation_system/configs/eval_ambient_flags.json"
TESTING_CONFIG_SCHEMA_PATH_RELATIVE = "evaluation_system/schemas/eval_ambient_flags_schema.json"
TESTING_VALIDITY = \
    validate_json_file_file(TESTING_CONFIG_PATH_RELATIVE, TESTING_CONFIG_SCHEMA_PATH_RELATIVE)

testing_conf_location = f'{data_folder}/{TESTING_CONFIG_PATH_RELATIVE}'

with open(testing_conf_location, "r", encoding="UTF-8") as jsonTestingFile:
    testing_config_content = json.load(jsonTestingFile)

DB_NAME = testing_config_content["db_name"]
DEBUGGING = testing_config_content["testing"] == "True"
TIMING = testing_config_content["timing"] == "True"
DELETE_DB_ON_LOAD = testing_config_content["delete_db_on_load"] == "True"
PRINT_LABELS_DF = testing_config_content["print_labels"] == "True"

print(f'DB_NAME : {DB_NAME}')
print(f'DEBUGGING status : {DEBUGGING}')
print(f'TIMING status : {TIMING}')
print(f'DELETE_DB_ON_LOAD status : {DELETE_DB_ON_LOAD}')
print(f'PRINT_LABELS_DF status : {PRINT_LABELS_DF}')

"""
    Testing Module for EvaluationSystem
"""
import logging
import time
import sys
import json
import os
from math import ceil
import jsonschema
import requests


TARGET_IP = "http://127.0.0.1:8001"
SECOND_IP = "http://192.168.142.201:8001"

project_root = os.path.realpath(__file__ + "/../../..")
data_folder = os.path.join(project_root, "data")

TEST_SYMBOL = "->"


def validate_json(json_data: dict, schema: dict) -> bool:
    """
        Quick json validation implementation
    :param json_data: dictionary of data
    :param schema: json schema to validate against
    :return:
    """
    try:
        jsonschema.validate(instance=json_data, schema=schema)
    except jsonschema.exceptions.ValidationError as ex:
        logging.error(ex)
        return False
    return True


def send_label(label_json):
    """
        Quick request->POST call
    :param label_json: json data
    :return:
    """
    response = requests.post(TARGET_IP, json=label_json, timeout=15)
    if not response.ok:
        logging.error("Failed to send label:\n%s", label_json)


def goodbye():
    """
        Goodbye function
    :return:
    """
    print(f'{TEST_SYMBOL}goodbye')
    sys.exit(0)


if __name__ == "__main__":
    config_path = f'{data_folder}/evaluation_system/configs/eval_config.json'
    config_schema_path = f'{data_folder}/evaluation_system/schemas/eval_config_schema.json'
    with open(config_path, "r", encoding="UTF-8") as jsonFile:
        ev_config = json.load(jsonFile)
    with open(config_path, "r", encoding="UTF-8") as jsonFileSchema:
        ev_config_schema = json.load(jsonFileSchema)
    GOOD_CONF = validate_json(ev_config, ev_config_schema)
    if not GOOD_CONF:
        logging.error("bad evaluation schema")
        goodbye()

    LABEL_PATH_SCHEMA_REL = "evaluation_system/schemas/eval_label_input_schema.json"

    test_label = {
        "session_id": "1",
        "source": "expert",
        "value": "normal"
    }
    with open(f'{data_folder}/{LABEL_PATH_SCHEMA_REL}', "r", encoding="UTF-8") as label_file:
        label_schema = json.load(label_file)
    GOOD_LABEL = validate_json(test_label, label_schema)
    print(GOOD_LABEL)
    #  send_label(test_label)

    #  sys.exit(0)

    min_labels_step = ev_config["min_labels_opinionated"]
    max_conflict = ev_config["max_conflicting_labels_threshold"]
    max_cons_conflict = ev_config["max_consecutive_conflicting_labels_threshold"]

    # delay expressed in seconds, precision is up to microseconds.
    # see: https://docs.python.org/3/library/time.html#time.sleep
    DELAY = 10000/1000000
    PRINT_DELAY = 10000/1000000
    OVERLOAD_TIMES = 1

    print(f'starting test, delay-per-packet : {DELAY} ;'
          f' delay-per-batch : {PRINT_DELAY} .')
    print(f'min_labels:{min_labels_step}; '
          f'max_errors:{max_conflict}; '
          f'max_cons_err:{max_cons_conflict} ')

    gen_step = max(min_labels_step, max_conflict, max_cons_conflict)
    err_range = max(max_conflict, max_cons_conflict, ceil(gen_step/2))

    CORRECT = "attack"
    MISTAKE = "normal"
    print(f'{TEST_SYMBOL} begin tests errors')
    #  err_range+1 covers from 0 to max_errors errors, so, just in case, we cover some more
    for k in range(0, OVERLOAD_TIMES, 1):
        for i in range(0, err_range+2, 1):
            for j in range(0, gen_step):
                FIRST = CORRECT
                SECOND = MISTAKE if (j < i) else CORRECT
                label = {
                    "session_id": str(j),
                    "source": "expert",
                    "value": FIRST
                }
                send_label(label)
                time.sleep(DELAY)
                label = {
                    "session_id": str(j),
                    "source": "classifier",
                    "value": SECOND
                }
                send_label(label)
                time.sleep(DELAY)
            print(f'{TEST_SYMBOL} done iteration : {i} .')
    print(f'{TEST_SYMBOL} end of test errors')

    goodbye()
    # eof

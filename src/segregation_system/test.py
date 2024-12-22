import json
import time

import requests
import os
from utility import project_root

def test_send_prepared_session():
    """
    Test the sending of a json file with the structure of a prepared session.
    """
    url = "http://192.168.97.250:5003/"

    # iterate through the json files in the directory lore and send them to the server
    for filename in os.listdir(os.path.join(project_root, 'src', 'prepare_system', 'lore')):
        if filename == "data1.json":
            continue

        if filename.endswith(".json"):
            json_filename = os.path.join(project_root, 'src', 'prepare_system', 'lore', filename)

            with open(json_filename, 'r') as file:
                json_data = json.load(file)

            response = requests.post(url, json=json_data)
            print(response.text)
            time.sleep(3)


if __name__ == "__main__":
    test_send_prepared_session()
    print("Test passed")
import os
import csv
import time
import json
import threading
import requests
from comms import ServerREST
from comms.json_transfer_api import ReceiveJsonApi
from utility import data_folder

SCENARIO_JSON = os.path.join(data_folder, "client_side/scenario.json")
DATA_FILES = [
    "localizationSys.csv",
    "networkMonitor.csv",
    "labels.csv",
    "transactionCloud.csv"
]

RAW_DATA_FOLDER = os.path.join(data_folder, "client_side/raw_data/")
CLEAN_DATA_FOLDER = os.path.join(data_folder, "client_side/clean_data_for_testing/")


class ClientSimulator:
    def __init__(self):
        with open(SCENARIO_JSON, "r", encoding="UTF-8") as scenario_file:
            scenario = json.load(scenario_file)

        self.scenario_type = scenario["type"]
        self.ingestion_system_url = scenario['ingestion_system_url']
        self.repetitions = scenario["repetitions"]
        self.required_rows = scenario["required_rows"]
        self.testing = scenario["testing"]

        if self.testing:
            self.end_of_test = False
            self.cv = threading.Condition()
            self.data = {
                "ingestion_system": 0,
                "segregation_system": 0,
                "development_system": 0,
                "production_system": 0,
                "evaluation_system": 0
            }

            flask_thread = threading.Thread(
                target=self.server_thread,
                args=(scenario['ip_address'], scenario['port'])
            )
            flask_thread.daemon = True
            flask_thread.start()

    def server_thread(self, ip_address, port):
        server = ServerREST()
        server.api.add_resource(
            ReceiveJsonApi,
            "/",
            resource_class_kwargs={
                'handler': self.receive_message
            }
        )
        print("set server handler")
        server.run(ip_address, port)

    def receive_message(self, received_json: dict):
        self.data[received_json["system"]] += received_json["time"]
        #  --- print(f'received message with json : {received_json}')
        if self.testing and received_json["end"]:
            #  --- print(f'received end : {received_json}')
            with self.cv:
                self.end_of_test = True
                self.cv.notify()
                print("done notify")
        #  --- print("done receive_message")

    def send_raw_data(self):
        datasets = []
        for csv_file_path in DATA_FILES:
            abs_path = os.path.join(RAW_DATA_FOLDER, csv_file_path)
            with open(abs_path, "r", encoding="UTF-8") as csv_file:
                csv_reader = csv.DictReader(csv_file)
                datasets.append([row for row in csv_reader])

        max_rows = max(len(dataset) for dataset in datasets)

        for i in range(max_rows):
            for dataset in datasets:
                if i < len(dataset):
                    try:
                        requests.post(self.ingestion_system_url, json=dataset[i])
                    except requests.exceptions.RequestException as ex:
                        print(ex)

    def test_development(self, csv_results_path):
        datasets = []
        for csv_file_path in DATA_FILES:
            abs_path = os.path.join(CLEAN_DATA_FOLDER, csv_file_path)
            with open(abs_path, "r", encoding="UTF-8") as csv_file:
                csv_reader = csv.DictReader(csv_file)
                datasets.append([row for row in csv_reader])

        max_row = len(datasets[0])
        for i in range(self.required_rows):
            for dataset in datasets:
                row = i % max_row
                rep = '-r' + str(i // max_row)
                json_to_send = dataset[row]
                # print(f'{json_to_send}')
                json_to_send['UUID'] = json_to_send['UUID'] + rep

                try:
                    requests.post(self.ingestion_system_url, json=json_to_send)
                except requests.exceptions.RequestException as ex:
                    print(ex)
            print(f'test_development : {i} of {self.required_rows}')

        # Wait before next iteration
        print("wait before next iteration")
        with self.cv:
            while not self.end_of_test:
                self.cv.wait()

            self.dump_data(csv_results_path)
            self.reset()

    def test_production(self, csv_results_path):
        datasets = []
        for csv_file_path in DATA_FILES:
            abs_path = os.path.join(CLEAN_DATA_FOLDER, csv_file_path)
            with open(abs_path, "r", encoding="UTF-8") as csv_file:
                csv_reader = csv.DictReader(csv_file)
                datasets.append([row for row in csv_reader])

        max_row = len(datasets[0])

        time_beginning = time.time_ns()
        time_returned = 0
        for i in range(self.required_rows):
            for dataset in datasets:
                row = i % max_row
                rep = '-r' + str(i // max_row)
                json_to_send = dataset[row]
                json_to_send['UUID'] = json_to_send['UUID'] + rep

                try:
                    requests.post(self.ingestion_system_url, json=json_to_send)
                except requests.exceptions.RequestException as ex:
                    print(ex)

            # Wait before next iteration
            with self.cv:
                while not self.end_of_test:
                    self.cv.wait()
                # time.sleep(10/1000)
                time_returned += time.time_ns() - time_beginning
                self.dump_data(csv_results_path)
                self.reset()
            print(f'test_production : {i} of {self.required_rows}')
        return time_returned

    def dump_data(self, csv_results_path):
        header = [
            "ingestion_system",
            "segregation_system",
            "development_system",
            "production_system",
            "evaluation_system"
        ]
        with open(csv_results_path, "a+", encoding="UTF-8") as csv_file:
            writer = csv.DictWriter(csv_file, header)
            writer.writerow(self.data)

    def reset(self):
        print("im gonna resetttttttt")
        self.end_of_test = False
        self.data = {
            "ingestion_system": 0,
            "segregation_system": 0,
            "development_system": 0,
            "production_system": 0,
            "evaluation_system": 0
        }

    def run(self):
        time_str = time.strftime("%d_%H_%M", time.localtime())
        file_name = "client_side/test_results/" \
                    f'{self.scenario_type}_' \
                    f'{self.repetitions}_reps_' \
                    f'{time_str}_results.csv'

        csv_results_path = os.path.join(data_folder, file_name)

        time_list = []
        for i in range(self.repetitions):
            if not self.testing:
                self.send_raw_data()

            elif self.scenario_type == "DEVELOPMENT":
                self.test_development(csv_results_path)

            else:  # self.scenario_type == "PRODUCTION"
                v = self.test_production(csv_results_path)
                time_list.append(v)
            print(f'test_{self.scenario_type} : iteration {i} of {self.repetitions}')
        time.sleep(3)
        time_file_name = "client_side/test_results/" \
                    f'TOTAL_'\
                    f'{self.scenario_type}_' \
                    f'{self.repetitions}_reps_' \
                    f'{time_str}_results.txt'
        tfn_path = os.path.join(data_folder, time_file_name)
        with open(tfn_path, 'w+') as trg_file:
            for a in time_list:
                trg_file.write(f'{a}\n')

1
"""
This module is responsible for orchestrating the segregation system.
It receives the prepared sessions, checks the risk class balancing and the feature coverage,
generates the learning sets and sends them to the development system.
It also starts the REST server to receive the prepared sessions from the preparation system.
"""
import random
import json
import multiprocessing
import os
import time
import requests
from db_sqlite3 import DatabaseController
from utility import data_folder, project_root
from segregation_system.ClassBalancing import CheckClassBalancing, ViewClassBalancing
from segregation_system.ClassBalancing import BalancingReport
from segregation_system.InputCoverage import CheckInputCoverage, ViewInputCoverage
from segregation_system.InputCoverage import CoverageReport
from segregation_system.PreparedSession import PreparedSessionController
from segregation_system.LearningSetsController import LearningSetsController
from segregation_system.CommunicationController import CommunicationController

# Define the paths of the configuration file, the json files, the sets file,
# the input file, the schema file and the URL of the development system
CONFIG_PATH = os.path.join(data_folder, 'segregation_system', 'config', 'segregation_config.json')
JSON_BALANCING_PATH = os.path.join(
    data_folder, 'segregation_system', 'outcomes', 'balancing_outcome.json'
)
JSON_COVERAGE_PATH = os.path.join(
    data_folder, 'segregation_system', 'outcomes', 'coverage_outcome.json'
)
SET_PATH = os.path.join(data_folder, 'segregation_system', 'sets', 'all_sets.json')
FILE_PATH = os.path.join(data_folder, 'segregation_system', 'input')
SCHEMA_PATH = os.path.join(
    data_folder, 'segregation_system', 'schemas', 'prepared_session_schema.json'
)
DATABASE_PATH = os.path.join(project_root, 'src', 'segregation_system', 'segregationDB.db')
# put it in the config file
URL = "http://192.168.97.2:5555/"


class SegregationSystemOrchestrator:
    """
    Class that orchestrates the segregation system. It receives the prepared sessions,
    checks the risk class balancing and the feature coverage, generates the
    learning sets and sends them to the development system.
    It also starts the REST server to receive the prepared sessions from the
    preparation system.
    """
    def __init__(self):
        """
        Constructor of the SegregationSystemOrchestrator class.
        It initializes the configuration object, the database controller,
        the prepared session controller and the REST server.
        """

        # Load the configuration object
        self.segregation_config = {}
        try:
            with open(CONFIG_PATH, 'r', encoding="UTF-8") as f:
                # Open the configuration file
                config = json.load(f)
        except FileNotFoundError:
            # If the configuration file is not found, print an error message
            print("ERROR> Configuration file not found")
        except json.JSONDecodeError:
            # If the configuration file is not a valid JSON file, print an error message
            print("ERROR> Error decoding JSON file")

        # Load the configuration parameters
        self.segregation_config["minimum_session_number"] = int(config["sessionNumber"])
        self.segregation_config["operation_mode"] = str(config["operationMode"])
        self.segregation_config["development_system_endpoint"] = str(
            config["developmentSystemEndpoint"]
        )
        self.segregation_config["check_server"] = str(
            config["checkServerEndpoint"]
        )

        # Initialize the database controller
        self.db = DatabaseController(DATABASE_PATH)

        # Initialize the prepared session controller
        self.sessions = PreparedSessionController()

        # Initialize the communication controller
        self.communication_controller = CommunicationController()

        # Initialize the server
        self.server = None

        # Initialize the timestamp variables
        self.timestamp_begin = None
        self.timestamp_end = None

    def receive(self, received_json: dict):
        """
        Method that receives the prepared sessions from the preparation system.
        It waits for the file to appear in the data folder
        and then stores the sessions in the database.
        :return: file path of the received file
        """

        with open(os.path.join(FILE_PATH, "prepared_sessions.json"), 'w', encoding='UTF-8') as f:
            json.dump(received_json, f, indent='\t')

        if self.segregation_config["operation_mode"] == "wait_sessions":
            to_process = 1
        else:
            to_process = 0

        if self.sessions.store(os.path.join(FILE_PATH, "prepared_sessions.json"), to_process):
            print("Sessions stored successfully")
        else:
            print("ERROR> Error storing sessions")

    def run(self, service_flag):
        """
        Method that starts the segregation process. It waits for the minimum
        number of sessions to be collected, then checks the risk class balancing
        and the feature coverage. If the balancing and coverage are approved,
        it generates the learning sets and sends them to the development system.
        """

        response = self.communication_controller.is_server_running()
        if response:
            print("Server already running...")
        else:
            # Start the REST server in a separate thread
            flask_thread = multiprocessing.Process(
                target=self.communication_controller.start_server,
                args=(SCHEMA_PATH, self.receive)
            )
            flask_thread.daemon = False
            flask_thread.start()

            # Check if the database file exists and delete it
            if os.path.exists(DATABASE_PATH):
                os.remove(DATABASE_PATH)

        # Initialize the class balancing check
        balancing_check = CheckClassBalancing()

        # Initialize the input coverage check
        coverage_check = CheckInputCoverage()

        # Create the table of prepared sessions in the database if
        # it does not exist
        create_table_query = """
                CREATE TABLE IF NOT EXISTS prepared_sessions (
                    uuid TEXT PRIMARY KEY,
                    label TEXT,
                    mean_abs_diff_ts REAL,
                    mean_abs_diff_am REAL,
                    median_long REAL,
                    median_lat REAL,
                    median_targetIP TEXT,
                    median_destIP TEXT,
                    to_process BOOLEAN
                );
                """
        self.db.create_table(create_table_query, [])

        # The system is in a loop until the learning sets are generated and sent
        # to the development system
        while True:
            # The system starts by waiting for the minimum number of sessions to be collected
            if self.segregation_config["operation_mode"] == "wait_sessions":
                # Receive the prepared sessions file from the preparation system and
                # store the sessions in the database
                # while the FILE_PATH directory does not contain any files
                if not os.listdir(FILE_PATH):
                    continue

                # Check if the minimum number of sessions has been collected
                to_collect = self.segregation_config["minimum_session_number"]
                collected = self.sessions.sessions_count()

                if collected < to_collect:
                    continue

                if service_flag:
                    self.timestamp_begin = time.time_ns()

                # Go to the class balancing check
                self.segregation_config["operation_mode"] = "check_balancing"

            # The system checks the risk class balancing by generating a plot of the risk classes
            # and prompting the user to approve the balancing. If the balancing is approved, the
            # system goes to the feature coverage check. If the balancing is not approved,
            # the system goes back to the wait sessions and the data analyst
            # modify the json file with the number of samples he needs.
            if self.segregation_config["operation_mode"] == "check_balancing":
                # Retrieve the labels of the prepared sessions from the database
                balancing_check.retrieve_labels()

                # Initialize the object to view the class balancing check and generate the plot
                balancing_check_view = ViewClassBalancing(balancing_check)
                balancing_check_view.show_plot()
                print("Generated plot for class balancing check...")

                # if we are in the testing phase, we generate a random outcome
                if service_flag:
                    approved = random.random() < 0.73

                    # if the balancing is approved, we generate a json file with the approved flag
                    # and no unbalanced classes
                    if approved:
                        data = {
                            "approved": approved,
                            "unbalanced_classes": {
                                "normal": 0,
                                "moderate": 0,
                                "high": 0
                            }
                        }

                        with open(JSON_BALANCING_PATH, "w", encoding="UTF-8") as json_file:
                            json.dump(data, json_file, indent=4)
                    else:
                        # if the balancing is not approved, we generate a json file with the approved flag
                        # and random number of samples required for the unbalanced classes
                        data = {
                            "approved": approved,
                            "unbalanced_classes": {
                                "normal": random.randint(0, 200),
                                "moderate": random.randint(0, 200),
                                "high": random.randint(0, 200)
                            }
                        }

                        with open(JSON_BALANCING_PATH, "w", encoding="UTF-8") as json_file:
                            json.dump(data, json_file, indent=4)

                    # we change the operation mode to generate the outcome of the balancing
                    self.segregation_config["operation_mode"] = "generate_balancing_outcome"
                else:
                    # if we are not in testing phase, the system is shut down and the data analyst
                    # needs to check the balancing before restarting the system
                    print(">>> Shutting down the system. Data Analyst can restart it after the balancing check.")
                    with open(CONFIG_PATH, "r", encoding="UTF-8") as json_file:
                        data = json.load(json_file)
                    data["operationMode"] = "generate_balancing_outcome"
                    with open(CONFIG_PATH, "w", encoding="UTF-8") as json_file:
                        json.dump(data, json_file, indent=4)
                    return False

            # The outcome of the balancing plot is checked to see if the balancing is approved.
            # If the balancing is approved, the system goes to the feature coverage check.
            # If the balancing is not approved, the system goes back to the wait sessions
            if self.segregation_config["operation_mode"] == "generate_balancing_outcome":
                # Initialize the object to check the balancing outcome
                balancing_report = BalancingReport()

                if balancing_report.approved:
                    self.segregation_config["operation_mode"] = "check_coverage"
                else:
                    # if we are in the testing phase, we send the timestamp to the client-side system
                    # to tell them that the system is shutting down, but for testing purposes
                    # we just return to the wait sessions
                    if service_flag:
                        self.timestamp_end = time.time_ns()
                        diff_time = self.timestamp_end - self.timestamp_begin
                        sending_data = {
                            "system": "segregation_system",
                            "time": diff_time,
                            "end": True
                        }
                        self.communication_controller.send_json(URL, sending_data)

                        # we update the prepared_sessions table to process the sessions again
                        query = """
                        UPDATE prepared_sessions SET to_process = 1;
                        """
                        self.db.update(query, [])

                        # we change the operation mode to wait sessions
                        self.segregation_config["operation_mode"] = "wait_sessions"
                    else:
                        # if we are not in testing phase, the system is shut down and the data analyst
                        # needs to wait for more samples before restarting the system
                        print("Shutting down the system. More samples needed.")
                        with open(CONFIG_PATH, "r", encoding="UTF-8") as json_file:
                            data = json.load(json_file)
                        data["operationMode"] = "wait_sessions"
                        with open(CONFIG_PATH, "w", encoding="UTF-8") as json_file:
                            json.dump(data, json_file, indent=4)

                        # we update the prepared_sessions table to process the sessions again
                        query = """
                        UPDATE prepared_sessions SET to_process = 1;
                        """
                        self.db.update(query, [])
                        return False

            # The system checks the feature coverage by generating a plot of the features.
            # If the coverage is approved by the data analyst the system generates the
            # learning sets and sends them to the development system.
            # If the coverage is not approved, the system goes back to the wait sessions
            # and the Data Analyst modifies the json file with some suggestions about the
            # features that are not well covered.
            if self.segregation_config["operation_mode"] == "check_coverage":
                # Retrieve the features of the prepared sessions from the database
                coverage_check.retrieve_features()

                # Initialize the object to view the input coverage check and generate the plot
                coverage_check_view = ViewInputCoverage(coverage_check)
                coverage_check_view.show_plot()

                # if we are in the testing phase, we generate a random outcome
                if service_flag:
                    approved = random.random() < 0.53

                    # if the coverage is approved, we generate a json file with the approved flag
                    # and no uncovered features suggestions
                    data = {
                        "approved": approved,
                        "uncovered_features_suggestions": {
                            "median_longitude": "",
                            "median_latitude": "",
                            "mean_diff_time": "",
                            "mean_diff_amount": "",
                            "median_targetIP": "",
                            "median_destIP": ""
                        }
                    }

                    with open(JSON_COVERAGE_PATH, "w", encoding="UTF-8") as json_file:
                        json.dump(data, json_file, indent=4)

                    # we change the operation mode to generate the outcome of the coverage
                    self.segregation_config["operation_mode"] = "generate_coverage_outcome"
                else:
                    # if we are not in testing phase, the system is shut down and the data analyst
                    # needs to check the coverage before restarting the system
                    print("Shutting down the system. Data Analyst can restart it after the coverage check.")
                    with open(CONFIG_PATH, "r", encoding="UTF-8") as json_file:
                        data = json.load(json_file)
                    data["operationMode"] = "generate_coverage_outcome"
                    with open(CONFIG_PATH, "w", encoding="UTF-8") as json_file:
                        json.dump(data, json_file, indent=4)
                    return False

            # The outcome of the coverage plot is checked to see if the coverage is approved.
            # If the coverage is approved, the system generates the learning sets and sends
            # them to the development system. If the coverage is not approved, the system goes
            # back to the wait sessions.
            if self.segregation_config["operation_mode"] == "generate_coverage_outcome":
                # Initialize the object to check the coverage outcome
                coverage_report = CoverageReport()

                if coverage_report.approved:
                    self.segregation_config["operation_mode"] = "generate_sets"
                else:
                    # if we are in the testing phase, we send the timestamp to the client-side system
                    # to tell them that the system is shutting down, but for testing purposes
                    # we just return to the wait sessions
                    if service_flag:
                        self.timestamp_end = time.time_ns()
                        diff_time = self.timestamp_end - self.timestamp_begin
                        sending_data = {
                            "system": "segregation_system",
                            "time": diff_time,
                            "end": True
                        }
                        try:
                            response = requests.post(URL, json=sending_data)
                            print("response", response)
                        except requests.exceptions.RequestException as e:
                            print("Error in sending data to the development system: ", e)

                        # we update the prepared_sessions table to process the sessions again
                        query = """
                        UPDATE prepared_sessions SET to_process = 1;
                        """
                        self.db.update(query, [])

                        # we change the operation mode to wait sessions
                        self.segregation_config["operation_mode"] = "wait_sessions"
                    else:
                        # if we are not in testing phase, the system is shut down and the data analyst
                        # needs to wait for more samples before restarting the system
                        print("Shutting down the system. More samples needed.")
                        with open(CONFIG_PATH, "r", encoding="UTF-8") as json_file:
                            data = json.load(json_file)
                        data["operationMode"] = "wait_sessions"
                        with open(CONFIG_PATH, "w", encoding="UTF-8") as json_file:
                            json.dump(data, json_file, indent=4)

                        # we update the prepared_sessions table to process the sessions again
                        query = """
                        UPDATE prepared_sessions SET to_process = 1;
                        """
                        self.db.update(query, [])
                        return False

            # The system generates the learning sets and sends them to the development system.
            # It also drops the row of prepared sessions already processed in the database.
            if self.segregation_config["operation_mode"] == "generate_sets":
                # Initialize the learning sets controller and generate the learning sets
                learning_sets_controller = LearningSetsController()
                learning_sets_controller.save_sets()

                # if we are in the testing phase, we send the timestamp to the client-side system
                # to tell them that the system is shutting down because the learning sets have been
                # generated and sent to the development system
                if service_flag:
                    self.timestamp_end = time.time_ns()
                    diff_time = self.timestamp_end - self.timestamp_begin

                    sending_data = {
                        "system": "segregation_system",
                        "time": diff_time,
                        "end": False
                    }

                    requests.post(URL, json=sending_data, timeout=20)

                # Send the learning sets to the development system
                self.communication_controller.send_learning_sets(SET_PATH)

                # Drop the rows of prepared sessions in the database that have been processed
                query = """
                DELETE FROM prepared_sessions WHERE to_process = 1;
                """
                self.db.delete(query, [])

                # if there are still prepared sessions in the database, we change the to_process
                # value to 1 to process them in the next iteration
                query = """
                UPDATE prepared_sessions SET to_process = 1;
                """
                self.db.update(query, [])

                # if we are in testing phase, we change the operation mode to wait sessions
                if service_flag:
                    self.segregation_config["operation_mode"] = "wait_sessions"
                else:
                    # if we are not in testing phase, the system is shut down and the data analyst
                    # needs to wait for more samples before restarting the system
                    with open(CONFIG_PATH, "r", encoding="UTF-8") as json_file:
                        data = json.load(json_file)
                    data["operationMode"] = "wait_sessions"
                    with open(CONFIG_PATH, "w", encoding="UTF-8") as json_file:
                        json.dump(data, json_file, indent=4)

                    return False

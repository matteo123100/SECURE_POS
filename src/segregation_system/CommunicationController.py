"""
This module is used to manage the communication between the
segregation system and the other systems.
"""
import json
import os
from typing import Callable
import requests
from flask_restful import Resource
from utility import data_folder
from comms import ServerREST
from comms.json_transfer_api import ReceiveJsonApi

# Define the paths to the input folder and the configuration file
FILE_PATH = os.path.join(data_folder, 'segregation_system', 'input')
CONFIG_PATH = os.path.join(data_folder, 'segregation_system', 'config', 'segregation_config.json')

class HealthCheckApi(Resource):
    """
    Health check endpoint to verify the server is running.
    """
    def get(self):
        return "Server is running", 200

class CommunicationController:
    """
    Class used to manage the communication between the segregation system and the other systems.
    """
    def __init__(self):
        """
        Constructor of the class.
        """
        with open(CONFIG_PATH, 'r', encoding="UTF-8") as file:
            # Load the configuration file
            config = json.load(file)

            # Load the configuration parameters
            self.ip_address = config["segregationSystemIpAddress"]
            self.port = config["segregationSystemPort"]
            self.development_system_url = config["developmentSystemEndpoint"]
            self.server = None
            self.check = config["checkServerEndpoint"]

    def is_server_running(self) -> bool:
        """
        Check if the REST server is already running by sending a request to the health endpoint.
        :return: True if the server is running, False otherwise.
        """
        try:
            response = requests.get(self.check, timeout=5)
            if response.status_code == 200:
                print("REST server is already running.")
                return True
        except requests.ConnectionError:
            print("REST server is not running.")
        return False

    def start_server(self, json_schema_path: dict, handler: Callable[[dict], None]) -> None:
        """
        Start the REST server.
        :param json_schema_path: path to the JSON schema file.
        :param handler: handler function to be called when a JSON is received.
        :return: None
        """

        # Initialize the REST server
        self.server = ServerREST()

        # Add the health check endpoint
        self.server.api.add_resource(
            HealthCheckApi,
            "/health",
            resource_class_kwargs={}
        )

        # Add the endpoint to receive JSON messages
        self.server.api.add_resource(
            ReceiveJsonApi,
            "/",
            resource_class_kwargs={
                'json_schema_path': json_schema_path,
                'handler': handler
            })

        # Start the REST server on the specified IP address and port
        self.server.run(host=self.ip_address, port=self.port, debug=False)

    def send_json(self, url, json_data):
        """
        Function used to send a json to a generic URL.
        :param url: URL where the json will be sent.
        :param json_data: JSON data to be sent.
        """

        # try to send the json to the specified URL with a post request
        try:
            requests.post(url,
                          json=json_data,
                          timeout=20)
        except requests.exceptions.RequestException as e:
            # print an error message if the request fails
            print("Error during the send of message: ", e)

    def send_learning_sets(self, learning_sets):
        """
        Function used to send the learning sets to the development system.
        :param learning_sets: path to the learning sets file.
        """

        # try to open the learning sets file and send the data to the development system
        try:
            with open(learning_sets, 'r', encoding="UTF-8") as file:
                data = json.load(file)

            response = requests.post(
                self.development_system_url, json=data,
                timeout=20
            )

            # print an error message if the request fails
            if not response.ok:
                print("Failed to send the learning sets")
            else:
                print("Learning sets sent")

        except requests.exceptions.RequestException as ex:
            # print an error message if the request fails
            print(f'Error during the send of the learning sets: {ex}')

""" 
This module contains the PrepareSessionHandler class for preparing and managing session data.
"""
import json
import os
import time

# pylint: disable=C0301

class PrepareSessionHandler:
    """
    A handler class for preparing and managing session data.

    Attributes:
        jsonIO (jsonIO.jsonIO): An instance of the jsonIO class for handling JSON input/output operations.
        uuid (str): The unique identifier for the session.
        label (str): The label associated with the session.
        median_coordinates (list): The median coordinates for the session.
        mean_diff_time (float): The mean difference in time for the session.
        mean_diff_amount (float): The mean difference in amount for the session.
        mean_target_ip (str): The mean target IP address for the session.
        mean_dest_ip (str): The mean destination IP address for the session.

    Methods:
        __init__(filepath):
            Initializes the PrepareSessionHandler with the given filepath for JSON I/O operations.

        session_request():
            Creates and returns a JSON object with the session data.

        new_session():
            Retrieves a new session message from the jsonIO, parses it, and updates the session attributes.
    """

    # Constructor for initializing the handler with a file path for JSON I/O
    def __init__(self):
                # Parse the session message to update session attributes
        self.uuid = None  # Unique identifier

        self.label = None  # Associated label
        self.median_coordinates = [None, None]  # Median coordinates
        self.mean_diff_time = None  # Mean time difference
        self.mean_diff_amount = None  # Mean amount difference
        self.mean_target_ip = None  # Mean target IP address
        self.mean_dest_ip = None  # Mean destination IP address

    def session_request(self):
        """
        Creates and returns a JSON object containing session data.
        This JSON will be based on the class attributes populated from the last session.
        """
        try:
            data = {
                # Unique identifier for the session
                'uuid': self.uuid,
                # Associated label for the session
                'label': self.label,
                # Median coordinates, formatted as a list of two elements
                'median_coordinates': [self.median_coordinates[0], self.median_coordinates[1]],
                # Mean time difference between events in the session
                'mean_diff_time': self.mean_diff_time,
                # Mean amount difference between events in the session
                'mean_diff_amount': self.mean_diff_amount,
                # The mean target IP address observed in the session
                'mean_target_ip': self.mean_target_ip,
                # The mean destination IP address observed in the session
                'mean_dest_ip': self.mean_dest_ip
            }

            # Return the session data as a JSON object
            return data
        except (TypeError, ValueError, KeyError):
            return None

    def new_session(self):
        """
        Retrieves a new session message from the JSON I/O system.
        Parses the message to populate the attributes of the current session.
        """
        current_directory = os.path.join(os.path.dirname(__file__), 'session')

        # wait until at least one file with .json extension is present in the "session" directory
        while not any(fname.endswith('.json') for fname in os.listdir(current_directory)):
            # wait for file to be received
            time.sleep(1)

            # get list of files in the directory and take the first one with .json extension
        files = [fname for fname in os.listdir(current_directory) if fname.endswith('.json')]
        if not files:
            return False
        filename = files[0]
        with open(os.path.join(current_directory, filename), 'r', encoding='utf-8') as file:
            message = json.load(file)

            # delete the file
            os.remove(os.path.join(current_directory, filename))

        # If the message is empty, exit the method
        if not message:
            return False

        try:
            # Parse the session message to update session attributes
            self.uuid = message['UUID']  # Unique identifier
            # Extract and set median coordinates
            self.median_coordinates = [
                message['median_lat'],  # Median latitude
                message['median_long']  # Median longitude
            ]
            self.mean_diff_time = message['mean_abs_diff_ts']  # Mean time difference
            self.mean_diff_amount = message['mean_abs_diff_am']  # Mean amount difference
            self.mean_target_ip = message['median_targetIP']  # Mean target IP address
            self.mean_dest_ip = message['median_destIP']  # Mean destination IP address
        except (KeyError, TypeError, ValueError) as e:
            print(f"Error parsing session message: {e}")
            return False
        return True

"""
This module contains a class for handling the internal status of the Development System
"""
import os
import json


class DevelopmentSystemStatus:
    """
    Class that handles the system status
    """
    def __init__(self, status_file):
        """
        Initialize the status by loading internal file
        :param status_file: path to status file
        """
        self.status_file = status_file
        if os.path.isfile(status_file):
            with open(status_file, "r", encoding="UTF-8") as file:
                self.status = json.load(file)
                if self.status['phase'] == "Waiting":
                    self.status = {
                        "phase": "Starting"
                    }
        else:
            self.status = {
                "phase": "Starting"
            }

    def update_status(self, new_status: dict):
        """
        Update the status of the system
        :param new_status: dictionary of updates
        :return:
        """
        self.status.update(new_status)
        with open(self.status_file, "w", encoding="UTF-8") as file:
            json.dump(self.status, file)

    def get_phase(self) -> str:
        """
        Gets current phase the system is in
        :return: a string representing the phase
        """
        return self.status['phase']

    def first_iter(self) -> bool:
        """
        Tells if a learning curve was already generated
        :return: True if "max_iter" is already in the internal status
        """
        return "max_iter" not in self.status

    def get_training_params(self) -> dict:
        """
        Gets training parameters by compacting max_iter and avg_params in the same dictionary
        :return: a dictionary of parameters for training
        """
        params = {
            "max_iter": self.status['max_iter']
        }
        params.update(self.status['avg_params'])
        return params

    def get_max_iter(self) -> int:
        """
        Gets the number of iterations saved in the internal status
        :return: the lastly used max_iter if present, -1 otherwise
        """
        if "max_iter" in self.status:
            return int(self.status['max_iter'])
        return -1

    def get_best_classifier_id(self) -> int:
        """
        Gets the index of the model selected by the user
        :return: an index if a valid model was already selected,-1 otherwise
        """
        if "best_classifier_data" in  self.status:
            return int(self.status["best_classifier_data"]["index"])
        return -1

    def get_best_classifier_data(self) -> dict:
        """
        Gets the information of the best model, saved in the internal status
        :return: a dictionary of information
        """
        return self.status["best_classifier_data"]

    def retry(self):
        """
        Discards results and sets internal state to the phase
        before the first learning curve was generated
        :return:
        """
        self.status = {"phase": "Ready"}
        with open(self.status_file, "w", encoding="UTF-8") as file:
            json.dump(self.status, file)

    def reset(self):
        """
        Resets the whole system
        :return:
        """
        self.status = {"phase": "Starting"}
        with open(self.status_file, "w", encoding="UTF-8") as file:
            json.dump(self.status, file)

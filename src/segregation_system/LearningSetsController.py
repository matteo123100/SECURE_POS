"""
This module is responsible for generating the learning sets for the development system.
"""
import ipaddress
import json
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from utility import data_folder
from segregation_system.DataExtractor import DataExtractor

# Path to the parameters file and the output file
PARAMETERS_PATH = os.path.join(data_folder, 'segregation_system', 'config', 'learning_sets_parameters.json')
FILE_PATH = os.path.join(data_folder, 'segregation_system', 'sets', 'all_sets.json')

def ip_to_float(ip_string):
    """
    Convert an IP address string to a normalized float.
    """
    try:
        return float(int(ipaddress.ip_address(ip_string))) / float(int(ipaddress.ip_address("255.255.255.255")))
    except ValueError:
        return 0.0  # Return 0.0 if the IP is invalid

class LearningSetsParameters:
    """
    This class is responsible for loading the parameters for the learning sets generation.
    """
    def __init__(self):
        """
        Constructor for the LearningSetsParameters class.
        """


        # Load the parameters from the JSON file.
        # - trainPercentage: percentage of the training set
        # - testPercentage: percentage of the test set
        # - validationPercentage: percentage of the validation set
        try:
            with open(PARAMETERS_PATH, 'r', encoding="UTF-8") as f:
                config = json.load(f)
        except FileNotFoundError:
            print('ERROR> Parameters file not found')
        except json.JSONDecodeError:
            print('ERROR> Error decoding JSON file')

        self.train_percentage = float(config['trainPercentage'])
        self.test_percentage = float(config['testPercentage'])
        self.validation_percentage = float(config['validationPercentage'])


class LearningSet:
    """
    This class is responsible for storing the learning sets.
    """
    def __init__(self, training_set, validation_set, test_set):
        """
        Constructor for the LearningSet class.
        :param training_set: data structure that stores the training set
        :param validation_set: data structure that stores the validation set
        :param test_set: data structure that stores the test set
        """
        self.training_set = training_set
        self.validation_set = validation_set
        self.test_set = test_set


class LearningSetsController:
    """
    This class is responsible for generating the learning sets for the development system.
    """
    def __init__(self):
        """
        Constructor for the LearningSetsController class.
        """

        # Initialize the parameters and the data extractor.
        # - parameters: object that stores the parameters for the learning sets generation
        # - data_extractor: object that extracts the data from the database
        self.parameters = LearningSetsParameters()
        self.data_extractor = DataExtractor()

    def _process_ip_columns(self, data):
        """
        Detects IP-related columns, converts them to normalized floats.
        :param data: Input dataframe with potential IP columns.
        :return: Processed dataframe with normalized IP values.
        """
        ip_columns = [col for col in data.columns if 'ip' in col.lower()]

        for col in ip_columns:
            # Convert IP addresses to normalized floats using the ip_to_float function
            data[col] = data[col].apply(ip_to_float)

        return data

    def generate_sets(self):
        """
        This method is responsible for generating the learning sets.
        :return: learning sets
        """

        # Extract the data and the labels from the database.
        input_data = self.data_extractor.extract_all()
        input_labels = self.data_extractor.extract_labels()

        # Convert the labels to numerical values.
        label_mapping = {
            "normal": 0,
            "moderate": 1,
            "high": 2
        }
        input_labels = input_labels.replace(label_mapping)
        input_data = self._process_ip_columns(input_data)

        # Generate the training set and the temporary set that will be split into the validation and test sets.
        test_length = 1.0 - self.parameters.train_percentage
        x_train, x_tmp, y_train, y_tmp = train_test_split(
            input_data, input_labels, stratify=input_labels, test_size=test_length
        )

        # Split the temporary set into the validation and test sets.
        x_validation = x_tmp[:len(x_tmp) // 3]
        x_test = x_tmp[len(x_tmp) // 3:]
        y_validation = y_tmp[:len(y_tmp) // 3]
        y_test = y_tmp[len(y_tmp) // 3:]

        # Combine features and labels for the training set
        training_set = pd.DataFrame(x_train)
        training_set['label'] = y_train

        # Combine features and labels for the validation set
        validation_set = pd.DataFrame(x_validation)
        validation_set['label'] = y_validation

        # Combine features and labels for the test set
        test_set = pd.DataFrame(x_test)
        test_set['label'] = y_test

        # Return the learning sets
        return LearningSet(training_set, validation_set, test_set)

    def save_sets(self):
        """
        This method is responsible for saving the learning sets to a JSON file.
        """
        sets = self.generate_sets()

        # Drop 'uuid' and 'label' from features
        training_features = sets.training_set.drop(columns=['uuid', 'label'], errors='ignore')
        validation_features = sets.validation_set.drop(columns=['uuid', 'label'], errors='ignore')
        test_features = sets.test_set.drop(columns=['uuid', 'label'], errors='ignore')

        # Create a dictionary to store all sets
        all_sets = {
            "training_set": {
                "features": training_features.to_dict(orient='records'),
                "labels": sets.training_set['label'].to_list()
            },
            "validation_set": {
                "features": validation_features.to_dict(orient='records'),
                "labels": sets.validation_set['label'].to_list()
            },
            "test_set": {
                "features": test_features.to_dict(orient='records'),
                "labels": sets.test_set['label'].to_list()
            }
        }

        # Save the dictionary as a single JSON file
        with open(FILE_PATH, 'w', encoding="UTF-8") as f:
            json.dump(all_sets, f, indent='\t')

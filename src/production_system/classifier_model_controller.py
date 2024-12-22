"""
Module delegated to the classification of the session request.
"""
import os
import time
import ipaddress
import json
import joblib
import pandas as pd
import requests

# pylint: disable=C0301
class ClassifierModelController:
    """
    Controller class for managing and using a classifier model.

    Methods:
    --------
    __init__():
        Initializes the ClassifierModelController instance, loads hyperparameters, and loads the classifier model.
    get_hyperparameters():
        Retrieves hyperparameters from a JSON file.
    load_classifier():
        Loads the classifier model using the hyperparameters.
    get_classifier_model():
        Returns the loaded classifier model.
    classify(data):
        Classifies the given data using the loaded model.
    predict(data):
        Placeholder method for predicting data using the model.
    """
    def __init__(self):
        """
        Initializes the ClassifierModelController.

        This includes creating an instance of the JSON I/O handler and loading the classifier model with its hyperparameters.
        """
        self.model = None
        while self.model is None:
            self.load_classifier()

    def get_hyperparameters(self):
        """
        Retrieves hyperparameters for the classifier model.

        The hyperparameters are fetched using the JSON I/O handler from a predefined source.
        
        Returns:
        --------
        dict
            A dictionary containing hyperparameters like 'num_inputs', 'num_layers', 'num_neurons', 
            'training_error', and 'model_file'.
        """
        # Check if the file exists
        while not os.path.exists('model/hyperparameters.json'):
            time.sleep(1)
        with open('model/hyperparameters.json', 'r', encoding='utf-8') as file:
            hyperparameters = json.load(file)
        return hyperparameters

    def load_classifier(self):
        """
        Loads the classifier model using hyperparameters.

        Extracts necessary details like the number of inputs, layers, neurons, and training error from the hyperparameters.
        Uses the 'model_file' path from hyperparameters to load the model with joblib.
        """
        model_file = os.path.join('src', 'production_system', 'model')

        while not any(fname.endswith('.joblib') for fname in os.listdir(model_file)):
            time.sleep(1)
        # load the classifier model
        try:

            files = [fname for fname in os.listdir(model_file) if fname.endswith('.joblib')]
            model_file = os.path.join(model_file, files[0])

            start_time = time.time_ns()

            self.model = joblib.load(model_file)

            time_now = time.time_ns()
            end_time = time_now - start_time

            print(f"Time now: {time_now}.Time to deploy classifier model in seconds: {end_time/(10**9)}")
            try:
                requests.post("http://192.168.97.2:5555/", json={
                    'system':'production_system',
                    'time':end_time,
                    'end':True
                }, timeout=10)
            except requests.exceptions.RequestException as e:
                print(f"An error occurred while sending timestamp: {e}")
        except (FileNotFoundError, joblib.externals.loky.process_executor.TerminatedWorkerError) as e:
            print(f"Error loading model: {e}")
            self.model = None
            return False
        os.remove(model_file)
        return True

    def classify(self, data):
        """
        Classifies the given data using the loaded model.

        Parameters:
        -----------
        data : dict
            The input data to classify.

        Returns:
        --------
        array
            The classification results.
        """
        if not hasattr(self, 'model'):
            raise RuntimeError("Model not loaded")

        start_time = time.time()
        # Estrai le caratteristiche rilevanti dal dizionario
        features = {
            'mean_abs_diff_ts': data['mean_diff_time'],
            'mean_abs_diff_am': data['mean_diff_amount'],
            'median_long': data['median_coordinates'][1],
            'median_lat': data['median_coordinates'][0],
            'median_targetIP': ip_to_float(data['mean_target_ip']),  # Converti IP a float
            'median_destIP': ip_to_float(data['mean_dest_ip']),  # Converti IP a float
        }
        # Converti le caratteristiche in un DataFrame di pandas
        features_df = pd.DataFrame([features])
        # Predici con il modello
        y_pred = self.model.predict(features_df)  # Usa il modello caricato
        end_time = time.time()
        print("Classification took ", end_time - start_time, " seconds")
        return y_pred

    def get_classifier_model(self):
        """
        Returns the loaded classifier model.

        Returns:
        --------
        MLPClassifier
            The loaded classifier model.
        """
        if not hasattr(self, 'model'):
            raise RuntimeError("Model not loaded")
        return self.model

def ip_to_float(ip_string):
    """
    Convert an IP address string to a normalized float.
    """
    try:
        return float(int(ipaddress.ip_address(ip_string))) / float(int(ipaddress.ip_address("255.255.255.255")))
    except ValueError:
        return 0.0  # Return 0.0 if the IP is invalid

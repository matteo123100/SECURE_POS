""" 
This module contains the unit tests for the ClassifierModelController class.
"""
# pylint: disable=E0401

import unittest
import ipaddress
from unittest.mock import patch, mock_open, MagicMock
from classifier_model_controller import ClassifierModelController, ip_to_float


class TestClassifierModelController(unittest.TestCase):
    """ 
    Unit tests for the ClassifierModelController class.
    """
    @patch('classifier_model_controller.os.path.exists')
    @patch('classifier_model_controller.joblib.load')
    def test_init(self, mock_joblib_load, mock_path_exists):
        """ 
        Test the initialization of the ClassifierModelController class.
        """
        # Mock the existence of the model file
        mock_path_exists.return_value = True
        mock_joblib_load.return_value = MagicMock()

        # Initialize the controller
        controller = ClassifierModelController()

        # Check if the model is loaded
        self.assertIsNotNone(controller.model)

    @patch('classifier_model_controller.os.path.exists')
    @patch('classifier_model_controller.time.sleep')
    @patch('builtins.open', new_callable=mock_open,
        read_data='{"model_file": "model/classifier_model.joblib"}')
    def test_get_hyperparameters(self, mock_path_exists):
        """ 
        Test the get_hyperparameters method of the ClassifierModelController class.
        """
        # Mock the existence of the hyperparameters file
        mock_path_exists.return_value = True

        # Initialize the controller
        controller = ClassifierModelController()

        # Get hyperparameters
        hyperparameters = controller.get_hyperparameters()

        # Check if the hyperparameters are correct
        self.assertEqual(hyperparameters['model_file'], 'model/classifier_model.joblib')

    @patch('classifier_model_controller.os.path.exists')
    @patch('classifier_model_controller.time.sleep')
    @patch('classifier_model_controller.joblib.load')
    def test_load_classifier(self, mock_joblib_load, mock_path_exists):
        """ 
        Test the load_classifier method of the ClassifierModelController class.
        """
        # Mock the existence of the model file
        mock_path_exists.return_value = True
        mock_joblib_load.return_value = MagicMock()

        # Initialize the controller
        controller = ClassifierModelController()

        # Load the classifier
        result = controller.load_classifier()

        # Check if the model is loaded
        self.assertTrue(result)
        self.assertIsNotNone(controller.model)

    @patch('classifier_model_controller.os.path.exists')
    @patch('classifier_model_controller.time.sleep')
    @patch('classifier_model_controller.joblib.load')
    def test_classify(self, mock_joblib_load, mock_path_exists):
        """ 
        Test the classify method of the ClassifierModelController class.
        """
        # Mock the existence of the model file
        mock_path_exists.return_value = True
        mock_joblib_load.return_value = MagicMock()

        # Initialize the controller
        controller = ClassifierModelController()

        # Mock the model's predict method
        controller.model.predict = MagicMock(return_value=[1])

        # Create a sample data
        data = {
            'median_coordinates': [40.7128, -74.0060],
            'mean_diff_time': 10.5,
            'mean_diff_amount': 200.0,
            'mean_target_ip': '192.168.1.1',
            'mean_dest_ip': '192.168.1.2'
        }

        # Classify the data
        result = controller.classify(data)

        # Check if the classification result is correct
        self.assertEqual(result, [1])

    @patch('classifier_model_controller.os.path.exists')
    @patch('classifier_model_controller.joblib.load')
    def test_get_classifier_model(self, mock_joblib_load, mock_path_exists):
        """ 
        Test the get_classifier_model method of the ClassifierModelController class.
        """
        # Mock the existence of the model file
        mock_path_exists.return_value = True
        mock_joblib_load.return_value = MagicMock()

        # Initialize the controller
        controller = ClassifierModelController()

        # Get the classifier model
        model = controller.get_classifier_model()

        # Check if the model is correct
        self.assertIsNotNone(model)

    def test_ip_to_float(self):
        """ 
        Test the ip_to_float function.
        """
        # Test valid IP address
        ip = '192.168.1.1'
        result = ip_to_float(ip)
        expected = float(int(ipaddress.ip_address(ip))) / \
               float(int(ipaddress.ip_address("255.255.255.255")))
        self.assertEqual(result, expected)

        # Test invalid IP address
        ip = 'invalid_ip'
        result = ip_to_float(ip)
        self.assertEqual(result, 0.0)

if __name__ == '__main__':
    unittest.main()

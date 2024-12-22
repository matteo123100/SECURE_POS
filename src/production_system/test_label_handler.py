""" 
This module contains the unit tests for the LabelHandler class.
"""
# pylint: disable=E0401

import unittest
from unittest.mock import patch, MagicMock
from label_handler import LabelHandler
import requests

class TestLabelHandler(unittest.TestCase):
    """ 
    Unit tests for the LabelHandler class.
    """

    def test_create_label_normal(self):
        """ 
        Test the creation of a label with a normal value.
        """
        # Create an instance of LabelHandler
        handler = LabelHandler(uuid="12345", label=0)

        # Check if the label is created correctly
        expected_label = {
            "session_id": "12345",
            "source": "classifier",
            "value": "normal"
        }
        self.assertEqual(handler.label, expected_label)

    def test_create_label_moderate(self):
        """ 
        Test the creation of a label with a moderate value.
        """
        # Create an instance of LabelHandler
        handler = LabelHandler(uuid="12345", label=1)

        # Check if the label is created correctly
        expected_label = {
            "session_id": "12345",
            "source": "classifier",
            "value": "moderate"
        }
        self.assertEqual(handler.label, expected_label)

    def test_create_label_high(self):
        """ 
        Test the creation of a label with a high value.
        """
        # Create an instance of LabelHandler
        handler = LabelHandler(uuid="12345", label=2)

        # Check if the label is created correctly
        expected_label = {
            "session_id": "12345",
            "source": "classifier",
            "value": "high"
        }
        self.assertEqual(handler.label, expected_label)

    @patch('label_handler.requests.post')
    def test_send_label_evaluation(self, mock_post):
        """ 
        Test the send_label method of the LabelHandler class with the evaluation phase.
        """
        # Mock the post request
        mock_post.return_value = MagicMock(status_code=200)

        # Create an instance of LabelHandler
        handler = LabelHandler(uuid="12345", label=1)

        # Send the label to the evaluation phase
        handler.send_label(phase='evaluation')

        # Check if the post request was made with the correct parameters
        mock_post.assert_called_once_with('http://192.168.97.2:8001', json=handler.label, timeout=1)

    @patch('label_handler.requests.post')
    def test_send_label_production(self, mock_post):
        """ 
        Test the send_label method of the LabelHandler class with the production phase.
        """
        # Mock the post request
        mock_post.return_value = MagicMock(status_code=200)

        # Create an instance of LabelHandler
        handler = LabelHandler(uuid="12345", label=1)

        # Send the label to the production phase
        handler.send_label(phase='production')

        # Check if the post request was made with the correct parameters
        mock_post.assert_called_once_with('http://192.168.97.2:8001', json=handler.label, timeout=1)

    @patch('label_handler.requests.post')
    def test_send_label_request_exception(self, mock_post):
        """ 
        Test the send_label method of the LabelHandler class with a request exception.
        """
        # Mock the post request to raise an exception
        mock_post.side_effect = requests.exceptions.RequestException

        # Create an instance of LabelHandler
        handler = LabelHandler(uuid="12345", label=1)

        # Send the label to the evaluation phase
        result = handler.send_label(phase='evaluation')

        # Check if the post request was made with the correct parameters
        mock_post.assert_called_once_with('http://192.168.97.2:8001', json=handler.label, timeout=1)

        # Check if the result is None (indicating an exception was handled)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()

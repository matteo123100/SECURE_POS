""" 
This module contains the unit tests for the PrepareSessionHandler class.
"""
# pylint: disable=E0401

import unittest
from unittest.mock import patch, mock_open
import os
from prepare_session_handler import PrepareSessionHandler

class TestPrepareSessionHandler(unittest.TestCase):
    """     
    Unit tests for the PrepareSessionHandler class.
    """

    @patch('prepare_session_handler.os.path.exists')
    @patch('prepare_session_handler.os.listdir')
    @patch('prepare_session_handler.time.sleep')
    @patch('builtins.open', new_callable=mock_open,
        read_data='{"UUID": "12345", "median_lat": 40.7128, "median_long": -74.0060}')
    @patch('prepare_session_handler.os.remove')
    def test_new_session(self, mock_remove, mock_listdir, mock_path_exists):
        """ 
        Test the new_session method of the PrepareSessionHandler class.
        """
        # Mock the existence of the directory and files
        mock_path_exists.return_value = True
        mock_listdir.side_effect = [['session.json'], ['session.json'], []]

        # Initialize the handler
        handler = PrepareSessionHandler()

        # Call the new_session method
        result = handler.new_session()

        # Check if the session was processed correctly
        self.assertTrue(result)
        self.assertEqual(handler.uuid, "12345")
        self.assertEqual(handler.median_coordinates, [40.7128, -74.0060])

        # Check if the file was removed
        mock_remove.assert_called_once_with(
            os.path.join(os.path.dirname(__file__), 'session', 'session.json'))

    @patch('prepare_session_handler.os.path.exists')
    @patch('prepare_session_handler.os.listdir')
    @patch('prepare_session_handler.time.sleep')
    def test_new_session_no_files(self, mock_listdir, mock_path_exists):
        """     
        Test the new_session method of the PrepareSessionHandler class when no files are present.
        """
        # Mock the existence of the directory but no files
        mock_path_exists.return_value = True
        mock_listdir.return_value = []

        # Initialize the handler
        handler = PrepareSessionHandler()

        # Call the new_session method
        result = handler.new_session()

        # Check if the session was not processed
        self.assertFalse(result)
        self.assertIsNone(handler.uuid)
        self.assertIsNone(handler.median_coordinates)

    @patch('prepare_session_handler.os.path.exists')
    @patch('prepare_session_handler.os.listdir')
    @patch('prepare_session_handler.time.sleep')
    @patch('builtins.open', new_callable=mock_open, read_data='{}')
    def test_new_session_empty_file(self, mock_listdir, mock_path_exists):
        """     
        Test the new_session method of the PrepareSessionHandler class when the file is empty.
        """
        # Mock the existence of the directory and an empty file
        mock_path_exists.return_value = True
        mock_listdir.side_effect = [['session.json'], ['session.json'], []]

        # Initialize the handler
        handler = PrepareSessionHandler()

        # Call the new_session method
        result = handler.new_session()

        # Check if the session was not processed
        self.assertFalse(result)
        self.assertIsNone(handler.uuid)
        self.assertIsNone(handler.median_coordinates)

    @patch('prepare_session_handler.os.path.exists')
    @patch('prepare_session_handler.os.listdir')
    @patch('prepare_session_handler.time.sleep')
    @patch('builtins.open', new_callable=mock_open, read_data='{"UUID": "12345"}')
    def test_new_session_missing_coordinates(self, mock_listdir, mock_path_exists):
        """
        Test the new_session method of the PrepareSessionHandler class when coordinates are missing.
        """
        # Mock the existence of the directory and a file missing coordinates
        mock_path_exists.return_value = True
        mock_listdir.side_effect = [['session.json'], ['session.json'], []]

        # Initialize the handler
        handler = PrepareSessionHandler()

        # Call the new_session method
        result = handler.new_session()

        # Check if the session was not processed
        self.assertFalse(result)
        self.assertEqual(handler.uuid, "12345")
        self.assertIsNone(handler.median_coordinates)

    def test_get_data(self):
        """ 
        Test the get_data method of the PrepareSessionHandler class.
        """
        # Initialize the handler
        handler = PrepareSessionHandler()
        handler.uuid = "12345"
        handler.median_coordinates = [40.7128, -74.0060]

        # Get the session data
        data = handler.get_data()

        # Check if the data is correct
        expected_data = {"UUID": "12345", "median_coordinates": [40.7128, -74.0060]}
        self.assertEqual(data, expected_data)

if __name__ == '__main__':
    unittest.main()

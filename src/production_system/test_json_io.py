""" 
Unit tests for the JSON I/O module.
"""
# pylint: disable=E0401

import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import json
from json_io import ModelUpload, SessionUpload, FlaskServer

class TestModelUpload(unittest.TestCase):
    """ 
    Unit tests for the ModelUpload resource.
    """

    @patch('json_io.request')
    @patch('json_io.os.makedirs')
    @patch('json_io.open', new_callable=mock_open)
    def test_post_model_file(self, mock_makedirs, mock_request):
        """ 
        Test the post method of the ModelUpload resource.
        """
        # Mock the request to contain a file
        mock_request.files = {'file': MagicMock()}
        mock_request.files['file'].filename = 'classifier_model.joblib'

        # Create an instance of the resource
        resource = ModelUpload()

        # Call the post method
        response = resource.post()

        # Check if the file was saved correctly
        mock_makedirs.assert_called_once_with(
            os.path.join('src', 'production_system', 'model'), exist_ok=True)
        mock_request.files['file'].save.assert_called_once_with(
            os.path.join('src', 'production_system', 'model', 'classifier_model.joblib'))

        # Check the response
        self.assertEqual(response, ({'message': 'Model saved successfully'}, 201))

    @patch('json_io.request')
    def test_post_no_file(self, mock_request):
        """ 
        Test the post method of the ModelUpload resource when no file is present.
        """
        # Mock the request to not contain a file
        mock_request.files = {}

        # Create an instance of the resource
        resource = ModelUpload()

        # Call the post method
        response = resource.post()

        # Check the response
        self.assertEqual(response, ({'error': 'No file part in the request'}, 400))

class TestSessionUpload(unittest.TestCase):
    """
    Unit tests for the SessionUpload resource.
    """

    @patch('json_io.request')
    @patch('json_io.os.makedirs')
    @patch('json_io.open', new_callable=mock_open)
    def test_post_session_data(self, mock_makedirs, mock_request):
        """ 
        Test the post method of the SessionUpload resource.
        """
        # Mock the request to contain JSON data
        mock_request.is_json = True
        mock_request.get_data.return_value = json.dumps({
            'UUID': '12345',
            'data': 'example_data'
        })

        # Create an instance of the resource
        resource = SessionUpload()

        # Call the post method
        response = resource.post()

        # Check if the file was saved correctly
        mock_makedirs.assert_called_once_with(
            os.path.join('src', 'production_system', 'session'), exist_ok=True)
        mock_open().assert_called_once_with(
            os.path.join('src', 'production_system', 'session', '12345.json'), 'w', encoding='utf8')
        mock_open().write.assert_called_once_with(json.dumps({
            'UUID': '12345',
            'data': 'example_data'
        }))

        # Check the response
        self.assertEqual(response, ({'message': 'Session saved'}, 201))

    @patch('json_io.request')
    def test_post_invalid_json(self, mock_request):
        """ 
        Test the post method of the SessionUpload resource with invalid JSON data.
        """
        # Mock the request to contain invalid JSON data
        mock_request.is_json = True
        mock_request.get_data.return_value = 'invalid_json'

        # Create an instance of the resource
        resource = SessionUpload()

        # Call the post method
        response = resource.post()

        # Check the response
        self.assertEqual(response, ({'error': 'Invalid JSON format'}, 400))

    @patch('json_io.request')
    def test_post_missing_uuid(self, mock_request):
        """ 
        Test the post method of the SessionUpload resource with missing UUID.
        """
        # Mock the request to contain JSON data without UUID
        mock_request.is_json = True
        mock_request.get_data.return_value = json.dumps({
            'data': 'example_data'
        })

        # Create an instance of the resource
        resource = SessionUpload()

        # Call the post method
        response = resource.post()

        # Check the response
        self.assertEqual(response, ({'error': 'Missing required field: UUID'}, 400))

    @patch('json_io.request')
    def test_post_unsupported_media_type(self, mock_request):
        """ 
        Test the post method of the SessionUpload resource with unsupported media type.
        """
        # Mock the request to not contain JSON data
        mock_request.is_json = False

        # Create an instance of the resource
        resource = SessionUpload()

        # Call the post method
        response = resource.post()

        # Check the response
        self.assertEqual(response, ({'error': 'Unsupported media type'}, 415))

class TestFlaskServer(unittest.TestCase):
    """ 
    Unit tests for the FlaskServer class.
    """

    @patch('json_io.Flask.run')
    def test_start(self, mock_run):
        """ 
        Test the start method of the FlaskServer class.
        """
        # Create an instance of the FlaskServer
        server = FlaskServer()

        # Start the server
        server.start(debug=True)

        # Check if the server was started with the correct parameters
        mock_run.assert_called_once_with(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    unittest.main()

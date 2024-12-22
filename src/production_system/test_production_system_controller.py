""" 
Test the ProductionSystemController class
"""
# pylint: disable=E0401


import unittest
from unittest.mock import patch, MagicMock
from production_system_controller import ProductionSystemController

class TestProductionSystemController(unittest.TestCase):
    """     
    Unit tests for the ProductionSystemController class.
    """

    @patch('production_system_controller.classifier_model_controller.ClassifierModelController')
    def test_handle_classifier_model_deployment(self, mock_classifier_model_controller):
        """ 
        Test the handle_classifier_model_deployment method of the ProductionSystemController class.
        """
        # Mock the classifier model controller
        mock_classifier = mock_classifier_model_controller.return_value

        # Initialize the controller
        controller = ProductionSystemController()

        # Call the method
        controller.handle_classifier_model_deployment()

        # Check if the classifier model controller was initialized
        mock_classifier_model_controller.assert_called_once()
        self.assertEqual(controller.classifier, mock_classifier)

    @patch('production_system_controller.prepare_session_handler.PrepareSessionHandler')
    @patch('production_system_controller.time.sleep')
    def test_handle_prepared_session_reception(self, mock_sleep, mock_prepare_session_handler):
        """     
        Test the handle_prepared_session_reception method of the ProductionSystemController class.
        """
        # Mock the session handler
        mock_session_handler = mock_prepare_session_handler.return_value
        mock_session_handler.new_session.side_effect = [False, True]

        # Initialize the controller
        controller = ProductionSystemController()
        controller.session = mock_session_handler

        # Call the method
        controller.handle_prepared_session_reception()

        # Check if the session handler was called correctly
        self.assertEqual(mock_session_handler.new_session.call_count, 2)
        mock_sleep.assert_called_once_with(1)

    @patch('production_system_controller.classifier_model_controller.ClassifierModelController')
    @patch('production_system_controller.prepare_session_handler.PrepareSessionHandler')
    @patch('production_system_controller.label_handler.LabelHandler')
    def test_run_classification_task(
        self, mock_label_handler, mock_prepare_session_handler, mock_classifier_model_controller):
        """ 
        Test the run_classsification_task method of the ProductionSystemController class.
        """
        # Mock the classifier model controller
        mock_classifier = mock_classifier_model_controller.return_value
        mock_classifier.classify.return_value = 1

        # Mock the session handler
        mock_session_handler = mock_prepare_session_handler.return_value
        mock_session_handler.session_request.return_value = {'data': 'example'}

        # Mock the label handler
        mock_label_handler = mock_label_handler.return_value

        # Initialize the controller
        controller = ProductionSystemController()
        controller.classifier = mock_classifier
        controller.session = mock_session_handler

        # Call the method
        controller.run_classsification_task()

        # Check if the classification and label handler were called correctly
        mock_classifier.classify.assert_called_once_with(mock_session_handler.session_request())
        mock_label_handler.assert_called_once_with(mock_session_handler.uuid, 1)
        self.assertEqual(controller.label, mock_label_handler)

    @patch('production_system_controller.label_handler.LabelHandler')
    def test_send_label(self, mock_label_handler):
        """ 
        Test the send_label method of the ProductionSystemController class.
        """
        # Mock the label handler
        mock_label_handler = mock_label_handler.return_value

        # Initialize the controller
        controller = ProductionSystemController()
        controller.label = mock_label_handler

        # Call the method
        controller.send_label()

        # Check if the label was sent
        mock_label_handler.send_label.assert_called_once()

    @patch('production_system_controller.label_handler.LabelHandler')
    def test_send_label_evaluation(self, mock_label_handler):
        """ 
        Test the send_label_evaluation method of the ProductionSystemController class.
        """
        # Mock the label handler
        mock_label_handler = mock_label_handler.return_value

        # Initialize the controller
        controller = ProductionSystemController()
        controller.label = mock_label_handler

        # Call the method
        controller.send_label_evaluation()

        # Check if the label was sent with the evaluation phase
        mock_label_handler.send_label.assert_called_once_with('evaluation')

    @patch('production_system_controller.requests.post')
    @patch('production_system_controller.classifier_model_controller.ClassifierModelController')
    @patch('production_system_controller.prepare_session_handler.PrepareSessionHandler')
    @patch('production_system_controller.time.time_ns', side_effect=[1, 2, 3, 4])
    def test_run(
        self, mock_prepare_session_handler, mock_classifier_model_controller, mock_requests_post):
        """ 
        Test the run method of the ProductionSystemController class.
        """
        # Mock the classifier model controller
        mock_classifier = mock_classifier_model_controller.return_value

        # Mock the session handler
        mock_session_handler = mock_prepare_session_handler.return_value
        mock_session_handler.new_session.side_effect = [True, False]

        # Initialize the controller
        controller = ProductionSystemController()
        controller.classifier = mock_classifier
        controller.session = mock_session_handler

        # Mock the methods
        controller.handle_classifier_model_deployment = MagicMock()
        controller.handle_prepared_session_reception = MagicMock()
        controller.run_classsification_task = MagicMock()
        controller.send_label = MagicMock()

        # Call the method
        with self.assertRaises(StopIteration):
            controller.run()

        # Check if the methods were called correctly
        controller.handle_classifier_model_deployment.assert_called_once()
        controller.handle_prepared_session_reception.assert_called_once()
        controller.run_classsification_task.assert_called_once()
        controller.send_label.assert_called_once()

        # Check if the requests were sent correctly
        mock_requests_post.assert_any_call("192.168.97.2:5555/", json={
            'system': 'production_system',
            'time': 1,
            'end': True
        }, timeout=10)
        mock_requests_post.assert_any_call("192.168.97.2:5555/", json={
            'system': 'production_system',
            'time': 1,
            'end': True
        }, timeout=10)

if __name__ == '__main__':
    unittest.main()

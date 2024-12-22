"""
This module contains an orchestrator for testing a classifier
"""
import json
import logging

from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score

from development_system.testing_report_generator import TestingReportGenerator
from utility.json_validation import validate_json_data_file


class TestingOrchestrator:
    """
    Class for testing classifiers
    """
    def __init__(self, config_path, config_schema_path, report_file):
        """

        :param config_path:
        :param config_schema_path:
        :param report_file:
        """
        with open(config_path, "r", encoding="UTF-8") as file:
            conf_json = json.load(file)

        if not validate_json_data_file(conf_json, config_schema_path):
            logging.error("Impossible to load testing "
                          "configuration: JSON file is not valid")
            raise ValueError("Testing Orchestrator configuration failed")

        self.report_generator = TestingReportGenerator(report_file,
                                                       conf_json["generalization_tolerance"])

    def test_classifier(self,
                        classifier: MLPClassifier,
                        classifier_data: dict,
                        test_data,
                        test_labels):
        """
        Predicts labels from testing set and calculates accuracy error. Generates a report.
        :param classifier:
        :param classifier_data:
        :param test_data:
        :param test_labels:
        :return:
        """
        testing_error = 1 - accuracy_score(test_labels, classifier.predict(test_data))
        self.report_generator.generate_report(classifier_data, testing_error)

        print("Test finished")

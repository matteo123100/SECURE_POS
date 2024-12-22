"""
This module contains a class for generating testing reports
"""

import json


class TestingReportGenerator:
    """
    Class for generating a testing report
    """
    def __init__(self, report_file, generalization_tolerance):
        """
        :param report_file: path to file where the report will be written to
        :param generalization_tolerance: threshold in difference between test and validation error
        """
        self.report_file = report_file
        self.generalization_tolerance = generalization_tolerance

    def generate_report(self, classifier_data: dict, testing_error) -> None:
        """
        Generates report and saves it to file
        :return: None
        """
        error_difference = testing_error - classifier_data["validation_error"]
        passed = -self.generalization_tolerance < error_difference < self.generalization_tolerance

        report = {
            "title": "Testing Report",
            "classifier_id": classifier_data["index"],
            "hyper_parameters": {
                "layers": classifier_data["layers"],
                "neurons": classifier_data["neurons"]
            },
            "errors": {
                "validation_error": classifier_data["validation_error"],
                "testing_error": testing_error,
                "generalization_tolerance": self.generalization_tolerance,
                "error_difference": error_difference,
                "passed": bool(passed)
            }
        }

        with open(self.report_file, "w", encoding="UTF-8") as file:
            json.dump(report, file, indent='\t')

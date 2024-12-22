"""
This module contains a class for generating validation reports
"""

import json
import pandas as pd


class ValidationReportGenerator:
    """
    Class for generating a validation report
    """
    def __init__(self, report_file, overfitting_tolerance):
        """
        :param report_file: path to file where the report will be written to
        :param overfitting_tolerance: threshold in difference between training and validation error
        """
        self.report_file = report_file
        self.overfitting_tolerance = overfitting_tolerance
        self.report_df = pd.DataFrame()

    def add_row(self, classifier_data: dict) -> None:
        """
        Adds a new row to the report, sorts all rows and keeps only the first 5
        :param classifier_data: contains data of the classifier
        :return: None
        """
        error_difference = classifier_data["training_error"] - classifier_data["validation_error"]
        classifier_data["error_difference"] = error_difference
        valid = -self.overfitting_tolerance < error_difference < self.overfitting_tolerance
        classifier_data["valid"] = bool(valid)

        for key in classifier_data:
            classifier_data[key] = [classifier_data[key]]
        row = pd.DataFrame.from_dict(classifier_data)

        self.report_df = pd.concat([self.report_df, row]).sort_values(by='validation_error').head(5)

    def generate_report(self) -> None:
        """
        Saves report to file
        :return: None
        """
        report = {
            "title":                    "Validation Report",
            "overfitting_tolerance":    self.overfitting_tolerance,
            "best_classifiers":         self.report_df.to_dict(orient='records')
        }

        with open(self.report_file, "w", encoding="UTF-8") as file:
            json.dump(report, file, indent='\t')

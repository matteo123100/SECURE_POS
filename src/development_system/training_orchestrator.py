"""
This module contains the orchestrator for classifier training
"""

from sklearn.neural_network import MLPClassifier
from development_system.learning_curve_controller import LearningCurveController


class TrainingOrchestrator:
    """
    Orchestrator for training an MLP classifier
    """
    def __init__(self):
        """
        Initialize training orchestrator
        """
        self.training_params = {}

    def set_parameters(self, params: dict) -> None:
        """
        Set training parameters
        :param params: dictionary of 'parameter-name: value' couples
        :return: None
        """
        self.training_params.update(params)

    def generate_learning_curve(self, training_data, training_labels, learning_curve_path) -> None:
        """
        Generate a new learning curve
        :param training_data: training set features
        :param training_labels: training set labels
        :param learning_curve_path: path to save learning curve
        :return: None
        """
        tmp_classifier = MLPClassifier(random_state=42,
                                       **self.training_params)
        tmp_classifier.fit(training_data, training_labels)

        lcc = LearningCurveController(learning_curve_path)
        lcc.plot_learning_curve(tmp_classifier.loss_curve_)

    def train_classifier(self, training_data, training_labels) -> MLPClassifier:
        """
        Train an MLP classifier
        :param training_data: training set features
        :param training_labels: training set labels
        :return: fitted MLPClassifier
        """
        classifier = MLPClassifier(**self.training_params)
        classifier.fit(training_data, training_labels)
        return classifier

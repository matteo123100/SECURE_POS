"""
Production System Controller Module.
"""
# pylint: disable=E0401
import time
import requests
import classifier_model_controller  # Module for handling the classifier model
import prepare_session_handler  # Module for managing session preparation
import label_handler  # Module for handling labels

# pylint: disable=C0301
# Class to control the production system workflow
class ProductionSystemController:
    """
    ProductionSystemController manages the workflow of the production system.
    Attributes:
        classifier (classifier_model_controller): An instance of the classifier model controller.
        session (prepare_session_handler): An instance of the session handler.
        label (label_handler): An instance of the label handler.
    Methods:
        __init__():
            Initializes the ProductionSystemController with default attributes.
        handle_classifier_model_deployment():
            Initializes and deploys the classifier model by creating an instance of the classifier_model_controller.
        handle_prepared_session_reception():
            Receives a new session using the session handler and stores it for further classification tasks.
        run_classsification_task():
            Performs classification on the session request and initializes a LabelHandler with the resulting label.
        send_label():
            Sends the label generated from classification to the appropriate system.
        send_label_evaluation():
            Sends a label with the phase set to 'evaluation' for evaluation purposes.
        run():
            Starts the production system workflow, continuously handling incoming sessions, classifying them, and sending the resulting labels.
    """
    def __init__(self):
        self.classifier = None
        self.session = None
        self.label = None

    def handle_classifier_model_deployment(self):
        """
        Initializes and deploys the classifier model.
        
        This method creates an instance of the classifier_model_controller, which is responsible
        for loading and managing the classifier model used for classification tasks.
        """
        self.classifier = classifier_model_controller.ClassifierModelController()

    def handle_prepared_session_reception(self):
        """
        Receives a new session using the session handler.
        
        This method initializes the prepare_session_handler and uses it to retrieve a new session message.
        The session is then stored for further classification tasks.
        """
        while self.session.new_session() is False:
            time.sleep(1)

    def run_classsification_task(self):
        """
        Performs classification on the session request.
        
        This method takes the session's request, classifies it using the classifier model,
        and initializes a label_handler with the resulting label for further processing.
        """
        # Perform classification on the session request using the classifier model
        label = self.classifier.classify(self.session.session_request())
        self.label = label_handler.LabelHandler(self.session.uuid, label)
        # Initialize a label handler with the classification label

    def send_label(self):
        """
        Sends the label generated from classification.
        
        This method sends the generated label to the appropriate system (either evaluation or production).
        """
        self.label.send_label()

    def send_label_evaluation(self):
        """
        Sends an evaluation label.
        
        This method specifically sends a label with the phase set to 'evaluation', indicating
        that this label is meant for evaluation purposes rather than production.
        """
        self.label.send_label('evaluation')

    def run(self):
        """
        Starts the production system workflow.
        
        This method is the main loop of the production system. It continuously handles incoming sessions,
        classifies them using the classifier, and sends the resulting labels to the appropriate system.
        """
        development = True
        if development is False:
            self.handle_classifier_model_deployment()

        else:
            while True:
                self.handle_classifier_model_deployment()
        self.session = prepare_session_handler.PrepareSessionHandler()  # Initialize session handler
        while True:
            # Continuously handle incoming sessions and classify them
            self.handle_prepared_session_reception()

            start_time = time.time_ns()
            self.run_classsification_task()
            end_time = time.time_ns() - start_time
            try:
                requests.post("http://192.168.97.2:5555/",
                json={'system':'production_system',
                    'time':end_time,
                    'end':True}, 
                timeout=10)
            except requests.exceptions.RequestException as e:
                print(f"An error occurred while sending timestamp: {e}")

            self.send_label()

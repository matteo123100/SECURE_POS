""" 
This class is responsible for handling labels and sending them to different phases.
"""

import requests

class LabelHandler:
    """
    A class to handle labels and send them to different phases.

    Attributes:
    -----------
    uuid : str
        The unique identifier for the label.
    label : str
        The content of the label.

    Methods:
    --------
    __init__(label):
        Initializes the LabelHandler object with the given label data.

    send_label(phase='evaluation'):
        Sends the label to the specified phase (evaluation or production).
    """

    def __init__(self, uuid, label):
        """
        Constructs all the necessary attributes for the LabelHandler object.

        Parameters:
        -----------
        label : dict
            A dictionary containing 'uuid' and 'label' keys.
        """
        # Unique identifier for the label
        self.uuid = uuid
        # Content of the label
        self.label_string = ''
        self.create_label(uuid, label)

    def create_label(self, uuid, label):
        """ 
        Creates a label string from the given label.
        """
        label_string = ''
        if label == 0:
            label_string = 'normal'
        elif label == 1:
            label_string = 'moderate'
        elif label == 2:
            label_string = 'high'

        uuid_string = str(uuid)

        self.label = {"session_id": uuid_string,
                        "source": "classifier", 
                        "value": label_string}


    def send_label(self, phase='evaluation'):
        """
        Sends the label to the specified phase.

        Parameters:
        -----------
        phase : str, optional
            The phase to send the label to (default is 'evaluation').

        Sends the label to either the evaluation or production system based on the phase.
        """
        # Prepare the message to be sent
        if phase == 'evaluation':
            address = 'http://192.168.97.250:8001'
        else:
            address = 'http://192.168.97.250:8001'

        # Send the label to evaluation system using a post request
        try:
            requests.post(address, json=self.label, timeout=1)
        except requests.exceptions.RequestException:
            return
        return

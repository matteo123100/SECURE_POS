"""
This module offers classes to set up and deploy a simple REST server
"""

from flask import Flask
from flask_restful import Api


class ServerREST:
    """
    Central object of Flask Application
    """

    def __init__(self):
        """
        Initialize Flask Application
        """
        self.app = Flask(__name__)
        self.api = Api(self.app)

    def run(self, host="0.0.0.0", port=5000, debug=False):
        """
        Runs Flask Application on local server

        :param host: the hostname to listen on. Default is 0.0.0.0
        :param port: the port to listen on. Default is 5000
        :param debug: if given, enable or disable debug mode.
        """
        self.app.run(host=host, port=port, debug=debug)

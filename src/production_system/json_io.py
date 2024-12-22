"""
This module is responsible for handling JSON input/output operations.
"""
import os
import json

from flask import Flask, request
from flask_restful import Api, Resource
from flask_cors import CORS

class ModelUpload(Resource):
    """ 
    Flask-RESTful resource for handling model uploads.
    Methods
    -------
    post():
        Handles POST requests to upload a model file.
    """
    def post(self):
        """ 
        Handles POST requests to upload a model file.
        """
        # Verifica se il file è presente nella richiesta
        if 'file' in request.files:
            file = request.files['file']

            os.makedirs(os.path.join('src', 'production_system', 'model'), exist_ok=True)

            file.save(os.path.join('src', 'production_system', 'model', 'classifier_model.joblib'))
            return {'message': 'Model saved successfully'}, 201
        return {'error': 'No file part in the request'}, 400

class SessionUpload(Resource):
    """
    Flask-RESTful resource for handling session uploads.
    Methods
    -------
    post():
        Handles POST requests to upload session data in JSON format.

    """
    def post(self):
        """
        Handles POST requests to upload session data in JSON format.
        """
        # Verifica che la richiesta contenga dati JSON
        if request.is_json:
            try:
                # Carica i dati JSON dalla richiesta
                raw_data = request.get_data(as_text=True)  # Contenuto raw della richiesta
                # Parsing manuale del JSON
                try:
                    json_data = json.loads(raw_data)
                except json.JSONDecodeError:
                    return {'error': 'Invalid JSON format'}, 400

                # Verifica che il JSON contenga la chiave 'uuid' (attenzione al case-sensitive)
                if 'UUID' not in json_data:  # Cambiato da 'uuid' a 'UUID' in base ai dati ricevuti
                    return {'error': 'Missing required field: UUID'}, 400

                # Assicurati che esista la directory per salvare i file
                output_dir = os.path.join('src', 'production_system', 'session')
                os.makedirs(output_dir, exist_ok=True)

                # Salva il file JSON con il nome basato sull'UUID
                filename = f"{json_data['UUID']}.json"  # Cambiato da 'uuid' a 'UUID'
                file_path = os.path.join(output_dir, filename)
                with open(file_path, 'w', encoding='utf8') as file:
                    json.dump(json_data, file)

                return {'message': 'Session saved'}, 201

            except (OSError, IOError, json.JSONDecodeError) as e:
                # Gestisci eventuali errori durante il processo
                print(f"Error processing request: {e}")
                return {'error': 'Failed to process JSON'}, 500

        else:
            # Risposta per richieste con tipo MIME non supportato
            return {'error': 'Unsupported media type'}, 415

# pylint: disable=R0903

class FlaskServer:
    """
    Class to start the Flask server and add resources to it.
    Methods
    -------
    __init__():
        Initializes the Flask server and adds resources to it.
    start(debug=False):
        Starts the Flask server.
    """
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # Aggiungi supporto CORS
        self.api = Api(self.app)
        self.api.add_resource(ModelUpload, '/upload_model')
        self.api.add_resource(SessionUpload, '/upload_session')

        # Configura Flask per accettare file di grandi dimensioni
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

    def start(self, debug=False):
        """Metodo per avviare il server Flask."""
        self.app.run(debug=debug, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    server = FlaskServer()
    server.start()

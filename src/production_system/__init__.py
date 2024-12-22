
"""
The __init__.py file is used to initialize the production system and start the Flask server.
"""
# pylint: disable=E0401
import threading
import os
import time
from production_system_controller import ProductionSystemController
from json_io import FlaskServer


def start_flask_server():
    """
    Starts the Flask server.
    """
    flask_server = FlaskServer()
    flask_server.start()

def start_production_system_controller():
    """
    Starts the production system controller.
    """
    production_system_controller = ProductionSystemController()
    production_system_controller.run()

def main():
    """
    Main function to start the Flask server and production system controller in separate threads.
    
    This function performs the following steps:
    1. Creates and starts a new thread for the Flask server.
    2. Creates and starts a new thread for the production system controller.
    3. Waits for both threads to complete.
    4. Removes the classifier model file when both threads have ended.
    
    Note:
    The classifier model file is located at 'src/production system/model/classifier_model.joblib'.
    If the file exists, it will be removed. If the file does not exist, a message will be printed.
    """
    # Create a new Flask server thread
    flask_thread = threading.Thread(target=start_flask_server)
    flask_thread.start()

    # Create a new production system controller thread
    production_system_thread = threading.Thread(target=start_production_system_controller)
    production_system_thread.start()

    try:
        # Wait for both threads to complete
        production_system_thread.join()
        flask_thread.join()
    finally:
        # When both threads end, remove the model
        model_path = os.path.join('src', 'production_system', 'model', 'classifier_model.joblib')
        if os.path.exists(model_path):
            os.remove(model_path)
            print(f"Removed file: {model_path}")
        else:
            print(f"File not found: {model_path}")

if __name__ == "__main__":
    main()

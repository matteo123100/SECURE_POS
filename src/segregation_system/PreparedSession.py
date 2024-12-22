"""
This module is responsible for storing and managing prepared sessions
coming from the preparation system.
"""

import json
import os
import pandas as pd
from db_sqlite3 import DatabaseController
from utility.json_validation import validate_json_data_file
from utility import data_folder, project_root

DATABASE_PATH = os.path.join(project_root, 'src', 'segregation_system', 'segregationDB.db')
SCHEMA_PATH = os.path.join(data_folder,
                           'segregation_system', 'schemas', 'prepared_session_schema.json'
                          )


class PreparedSessionController:
    """
    Class that manages the prepared sessions.
    """
    def __init__(self):
        """
        Constructor of the PreparedSessionController class.
        """
        self.db = DatabaseController(DATABASE_PATH)

    def sessions_count(self):
        """
        Count the number of prepared sessions in the database.
        :return: the number of prepared sessions in the database
        """
        query = """
        SELECT COUNT(*) FROM prepared_sessions WHERE to_process = 1;
        """

        return self.db.read_sql(query).iloc[0, 0]

    def store(self, path, to_process):
        """
        Store a prepared session in the database.
        :param path: the path of the json file that contain the prepared session to store
        :param to_process: a boolean that indicates if the session is to process or not
        """
        # Load the json file
        with open(path, "r", encoding="UTF-8") as f:
            sessions = json.load(f)

        # Validate the json file
        if not validate_json_data_file(sessions, SCHEMA_PATH):
            return False

        # Create a dataframe from the json file
        df = pd.DataFrame([sessions])
        df["to_process"] = to_process

        # Insert the dataframe in the database
        return self.db.insert_dataframe(df, "prepared_sessions")

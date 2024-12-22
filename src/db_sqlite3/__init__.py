"""
This module offers classes to set up and deploy a sqlite3 database.
"""

import os
import sqlite3
import pandas as pd
"""
    sqlite3 Error : sqlite_[errorcode/errorname] require sqlite3 version 3.11
    https://docs.python.org/3/library/sqlite3.html#sqlite3.Error.sqlite_errorcode
"""


class DatabaseController:
    """
    Class that covers all low-level accesses to the database.
    This class does not implement any sanity check on queries.
    """

    def __init__(self, db_path: str):
        """
        :param db_path: path where the sqlite3 will be created,
            Use value ":memory:" to create an SQLite database existing only in memory .
            Give a <pathLike> object, i.e. str or bytes. test
            Can use os.fspath(path) when passing this parameter.
        """
        self.__database_path = db_path

    def __execute_commit_query(self, query: str, params: list):
        """
        :param query: single SQL statement
        :param params: Python values to bind to placeholders in sql.
            A sequence if unnamed placeholders are used.
            See https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders .
        :return: False if any error occurs, else True.
        """
        try:
            db_connection = sqlite3.connect(self.__database_path)
            cursor = db_connection.cursor()
            cursor.execute(query, params)
            db_connection.commit()
        except sqlite3.Error as er:
            print(er.sqlite_errorcode)  # Prints 275
            print(er.sqlite_errorname)  # Prints SQLITE_CONSTRAINT_CHECK
            return False
        return True
        # with sqlite3.connect(self.__database_path) as db_connection:
        #     cursor = db_connection.cursor()
        #     cursor.execute(sql=query, parameters=params)
        #     db_connection.commit()

    def create_table(self, query: str, params: list) -> bool:
        """
        Executes query of table creation, with given parameters if any
        :return: False if any error occurs, else True.
        """
        if "CREATE TABLE" not in query:
            return False
        return self.__execute_commit_query(query, params)

    def update(self, query: str, params: list) -> bool:
        """
        Executes query of table update, with given parameters if any.
        :return: False if any error occurs, else True.
        """
        if "UPDATE" not in query:
            return False
        return self.__execute_commit_query(query, params)

    def delete(self, query: str, params: list) -> bool:
        """
        Executes query of table delete, with given parameters if any.
        :return: False if any error occurs, else True.
        """
        if "DELETE" not in query:
            return False
        return self.__execute_commit_query(query, params)

    def insert_dataframe(self, dataframe: pd.DataFrame, table: str) -> bool:
        """
        Insert dataframe into table using pandas.DataFrame.to_sql,
            see : https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_sql.html .
        :param dataframe: dataframe that is to be uploaded to a table in target db.
        :param table: str name of SQL table in target db where dataframe shall be uploaded.
        :return: True if any row was affected, False otherwise.
        """
        try:
            db_connection = sqlite3.connect(self.__database_path, timeout=15)
            res = dataframe.to_sql(table, db_connection, if_exists="append", index=False)
        except sqlite3.Error as er:
            print(er.sqlite_errorcode)  # Prints 275
            print(er.sqlite_errorname)  # Prints SQLITE_CONSTRAINT_CHECK
            return False
        return bool(res)

    def read_sql(self, query: str, params=None):
        """
        Reads table or result of query from db using pandas.read_sql,
            see : https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html .
        :param query: str SQL query to be executed, or a table name.
        :param params: Parameters to bind to the query (default is None).
        :return: DataFrame or Iterator[DataFrame].
        """
        if params is None:
            params = []  # Default is an empty list if no parameters are provided
        with sqlite3.connect(self.__database_path, timeout=15) as db_connection:
            return pd.read_sql(query, db_connection, params=params)

    def drop_table(self, table: str) -> bool:
        """
        :param table: str name of Table to drop_if_exists from db.
        :return: False if any error occurs, else True.
        """
        return self.__execute_commit_query("DROP TABLE IF EXISTS ?;", [table])

    def drop_database(self) -> None:
        """
        Drop database (knows its location since __init__).
        :return:
        """
        try:
            os.remove(self.__database_path)
        except FileNotFoundError:
            return

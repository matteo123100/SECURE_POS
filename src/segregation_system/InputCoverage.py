"""
This module is responsible for checking the input coverage of the dataset.
"""
import os
import hashlib
import json
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from utility import data_folder
from segregation_system.DataExtractor import DataExtractor

# Path to the outcomes file and the image file
OUTCOMES_PATH = os.path.join(data_folder, 'segregation_system', 'outcomes', 'coverage_outcome.json')
IMAGE_PATH = os.path.join(data_folder, 'segregation_system', 'plots', 'coverage_plot.png')


class CoverageReport:
    """
    Class that holds the outcome of the input coverage check provided
    """
    def __init__(self):
        """
        Constructor for the CoverageReport class.
        """
        try:
            with open(OUTCOMES_PATH, 'r', encoding="UTF-8") as f:
                self.outcome = json.load(f)
        except FileNotFoundError:
            print("ERROR> Outcome file not found")
        except json.JSONDecodeError:
            print("ERROR> Error decoding JSON file")


        # Load the JSON attributes into the object.
        # - approved: bool, whether the input coverage is approved
        # - uncovered_features_suggestions: list of str, suggestions for uncovered features
        self.approved = self.outcome["approved"]
        self.uncovered_features_suggestions = self.outcome["uncovered_features_suggestions"]


class CheckInputCoverage:
    """
    Class that checks the input coverage of the dataset.
    """
    def __init__(self):
        """
        Constructor for the CheckInputCoverage class.
        """

        # Initialize the statistics attribute.
        # - statistics: pd.DataFrame, features of the dataset
        # - data_extractor: DataExtractor, object that extracts the features
        self.statistics = {}
        self.data_extractor = DataExtractor()

    def retrieve_features(self):
        """
        Retrieve the features of the dataset.
        """
        data = self.data_extractor.extract_features()

        # Create a DataFrame with the extracted features.
        self.statistics = pd.DataFrame(
            data,
            columns=["longitude", "latitude", "time", "amount", "targetIP", "destIP"]
        )

        # rename the columns for better readability
        self.statistics.rename(columns={
            "targetIP": "Median targetIP", "destIP": "Median destIP",
            "longitude": "Median longitude", "latitude": "Median latitude",
            "time": "Mean abs. diff. time", "amount": "Mean abs. diff. amount"
        }, inplace=True)

class ViewInputCoverage:
    """
    Class that visualizes the input coverage of the dataset
    """
    def __init__(self, coverage_report):
        """
        Constructor for the ViewInputCoverage class.
        :param coverage_report: data structure that holds the features for the plot
        """
        self.coverage_report = coverage_report

    def hash_ip(self, ip):
        """
        Hashes the IP address.
        :param ip: ip address
        """
        try:
            return int(hashlib.md5(str(ip).encode('utf-8')).hexdigest(), 16) % (10 ** 5)
        except Exception:
            return 0

    # Radar chart generation
    def radar_chart(self, data, original_df):
        # Get the features and the number of categories
        categories = list(data.columns)
        num_vars = len(categories)

        # Compute the angles for the radar chart
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]  # Repeat the first angle to close the circle

        # Initialize the radar chart
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

        # Define a color map for the features
        colors = plt.cm.get_cmap('tab10', num_vars)

        # Prepare legend entries
        legend_entries = []

        # Plot each feature as points with the same color
        for idx, feature in enumerate(categories):
            values = data[feature].tolist()
            values += values[:1]  # Close the circle
            ax.scatter([angles[idx]] * len(values[:-1]), values[:-1],
                       color=colors(idx), s=30, label=feature)

            # Safely compute min and max values for the legend
            min_val = original_df[feature].min()
            max_val = original_df[feature].max()

            # Append to legend entries with formatted min/max values
            if np.isfinite(min_val) and np.isfinite(max_val):
                legend_entries.append(f"{feature}: [{min_val:.2f}, {max_val:.2f}]")

        # Add labels and title
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10)

        # Adjust radial limits to ensure visibility
        ax.set_ylim(-0.1, 1.1)

        # set the title
        plt.title("Features Coverage", fontsize=14, fontweight='bold')

        # Add legend for min/max values
        plt.legend(legend_entries, loc='upper right', bbox_to_anchor=(1.1, 0.8), fontsize='small')

        # Save the plot
        plt.savefig(IMAGE_PATH)

    def show_plot(self):
        # Create a DataFrame from the statistics
        df = pd.DataFrame(self.coverage_report.statistics)

        # Process 'targetIP' and 'destIP' columns if they exist in order to hash the IP addresses
        if 'Median targetIP' in df.columns:
            df['Median targetIP'] = df['Median targetIP'].apply(lambda x: self.hash_ip(x))

        if 'Median destIP' in df.columns:
            df['Median destIP'] = df['Median destIP'].apply(lambda x: self.hash_ip(x))

        # Ensure all columns are numeric and fill NaN values
        df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

        # Select specific columns for the radar chart
        columns = ['Mean abs. diff. amount', 'Median longitude', 'Median latitude', 'Mean abs. diff. time', 'Median targetIP', 'Median destIP']
        df = df[columns]

        # Generate radar chart
        self.radar_chart(df, df)

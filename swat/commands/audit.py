import argparse
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Sequence, Union

import pandas as pd
from colorama import Fore, Style
from google.oauth2.service_account import Credentials
import googleapiclient
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ..commands.base_command import BaseCommand
from ..misc import get_custom_argparse_formatter, validate_args
from ..utils import ROOT_DIR


class KeyValueAction(argparse.Action):
    def __call__(self,
                 parser: argparse.ArgumentParser,
                 namespace: argparse.Namespace,
                 values: Union[str, Sequence[Any]],
                 option_string: Optional[str] = None) -> None:
        """
        The method is called when this action is specified on the command line.

        Parameters:
        parser (argparse.ArgumentParser): The argument parser object.
        namespace (argparse.Namespace): The namespace object that will be updated with the parsed values.
        values (Union[str, Sequence[Any]]): The command-line arguments to be parsed.
        option_string (Optional[str]): The option string that was used to invoke this action.

        Raises:
        argparse.ArgumentError: If the provided filter argument does not follow the 'key=value' format.

        Returns:
        None
        """
        for value in values:
            key, sep, val = value.partition('=')
            if sep != '=':
                raise argparse.ArgumentError(self, f"invalid filter argument '{value}', expected 'key=value'")
            setattr(namespace, self.dest, {key: val})

@dataclass
class Filters:
    """Dataclass representing a set of filters."""

    filters: Optional[Dict[str, Any]] = None

class Command(BaseCommand):
    """
    Command class for handling Google Workspace Audit command operations.

    Attributes:
        service (googleapiclient.discovery.Resource): The service resource object to interact with Google Workspace APIs.
        duration (str): The duration in format Xs, Xm, Xh or Xd to filter audit logs.
        application (str): The Google Workspace application name for which audit logs are to be fetched.
        filters (Filters): An object of Filters class that holds a dictionary of filter key-value pairs.
        parser (argparse.ArgumentParser): Argument parser object to parse command line arguments.
    """

    service: googleapiclient.discovery.Resource
    duration: str
    application: str
    filters: Filters

    parser = get_custom_argparse_formatter(prog="audit", description="Google Workspace Audit")
    parser.add_argument('application', help="Application name")
    parser.add_argument('duration', help="Duration in format Xs, Xm, Xh or Xd.")
    parser.add_argument('--columns', nargs='+', help="Columns to keep in the output. If not set, will take columns from config.")
    parser.add_argument('--export', action='store_true', default=False, help="Path to export the data")
    parser.add_argument('--export-format', choices=['csv', 'ndjson'], default='csv', help="Export format. Default is csv.")
    parser.add_argument('--filters', nargs='*', action=KeyValueAction, dest='filters', default={}, help='Filters to apply on the data')
    parser.add_argument('--interactive', action='store_true', help="Interactive mode")


    def __init__(self, **kwargs) -> None:
        """
        Initializes a new instance of the Command class.

        Parameters:
            kwargs (dict): Dictionary of keyword arguments.

        Raises:
            ImportError: If the pandas package is not installed.
            HttpError: If there is an error while building the Google Workspace admin service.
        """
        super().__init__(**kwargs)

        # Check if the session exists in the credential store
        if self.obj.cred_store.store['default'].session is None:
            self.logger.error(f"Please authenticate with 'auth session --default --config' before running this command.")
            return

        try:
            import pandas as pd
        except ImportError:
            self.logger.error(f"Pandas is not installed. Please install it with 'poetry install -E audit_support'.")
            return

        try:
            self.service = build('admin', 'reports_v1', credentials=self.obj.cred_store.store['default'].session)
        except HttpError as err:
            self.logger.error(f"An error occurred: {err}")
            return

        # Validate and setup arguments
        self.args = validate_args(self.parser, self.args)
        self.duration = self.args.duration
        self.application = self.args.application

        # Setup filters
        if self.args.filters:
            self.args.filters = [f.strip('\'"') for f in args.filters]
            self.filters = Filters(self.args.filters)


    def export_data(self, df: pd.DataFrame) -> None:
        """
        Exports the dataframe to a specified format.

        Parameters:
            df (pandas.DataFrame): The DataFrame to export.

        Raises:
            Warning: If the specified export format is not supported.
        """
        export_path = ROOT_DIR / f"{self.application}_{self.duration}.{self.args.export_format}"
        if self.args.export_format == 'csv':
            df.to_csv(export_path, index=False)
            self.logger.info(f"Data exported to {export_path} in CSV format.")
        elif self.args.export_format == 'ndjson':
            df.to_json(export_path, orient='records', lines=True)
            self.logger.info(f"Data exported to {export_path} in NDJSON format.")
        else:
            self.logger.warning(f"Unsupported export format: {self.args.export_format}. No data was exported.")


    def flatten_json(self, y: dict) -> dict:
        """
        Flattens a nested dictionary and returns a new dictionary with
        flattened structure where the nested keys are joined with underscore '_'.

        Parameters:
            y (dict): The dictionary to flatten.

        Returns:
            dict: The flattened dictionary.
        """
        out = {}

        def flatten(x, name=''):
            if type(x) is dict:
                for a in x:
                    flatten(x[a], name + a + '_')
            elif type(x) is list:
                i = 0
                for a in x:
                    flatten(a, name + str(i) + '_')
                    i += 1
            else:
                out[name[:-1]] = x

        flatten(y)
        return out

    def flatten_activities(self, activities: list) -> pd.DataFrame:
        """
        Flattens the activities data and converts it into a DataFrame.

        Parameters:
            activities (list): The list of activities data to flatten.

        Returns:
            pandas.DataFrame: The DataFrame containing the flattened activities data.
        """
        flattened_data = []
        for activity in activities:
            events = activity.pop('events')
            for event in events:
                # Convert parameters to a dictionary
                if 'parameters' in event:
                    parameters_dict = {item.get('name'): item.get('value') for item in event.pop('parameters')}
                    event = {**event, **parameters_dict}
                flattened_event = self.flatten_json(event)
                merged_data = {**activity, **flattened_event}
                flattened_data.append(merged_data)
        return pd.DataFrame(flattened_data)


    def fetch_data(self) -> pd.DataFrame:
        """
        Fetches the activity data from the Google Workspace Audit service, using the provided start time,
        application name, and user key. The data is returned as a pandas DataFrame.

        Returns:
            pandas.DataFrame: The DataFrame containing the fetched activity data.
        """
        now = pd.Timestamp.now(tz="UTC")
        start_time = (now - pd.to_timedelta(self.duration)).isoformat()
        request = self.service.activities().list(userKey='all', applicationName=self.application, startTime=start_time)
        activities = []

        while request is not None:
            activities_result = request.execute()
            activities.extend(activities_result.get('items', []))
            request = self.service.activities().list_next(request, activities_result)

        df = pd.DataFrame(activities)
        df = self.flatten_activities(activities)
        if self.args.filters:
            for column, value in self.args.filters.items():
                if "*" in value:
                    df = df[df[column].str.contains(value.strip('*'), case=False)]
                else:
                    df = df[df[column] == value]

        return df

    def filter_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filters the dataframe based on the columns specified in the arguments or in the config file.

        Args:
            df (pd.DataFrame): The dataframe to be filtered.

        Returns:
            pd.DataFrame: The filtered dataframe.
        """
        columns = self.args.columns or self.obj.config['google']['audit']['columns']
        modified_columns = [".*" + column + ".*" for column in columns]
        df = df[[column for column in df.columns for pattern in modified_columns if re.search(pattern, column, re.IGNORECASE)]]
        return df

    def interactive_session(self, df: pd.DataFrame, df_unfiltered: pd.DataFrame) -> None:
        """
        Starts an interactive session that allows the user to select specific columns to display and rows to expand.

        Args:
            df (pd.DataFrame): The DataFrame to display and interact with.
            df_unfiltered (pd.DataFrame): The original unfiltered DataFrame, used for expanding rows.

        Returns:
            None
        """
        # Ask the user which columns to display
        selected_columns_input = input("Enter the columns to display, separated by commas (see logged available columns): ")
        selected_columns = [column.strip() for column in selected_columns_input.split(",")]

        # Keep only the selected columns
        df = df[selected_columns]
        self.show_results(df)

        # Keep the session interactive, allow user to expand a row with iloc
        while True:
            row_number = input("Enter the number of the row you want to expand (or 'q' to quit): ")
            if row_number.lower() == 'q':
                break
            else:
                try:
                    row_number = int(row_number)
                    if row_number < len(df_unfiltered):
                        expanded_row = df_unfiltered.iloc[row_number].T.to_frame()
                        self.show_results(expanded_row)
                    else:
                        self.logger.warning(f"Row number {row_number} is out of range.")
                except ValueError:
                    self.logger.warning(f"Invalid row number: {row_number}")

    def show_results(self, df: pd.DataFrame) -> None:
        """
        Prints the DataFrame to the console in a markdown table format.

        Args:
            df (pd.DataFrame): The DataFrame to print.

        Returns:
            None
        """
        print(Fore.GREEN + df.to_markdown(headers='keys', tablefmt='fancy_grid') + Fore.RESET)


    def execute(self) -> None:
        """
        Main execution method of the Command class.

        Fetches the data, logs the results, and based on the provided arguments either exports the data,
        starts an interactive session, or simply shows the results with all columns.

        Returns:
            None
        """
        df = self.fetch_data()
        df_unfiltered = df.copy()
        if df is None:
            self.logger.info(f"No results found for {self.application} in the last {self.duration}.")
            return

        df = self.filter_columns(df)

        # Always log the results and available columns
        self.logger.info(f"Found {len(df)} results.")
        self.logger.info(f"Available columns: {', '.join(df.columns)}")

        # If export is set, export the data
        if self.args.export:
            self.export_data(df)
            return

        # If interactive argument is set, start interactive session
        if self.args.interactive:
            self.interactive_session(df, df_unfiltered)

        else:
            # Show the results with all columns if not in interactive mode
            self.show_results(df)

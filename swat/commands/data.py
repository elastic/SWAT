
import json

import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from swat.commands.base_command import BaseCommand


class Command(BaseCommand):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.service = build('admin', 'reports_v1', credentials=self.creds)
        self.duration = kwargs['args'][1]
        self.application = kwargs['args'][0]

    def fetch_data(self, filters=None):
        now = pd.Timestamp.now(tz="UTC")
        start_time = (now - pd.to_timedelta(self.duration)).isoformat()

        request = self.service.activities().list(userKey='all', applicationName=self.application, startTime=start_time)
        activities = []

        while request is not None:
            activities_result = request.execute()
            activities.extend(activities_result.get('items', []))
            request = self.service.activities().list_next(request, activities_result)

        df = pd.DataFrame(activities)

        if filters:
            for column, value in filters.items():
                df = df[df[column] == value]

        return df

    def execute(self):
        try:
            df = self.fetch_data()
            for i in range(df.shape[0]):
                row_as_dict = df.iloc[i].to_dict()
                print(json.dumps(row_as_dict, indent=2))
        except HttpError as error:
            self.logger.error(f"An error occurred: {error}")

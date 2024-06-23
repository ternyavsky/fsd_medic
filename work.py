import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, service_account
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
#
class GoogleCalendar:
    SCOPES = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events",
    ]
    FILE_PATH = ".credentials/credentials.json"

    def __init__(self) -> None:
        cred = service_account.Credentials.from_service_account_file(
            filename=self.FILE_PATH, scopes=self.SCOPES
        )
        delegate_cred = cred.with_subject(
            "poker-289@pre-calendar.iam.gserviceaccount.com"
        )
        self.service = build("calendar", "v3", credentials=delegate_cred)

    def get_calendars(self):
        return self.service.calendarList().list().execute()

    def add_calendar(self, id):
        calendar_list = {"id": id}
        return self.service.calendarList().insert(body=calendar_list).execute()

    def add_event(self, calendarId, body):
        return self.service.events().insert(calendarId=calendarId, body=body).execute()

    def get_events(self, calendarId):
        return self.service.events().list(calendarId=calendarId).execute()


event = {
    "summary": "Этo работает june",
    "location": "800 Howard St., San Francisco, CA 94103",
    "description": "A chance to hear more about Google's developer products.",
    "start": {
        "date": "2024-06-22",
    },
    "end": {
        "date": "2024-06-22",
    },
}

cal_id = "pppoker2015@gmail.com"

obj = GoogleCalendar()
# print(obj.add_calendar(cal_id))
event = obj.add_event(calendarId=cal_id, body=event)
events = obj.get_events(cal_id)
print(len(events["items"]))
print(events["items"])
# calendar_list = obj.service.calendarList().list().execute()
# print(obj.get_calendars())

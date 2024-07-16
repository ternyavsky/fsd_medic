from google.oauth2 import service_account
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendar:
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    FILE_PATH = "pre-recover-427415-3784e3fc5b1d.json"

    def __init__(self) -> None:
        cred = service_account.Credentials.from_service_account_file(
            filename=self.FILE_PATH, scopes=self.SCOPES
        )
        self.service = build("calendar", "v3", credentials=cred)

    def add_calendar(self, cal_id):
        cal_entry = {"id": cal_id}
        return self.service.calendarList().insert(body=cal_entry).execute()

    def add_event(self, cal_id, body):
        return self.service.events().insert(calendarId=cal_id, body=body).execute()


event = {
    "summary": "Temur",
    "location": "Абдусаймапов",
    "description": "Description",
    "start": {"date": "2024-07-13"},
    "end": {"date": "2024-07-13"},
}
obj = GoogleCalendar()
# obj.add_calendar(cal_id="calimur96@gmail.com")
# event = obj.add_event(cal_id="calimur96@gmail.com", body=event)
all_e = obj.service.events().list(calendarId="calimur96@gmail.com").execute()["items"]
# calendar_list = obj.service.calendarList().list().execute()
print(all_e)

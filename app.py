import streamlit as st
import pandas as pd
import gspread
import re
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ---------------- CONFIG ----------------
SHEET_URL = "https://docs.google.com/spreadsheets/d/1jis4IowMXM72jJUlz3Yanv2YBu7ilcvU/edit"
WORKSHEET_ID = 752189081
TIME_ROW_INDEX = 1  # Row 2 in sheet (0-indexed)
TIME_COL_RANGE = range(2, 9)  # C to I
TIMEZONE = "Asia/Kolkata"

SUBJECTS = [
    "Fintech-A","Fintech-B","BEDM-A","BEDM-B","Art-A","Art-B",
    "WH-A","WH-B","LETV","Film&Firm-A","Film&Firm-B","SHRM",
    "SCM-A","SCM-B","AIS","EB","AIAM-A","AIAM-B",
    "SA-A","SA-B","CSM","EM","I4TS"
]

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# ---------------- FUNCTIONS ----------------
def get_calendar_service():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return build("calendar", "v3", credentials=creds)

def load_sheet():
    gc = gspread.oauth()
    sh = gc.open_by_url(SHEET_URL)
    ws = sh.get_worksheet_by_id(WORKSHEET_ID)
    return ws

def parse_time_range(time_str):
    start, end = time_str.split("-")
    return start.strip(), end.strip()

def extract_subject_location(cell):
    match = re.match(r"(.*?)(?:\s*\((.*?)\))?$", cell)
    subject = match.group(1).strip()
    location = match.group(2) if match.group(2) else ""
    return subject, location

# ---------------- UI ----------------
st.title("📅 Term-6 Timetable → Google Calendar")

selected_subjects = st.multiselect("Select Subjects", SUBJECTS)
email = st.text_input("Google Calendar Email ID")

if st.button("Generate & Upload Schedule"):

    if not selected_subjects or not email:
        st.error("Please select subjects and enter email.")
        st.stop()

    ws = load_sheet()
    data = ws.get_all_values()

    time_slots = [data[TIME_ROW_INDEX][i] for i in TIME_COL_RANGE]

    events = []

    for r in range(2, len(data)):
        date_str = data[r][0]
        if not date_str:
            continue

        class_date = datetime.strptime(date_str, "%d/%m/%Y").date()

        for idx, c in enumerate(TIME_COL_RANGE):
            cell = data[r][c]
            if not cell:
                continue

            subject, location = extract_subject_location(cell)

            if subject not in selected_subjects:
                continue

            start_t, end_t = parse_time_range(time_slots[idx])

            start_dt = datetime.strptime(
                f"{date_str} {start_t}", "%d/%m/%Y %H:%M"
            )
            end_dt = datetime.strptime(
                f"{date_str} {end_t}", "%d/%m/%Y %H:%M"
            )

            events.append({
                "summary": subject,
                "location": location,
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat()
            })

    st.write("### Preview of Events")
    st.dataframe(events)

    service = get_calendar_service()

    for e in events:
        event_body = {
            "summary": e["summary"],
            "location": e["location"],
            "start": {"dateTime": e["start"], "timeZone": TIMEZONE},
            "end": {"dateTime": e["end"], "timeZone": TIMEZONE},
            "attendees": [{"email": email}],
        }
        service.events().insert(calendarId="primary", body=event_body).execute()

    st.success(f"✅ {len(events)} classes uploaded to Google Calendar!")

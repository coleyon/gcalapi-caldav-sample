import os
from datetime import datetime
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
from caldav.davclient import DAVClient
from ics import Calendar, Event
from ics.utils import get_arrow
from dateutil import parser
from dateutil.relativedelta import relativedelta
from ics.attendee import Attendee
from ics.organizer import Organizer

SCOPES = ['https://www.googleapis.com/auth/calendar.events.readonly', 'https://www.googleapis.com/auth/calendar.readonly']
API_ENDPOINT = 'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events?timeMin={time_min}&timeMax={time_max}&maxResults={max_results}'
SUBJECT = os.getenv('GOOGLE_CONTEXT_ID', default=None)
CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID', default='primary')
CREDENTIAL_FILE = os.getenv('GOOGLE_APP_CREDENTIALS', default=None)
CALDAV_URL = os.getenv('CALDAV_SERVER_URL')
CALDAV_USER = os.getenv('CALDAV_SERVER_USER')
CALDAV_PASS = os.getenv('CALDAV_SERVER_PASS')
CAL_NAME = os.getenv('CALDAV_SERVER_CALENDAR_NAME')

APIQUERY_DT_FMT = '%Y-%m-%dT%H:%M:%S-09:00'  # 2019-08-01T00:00:00-09:00
APIQUERY_MAX_RESULTS = int(os.getenv('APIQUERY_MAX_RESULTS', default=1000))
RANGE_OFFSET_MONTHS = int(os.getenv('RANGE_OFFSET_MONTHS', default=2))


def conv_arrow(datestr):
    '''Convert datetime format string to Arrow Object'''
    if datestr:
        return get_arrow(parser.parse(datestr))
    else:
        return None


def add_attendees(attendees, event):
    '''Add Attendees to event'''
    if attendees:
        for attendee in attendees:
            response_status = True if attendee.get('responseStatus') == 'accepted' else False
            event.add_attendee(Attendee(attendee.get('email'), response_status))


def date_or_time(attr):
    '''Get date or datetime from datetime type attribute'''
    if attr:
        return attr.get('dateTime') if attr.get('dateTime') else attr.get('date')
    else:
        return None


def generate_ics(events, timezone='Asia/Tokyo'):
    '''Generate CalDAV ics formatted events from Google API Responce data'''
    icals = []
    for event in events:
        if event.get('status') == 'cancelled':
            continue
        ics_event = Event(
            name=event.get('summary'),
            begin=conv_arrow(date_or_time(event.get('start'))),
            end=conv_arrow(date_or_time(event.get('end'))),
            # duration=None,
            uid=event.get('iCalUID'),
            description=event.get('description'),
            created=conv_arrow(event.get('created')),
            last_modified=conv_arrow(event.get('updated')),
            location=event.get('location'),
            url=event.get('htmlLink'),
            transparent=True if event.get('transparency') else False,
            alarms=None,
            # attendees=None,
            categories=set(),
            status=event.get('status'),
            organizer=Organizer(event.get('organizer').get('email')) if event.get('organizer') else None,
        )
        add_attendees(event.get('attendees'), ics_event)
        cal = Calendar()
        cal.events.add(ics_event)
        icals.append(str(cal))

    return icals


def get_gcals():
    '''Get Google Calendar API event Responces'''
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIAL_FILE, scopes=SCOPES).with_subject(SUBJECT)
    authed_session = AuthorizedSession(creds)
    time_min = datetime.utcnow() + relativedelta(months=-RANGE_OFFSET_MONTHS)
    time_max = datetime.utcnow() + relativedelta(months=+RANGE_OFFSET_MONTHS)
    response = authed_session.get(
        API_ENDPOINT.format(
            calendar_id=CALENDAR_ID,
            time_min=time_min.strftime(APIQUERY_DT_FMT),
            time_max=time_max.strftime(APIQUERY_DT_FMT),
            max_results=APIQUERY_MAX_RESULTS
        )
    ).json()
    timezone = response.get('timeZone')
    events = response.get('items', [])
    if events:
        return generate_ics(events, timezone)
    else:
        return None


def push_caldavs(icals):
    '''Regist ical formatted events to CalDAV server'''
    client = DAVClient(url=CALDAV_URL, username=CALDAV_USER, password=CALDAV_PASS)
    principal = client.principal()
    # get target calendar and remove all events
    calendar = [c for c in principal.calendars() if c.name == CAL_NAME][0]
    for event in calendar.events():
        event.delete()
    # put events
    if icals:
        for ical in icals:
            try:
                calendar.add_event(ical)
            except BaseException:
                print(ical)


def main(*args, **kwargs):
    '''entry point'''
    push_caldavs(get_gcals())


if __name__ == "__main__":
    main()

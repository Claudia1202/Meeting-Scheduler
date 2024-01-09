import os
from icalendar import Calendar, Event, vCalAddress, vText
import pytz
from datetime import datetime

# Create a calendar
cal = Calendar()

# Create an event
event = Event()
event.add('summary', 'Meditatii')
event.add('dtstart', datetime(2024, 2, 5, 10, 0, 0, tzinfo=pytz.utc))
event.add('dtend', datetime(2024, 2, 5, 12, 0, 0, tzinfo=pytz.utc))
event.add('dtstamp', datetime.now(pytz.utc))

# Adding participants
participants_emails = [
    "andreeadumi@yahoo.com",
    "johndoe@gmail.com"
]

for email in participants_emails:
    attendee = vCalAddress('MAILTO:' + email)
    attendee.params['ROLE'] = vText('REQ-PARTICIPANT')
    event.add('attendee', attendee, encode=0)

# Add event to the calendar
cal.add_component(event)

filepath = r'C:\Users\Claudia\Documents\Python-teme'
filename = "meditatii.ics"
new_path = os.path.join(filepath, filename)
# Write to file
with open(new_path, 'wb') as f:
    f.write(cal.to_ical())

print(f"ICS file created at {new_path}")

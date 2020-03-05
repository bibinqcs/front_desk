# -*- coding: utf-8 -*-
# Copyright (c) 2017, Quark Cyber Systems and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MeetingRoomReservation(Document):
	pass


@frappe.whitelist()
def get_meetings(start, end, filters=None):
	"""Returns events for Course Schedule Calendar view rendering.
	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Meeting Room Reservation", filters)

	data = frappe.db.sql("""select name, requested_by, room, subject,
			timestamp(schedule_date, from_time) as from_datetime,
			timestamp(schedule_date, to_time) as to_datetime,
			notes, 0 as 'allDay'
		from `tabMeeting Room Reservation`
		where ( schedule_date between %(start)s and %(end)s )
		{conditions}""".format(conditions=conditions), {
			"start": start,
			"end": end
			}, as_dict=True, update={"allDay": 0})
	return data

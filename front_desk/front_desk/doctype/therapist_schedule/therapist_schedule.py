# -*- coding: utf-8 -*-
# Copyright (c) 2017, Quark Cyber Systems and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TherapistSchedule(Document):
	def validate(self):
		self.set_title()

	def set_title(self):
		"""Set document Title"""
		self.title = self.student_name + " in " + self.room_name



@frappe.whitelist()
def get_therapist_schedule(start, end, filters=None):
	"""Returns events for Course Schedule Calendar view rendering.
	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Therapist Schedule", filters)

	data = frappe.db.sql("""select name, title,
			timestamp(schedule_date, from_time) as from_datetime,
			timestamp(schedule_date, to_time) as to_datetime, 0 as 'allDay'
		from `tabTherapist Schedule`
		where ( schedule_date between %(start)s and %(end)s )
		{conditions}""".format(conditions=conditions), {
			"start": start,
			"end": end
			}, as_dict=True, update={"allDay": 0})
	return data

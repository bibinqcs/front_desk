# -*- coding: utf-8 -*-
# Copyright (c) 2017, Quark Cyber Systems and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate

class StudentSchedule(Document):
	pass


@frappe.whitelist()
def get_teacher_schedule(start, end, filters=None):
	"""Returns events for Course Schedule Calendar view rendering.
	:param start: Start date-time.
	:param end: End date-time.
	:param filters: Filters (JSON).
	"""
	from frappe.desk.calendar import get_event_conditions
	conditions = get_event_conditions("Teacher Schedule", filters)

	data = frappe.db.sql("""select name, student_name, section, color, notes,
			from_time,
			to_time,
			0 as 'allDay'
		from `tabTeacher Schedule`
		where ( from_time between %(start)s and %(end)s )
		{conditions}""".format(conditions=conditions), {
			"start": start,
			"end": end
			}, as_dict=True, update={"allDay": 0})
	return data

from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, today

def execute():
	frappe.reload_doc("HR", "doctype", "Attendance")
	generate_attendance_entries()

def get_attendance_records():
	return frappe.db.get_list('Attendance', filters={
		'attendance_date': ['>', '2020-03-29']
		}, fields=['shift_type', 'shift', 'time_in', 'start_time', 'late_in', 'time_out', 'end_time', 'early_out', 'total_working_hours', 'total_time', 'diff_working_hours'
		], order_by='attendance_date ASC')

def generate_attendance_entries():
	attendance_list = get_attendance_records()
	for attendance in attendance_list:
		copy_shift_details()

def copy_shift_details():
	frappe.db.sql("""
		UPDATE `tabAttendance`
		SET `shift` = `shift_type`
	""")

def update_shift_type_blank():
		frappe.db.sql("""
		UPDATE `tabAttendance`
		SET `shift_type` = NULL
	""")

def update_time_in_blank():
		frappe.db.sql("""
		UPDATE `tabAttendance`
		SET `time_in` = NULL
	""")
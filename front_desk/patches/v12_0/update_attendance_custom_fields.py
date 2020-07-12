from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, today

def execute():
	frappe.reload_doc("HR", "doctype", "Attendance")



def generate_absent_records():
	absent_records = get_absent_attendance()

	for absent in absent_records:
		if frappe.db.exists("Attendance", {'status': 'Absent'}):
			update_timestamp_records()

def update_timestamp_records():
	frappe.db.sql("""UPDATE `tabAttendance` SET `time_in` = NULL""")
	frappe.db.sql("""UPDATE `tabAttendance` SET `time_out` = NULL""")
	frappe.db.sql("""UPDATE `tabAttendance` SET `start_time` = NULL""")
	frappe.db.sql("""UPDATE `tabAttendance` SET `end_time` = NULL""")
	frappe.db.sql("""UPDATE `tabAttendance` SET `late_in` = NULL""")
	frappe.db.sql("""UPDATE `tabAttendance` SET `early_out` = NULL""")
	frappe.db.sql("""UPDATE `tabAttendance` SET `total_working_hours` = NULL""")
	frappe.db.sql("""UPDATE `tabAttendance` SET `total_time` = NULL""")
	frappe.db.sql("""UPDATE `tabAttendance` SET `diff_working_hours` = NULL""")
	return

def get_half_day_attendance():
	return frappe.db.get_all('Attendance',
		filters={
			'status': 'Half Day'
		},
		fields=['time_in', 'start_time', 'late_in', 'time_out', 'end_time', 'early_out', 'total_working_hours', 'total_time', 'diff_working_hours', 'attendance_date'],
		order_by='attendance_date DESC'
	)

def get_absent_attendance():
	return frappe.db.get_all('Attendance',
		filters={
			'status': 'Absent'
		},
		fields=['time_in', 'start_time', 'late_in', 'time_out', 'end_time', 'early_out', 'total_working_hours', 'total_time', 'diff_working_hours', 'attendance_date'],
		order_by='attendance_date DESC'
	)

def get_leave_attendance():
	return frappe.db.get_all('Attendance',
		filters={
			'status': 'On Leave'
		},
		fields=['time_in', 'start_time', 'late_in', 'time_out', 'end_time', 'early_out', 'total_working_hours', 'total_time', 'diff_working_hours', 'attendance_date'],
		order_by='attendance_date DESC'
	)

def get_biostar_attendance():
	return frappe.db.get_all('Attendance',
		filters={
			'status': 'Present',
			'attendance_date': ['>', '2020-03-29']
		},
		fields=['time_in', 'start_time', 'late_in', 'time_out', 'end_time', 'early_out', 'total_working_hours', 'total_time', 'diff_working_hours', 'attendance_date'],
		order_by='attendance_date DESC'
	)
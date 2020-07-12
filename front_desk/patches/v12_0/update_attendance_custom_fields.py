from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, today

def execute():
	frappe.reload_doc("HR", "doctype", "Attendance")

def update_timestamp_records():

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

def generate_attendance_entries():
	attendance_list = get_biostar_attendance_records()
	for attendance in attendance_list:
		update_time_in_blank()
		update_time_out_blank()
		update_start_time_blank()
		update_end_time_blank()
		update_late_in_blank()
		update_early_out_blank()
		update_total_time_blank()
		update_total_working_hours_blank()
		update_diff_working_hours_blank()
		if frappe.get_meta("Attendance").has_field("shift_type"):
			update_shift_type_blank()

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

def update_time_out_blank():
		frappe.db.sql("""
		UPDATE `tabAttendance`
		SET `time_out` = NULL
	""")

def update_start_time_blank():
		frappe.db.sql("""
		UPDATE `tabAttendance`
		SET `start_time` = NULL
	""")

def update_end_time_blank():
		frappe.db.sql("""
		UPDATE `tabAttendance`
		SET `end_time` = NULL
	""")

def update_late_in_blank():
		frappe.db.sql("""
		UPDATE `tabAttendance`
		SET `late_in` = NULL
	""")

def update_early_out_blank():
		frappe.db.sql("""
		UPDATE `tabAttendance`
		SET `early_out` = NULL
	""")

def update_total_working_hours_blank():
		frappe.db.sql("""
		UPDATE `tabAttendance`
		SET `total_working_hours` = NULL
	""")

def update_total_time_blank():
		frappe.db.sql("""
		UPDATE `tabAttendance`
		SET `total_time` = NULL
	""")

def update_diff_working_hours_blank():
		frappe.db.sql("""
		UPDATE `tabAttendance`
		SET `diff_working_hours` = NULL
	""")

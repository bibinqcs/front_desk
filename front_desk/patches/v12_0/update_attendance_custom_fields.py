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
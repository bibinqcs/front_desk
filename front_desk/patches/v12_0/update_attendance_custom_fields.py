from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, today
import datetime

def execute():
	frappe.reload_doc("HR", "doctype", "Attendance")
	update_half_day_records()
	update_absent_records()
	update_on_leave_records()
	update_employee_checkin_records()

def update_employee_checkin_records():
	attendance_records = get_attendance()
	for attendance in attendance_records:
		if attendance.status == 'Present' and attendance.attendance_date > datetime.date(2020,3,29):
			update_timestamp_records(attendance)
			frappe.db.sql("""UPDATE `tabAttendance` SET `shift_type` = NULL WHERE name = %s""", attendance.name)

def update_half_day_records():
	attendance_records = get_attendance()
	for attendance in attendance_records:
		if attendance.status == 'Half Day':
			update_timestamp_records(attendance)

def update_absent_records():
	attendance_records = get_attendance()
	for attendance in attendance_records:
		if attendance.status == 'Absent':
			update_timestamp_records(attendance)

def update_on_leave_records():
	attendance_records = get_attendance()
	for attendance in attendance_records:
		if attendance.status == 'On Leave':
			update_timestamp_records(attendance)

def update_timestamp_records(attendance):
	frappe.db.sql("""UPDATE `tabAttendance` SET `time_in` = NULL WHERE name = %s""", attendance.name)
	frappe.db.sql("""UPDATE `tabAttendance` SET `time_out` = NULL WHERE name = %s""", attendance.name)
	frappe.db.sql("""UPDATE `tabAttendance` SET `start_time` = NULL WHERE name = %s""", attendance.name)
	frappe.db.sql("""UPDATE `tabAttendance` SET `end_time` = NULL WHERE name = %s""", attendance.name)
	frappe.db.sql("""UPDATE `tabAttendance` SET `late_in` = NULL WHERE name = %s""", attendance.name)
	frappe.db.sql("""UPDATE `tabAttendance` SET `early_out` = NULL WHERE name = %s""", attendance.name)
	frappe.db.sql("""UPDATE `tabAttendance` SET `total_working_hours` = NULL WHERE name = %s""", attendance.name)
	frappe.db.sql("""UPDATE `tabAttendance` SET `diff_working_hours` = NULL WHERE name = %s""", attendance.name)
	frappe.db.sql("""UPDATE `tabAttendance` SET `total_time` = NULL WHERE name = %s""", attendance.name)

def get_attendance():
	return frappe.db.get_all('Attendance',
		fields=['name', 'status', 'shift_type', 'time_in', 'start_time', 'late_in', 'time_out', 'end_time', 'early_out', 'total_working_hours', 'total_time', 'diff_working_hours', 'attendance_date'],
		order_by='attendance_date DESC'
	)
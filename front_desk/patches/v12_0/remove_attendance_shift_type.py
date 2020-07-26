from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, today
import datetime

def execute():
	frappe.reload_doc("HR", "doctype", "Attendance")
	update_shift_records()

def update_shift_records():
	attendance_records = get_attendance()
	for attendance in attendance_records:
		if not attendance.shift and attendance.shift_type and attendance.attendance_date < datetime.date(2020,3,30):
			update_shift(attendance)

def update_shift(attendance):
	frappe.db.sql("""UPDATE 
			`tabAttendance` 
		SET
			`shift` = `shift_type` 
		WHERE name = %s""", attendance.name)

def get_attendance():
	return frappe.db.get_all('Attendance',
		fields=['name', 'status', 'shift_type', 'shift', 'attendance_date'],
		order_by='attendance_date DESC'
	)

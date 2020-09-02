from __future__ import unicode_literals
import frappe
from frappe.utils import getdate, today
import datetime

def execute():
	frappe.reload_doc("HR", "doctype", "Employee Checkin")
	unlink_employee_checkin_attendance_records()

def unlink_employee_checkin_attendance_records():
	checkin_records = get_employee_checkin()
	for checkin in checkin_records:
		if checkin.time > datetime.datetime(2020,6,1):
			frappe.db.sql("""UPDATE 
					`tabEmployee Checkin` 
				SET 
					`attendance` = NULL,
					`skip_auto_attendance` = '0'
				WHERE name = %s""", checkin.name) 

def get_employee_checkin():
    return frappe.db.get_all('Employee Checkin',
        fields=['name', 'attendance', 'time'],
		order_by='time DESC'
    )

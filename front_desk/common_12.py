# -*- coding: utf-8 -*-
# Copyright (c) 2015, vivek and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, requests, urllib3, json, datetime, dateutil.parser, urllib, dateutil.relativedelta
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import flt, add_days, date_diff, get_request_site_address, formatdate, getdate
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from json import dumps
from datetime import date, timedelta, datetime
from frappe.utils.response import json_handler
from dateutil.relativedelta import relativedelta


def remove_custom_field_kanban_column():
    if frappe.db.exists("Custom Field", "Work Order-kanban_column"):
        frappe.delete_doc("Custom Field", "Work Order-kanban_column")

def redundant_attendance_custom_fields(attendance, method):
    attendance.set('time_in',"")
    attendance.set('time_out',"")
    attendance.set('start_time',"")
    attendance.set('end_time',"")
    attendance.set('late_in',"")
    attendance.set('early_out',"")
    attendance.set('total_working_hours',"")
    attendance.set('diff_working_hours',"")
    attendance.set('total_time',"")
    attendance.set('total_time',"")
    attendance.set('shift_type',"")

@frappe.whitelist()
def mark_attendance():
    today = datetime.today()

    #yt = datetime.combine(yesterday, datetime.min.time())
    for emp in frappe.get_all("Employee", fields={"name", "employee_name", "date_of_joining"},filters={"status":"Active"}):
        #fmonth = today
        fmonth = datetime(today.year, today.month, 1)

        g = 1
        fmonth = fmonth - dateutil.relativedelta.relativedelta(months=1)
        while g <= 31:
            if fmonth.date() >= emp.date_of_joining:
                ip = frappe.get_all("Attendance", "name", {"attendance_date": fmonth, "employee":emp.name})
                if not ip:
                    ac = frappe.get_all("Biometric Access Log", fields={"date", "employee"}, filters={"employee":emp.name, "only_date":("=",fmonth)}, order_by='date')
                    if ac:
                        attendance = frappe.new_doc("Attendance")
                        attendance.employee = emp.name
                        attendance.attendance_date = fmonth
                        attendance.status = "Present"
                        attendance.company = "Dubai Autism Center"
                        frappe.errprint(ac)
                        frappe.errprint(ac[0])
                        frappe.errprint(ac[-1])
                        attendance.time_in = ac[0]["date"].time()
                        attendance.time_out = ac[-1]["date"].time()
                        attendance.total_working_hours = datetime.strptime(str(attendance.time_out),"%H:%M:%S") - datetime.strptime(str(attendance.time_in),"%H:%M:%S")
                        attendance.save()
                        if datetime.strptime(str(attendance.start_time),"%H:%M:%S") > datetime.strptime(str(attendance.time_in),"%H:%M:%S"):
                            attendance.late_in = 0
                        if datetime.strptime(str(attendance.start_time),"%H:%M:%S") < datetime.strptime(str(attendance.time_in),"%H:%M:%S"):
                            attendance.late_in = datetime.strptime(str(attendance.time_in),"%H:%M:%S") - datetime.strptime(str(attendance.start_time),"%H:%M:%S")
                        if datetime.strptime(str(attendance.end_time),"%H:%M:%S") < datetime.strptime(str(attendance.time_out),"%H:%M:%S"):
                            attendance.early_out = 0
                        if datetime.strptime(str(attendance.end_time),"%H:%M:%S") > datetime.strptime(str(attendance.time_out),"%H:%M:%S"):
                            attendance.early_out = datetime.strptime(str(attendance.end_time),"%H:%M:%S") - datetime.strptime(str(attendance.time_out),"%H:%M:%S")
                        if datetime.strptime(str(attendance.total_working_hours),"%H:%M:%S") > datetime.strptime(str(attendance.total_time),"%H:%M:%S"):
                            attendance.diff_working_hours = 0
                        if datetime.strptime(str(attendance.total_working_hours),"%H:%M:%S") < datetime.strptime(str(attendance.total_time),"%H:%M:%S"):
                            attendance.diff_working_hours = datetime.strptime(str(attendance.total_time),"%H:%M:%S") - datetime.strptime(str(attendance.total_working_hours),"%H:%M:%S")
                        attendance.submit()

            fmonth = fmonth + timedelta(days=1)
            g += 1

def datetime_to_iso(date):
    """
    Converts a datetime to the ISO8601 format, like: 2014-05-20T06:11:41.733900.
    Parameters:
    date -- a `datetime` instance.
    """
    date = datetime.combine(date, datetime.min.time())
    return date.isoformat()

def jsonDefault(object):
    return object.__dict__

def salary_slip_deduction(salary_slip, method):
    if not salary_slip.deductions:
        salary_slip.set("deductions", [])
    late_mins = timedelta(0,0,0)
    early_mins = timedelta(0,0,0)
    if not salary_slip.cancel_tardiness:
        for d in frappe.get_all("Attendance", filters={"employee":salary_slip.employee, "status":"Present"}, fields=["name", "late_in", "early_out", "time_in", "start_time", "time_out", "end_time", "attendance_date"]):
            if getdate(salary_slip.start_date) <= d.attendance_date <= getdate(salary_slip.end_date):
                if d.start_time and d.time_in and d.time_in > d.start_time:
                    late_mins += d.time_in - d.start_time
                if d.end_time and d.time_out and d.time_out < d.end_time:
                     early_mins += d.end_time - d.time_out


        if late_mins.total_seconds() / 60 > 30 and late_mins.total_seconds() / 60 < 180:
            ssa = frappe.db.get_value("Salary Structure Assignment", filters={"salary_structure":"Default", "employee":salary_slip.employee})
            ssadoc = frappe.get_doc("Salary Structure Assignment", ssa)
            amt = ssadoc.base / 60
            salary_slip.append("deductions",{
                "salary_component":"Tardiness Deduction - Late In",
                "amount": amt

            })
        elif late_mins.total_seconds() / 60 > 180:
            ssa = frappe.db.get_value("Salary Structure Assignment", filters={"salary_structure":"Default", "employee":salary_slip.employee})
            ssadoc = frappe.get_doc("Salary Structure Assignment", ssa)
            amt = ssadoc.base / 30
            salary_slip.append("deductions",{
                "salary_component":"Tardiness Deduction - Late In",
                "amount": amt

            })
        if early_mins.total_seconds() / 60 > 30 and early_mins.total_seconds() / 60 < 180:
            ssa = frappe.db.get_value("Salary Structure Assignment", filters={"salary_structure":"Default", "employee":salary_slip.employee})
            ssadoc = frappe.get_doc("Salary Structure Assignment", ssa)
            amt = ssadoc.base / 60
            salary_slip.append("deductions",{
                "salary_component":"Tardiness Deduction - Early Out",
                "amount": amt

            })
        elif early_mins.total_seconds() / 60 > 180:
            ssa = frappe.db.get_value("Salary Structure Assignment", filters={"salary_structure":"Default", "employee":salary_slip.employee})
            ssadoc = frappe.get_doc("Salary Structure Assignment", ssa)
            amt = ssadoc.base / 30
            salary_slip.append("deductions",{
                "salary_component":"Tardiness Deduction - Early Out",
                "amount": amt

            })
        salary_slip.calculate_net_pay()
#        frappe.errprint(amt)

def manage_staff_student_permission(student_group, method):
    sg = frappe.get_doc("Student Group", student_group.name)

    #delete previous user Permissions
    for st in sg.student_class:

        frappe.db.sql("""delete from `tabUser Permission` where for_value = %(voucher_no)s""", {'voucher_no': st.student})
    #assign new user permission
    for staff in sg.educators:
        emp = frappe.get_doc("Employee", staff.employee)
        frappe.msgprint(emp.user_id)
        for st in sg.student_class:
            up = frappe.new_doc("User Permission")
            up.user = emp.user_id
            up.allow = "Student"
            up.for_value = st.student
            up.allow_for_all_roles = 0
            up.save()

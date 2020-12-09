# -*- coding: utf-8 -*-
# Copyright (c) 2020, Quark Cyber Systems and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import json
import dateutil.parser
import dateutil.relativedelta
from frappe.model.document import Document
from frappe.utils import today, getdate, get_time
from datetime import timedelta, datetime
from erpnext.hr.doctype.holiday_list.holiday_list import is_holiday


class SupremaBiometricDeviceIntegration(Document):
    pass


@frappe.whitelist()
def api_hourly_sync():
    hourly_enabled = frappe.db.get_single_value('Suprema Biometric Device Integration', 'hourly_sync')
    if hourly_enabled == 1:
        hourly_id_sync()
        hourly_fp_sync()


def hourly_id_sync():
    json_data = api_payload(today(), today(), "4102")
    new_biometric_log(json_data)


def hourly_fp_sync():
    json_data = api_payload(today(), today(), "4865")
    new_biometric_log(json_data)


@frappe.whitelist()
def api_manual_sync(from_date, to_date, event_code):
    json_data = api_payload(from_date, to_date, event_code)
    new_biometric_log(json_data)


def new_biometric_log(json_data):
    for data in json_data["EventCollection"]["rows"]:
        existing_record = frappe.get_value('Biometric Access Log', dict(
            id_index=data["index"],
            server_datetime=iso_datetime_trim(data["server_datetime"])
        ))
        if not existing_record:
            if frappe.db.get_value("Employee", {"name": data["user_id"]["user_id"]}):
                new_bal = frappe.new_doc("Biometric Access Log")
                new_bal.id_index = data["index"]
                new_bal.record_id = data["id"]
                new_bal.date = iso_date_trim(data["datetime"])
                new_bal.datetime = add_tz(data["timezone"]["hour"], data["datetime"])
                new_bal.server_datetime = iso_datetime_trim(data["server_datetime"])
                new_bal.device_id = data["device_id"]["id"]
                new_bal.device_id_name = data["device_id"]["name"]
                new_bal.employee = data["user_id"]["user_id"]
                new_bal.save()


def api_payload(from_date, to_date, event_code):
    session_id = api_session_id()
    server_url = suprema_api_info()[0]
    url = server_url + "/api/events/search"
    starttime = from_date + "T00:00:00.00Z"
    endtime = to_date + "T23:59:59.99Z"
    payload_search_query = {
        "Query": {
            "limit": 5000,
            "conditions": [
                {
                    "column": "event_type_id.code",
                    "operator": 0,
                    "values": [
                        event_code
                        ]
                },
                {
                    "column": "datetime",
                    "operator": 3,
                    "values": [
                        starttime,
                        endtime
                    ]
                }
            ],
            "orders": [
                {
                    "column": "datetime",
                    "descending": "false"
                }
            ]
        }
    }
    payload = json.dumps(payload_search_query, default=jsonDefault)
    headers = {
        'bs-session-id': session_id,
        'Content-Type': 'application/json'
    }
    r = requests.session()
    t = r.post(url, data=payload, headers=headers, verify=False)
    json_data = json.loads(t.text)
    return json_data


def api_session_id():
    server_url, login_id, login_password = suprema_api_info()
    url = server_url + "/api/login"
    payload_login = {
        "User": {
            "login_id": login_id,
            "password": login_password
        }
    }
    payload_l = json.dumps(payload_login, default=jsonDefault)
    headers_l = {
        'Content-Type': 'application/json'
        }
    response = requests.request("POST", url, headers=headers_l, data=payload_l, verify=False)
    session_id = response.headers["bs-session-id"]
    return session_id


def suprema_api_info():
    api = frappe.get_doc('Suprema Biometric Device Integration')
    server_url = api.server_url
    login_id = api.username
    login_password = api.password
    return server_url, login_id, login_password


def jsonDefault(object):
    return object.__dict__


def add_tz(tz, json_datetime):
    """
    Add Timezone hour
    """
    formatted_iso_date = iso_datetime_trim(json_datetime)
    tzhour = int(tz)
    add_tzhour = timedelta(hours=tzhour)
    tz_datetime = formatted_iso_date + add_tzhour
    return tz_datetime


def iso_date_trim(json_date):
    """
    Trims YYYY-MM-DDThh:mm:ss.ffZ to %Y-%m-%d
    """
    iso_date = getdate(json_date)
    return iso_date


def iso_datetime_trim(json_datetime):
    """
    Trims YYYY-MM-DDThh:mm:ss.ffZ to "%Y-%m-%d %H:%M:%S"
    """
    iso_datetime = dateutil.parser.isoparse(json_datetime)
    string_datetime = str(iso_datetime)
    trim_datetime = string_datetime.split('+')[0]
    formatted_datetime = datetime.strptime(str(trim_datetime), "%Y-%m-%d %H:%M:%S")
    return formatted_datetime


@frappe.whitelist()
def daily_attendance():
    daily_enabled = frappe.db.get_single_value('Suprema Biometric Device Integration', 'daily_attendance')
    if daily_enabled == 1:
        employee_details = frappe.get_all('Employee', filters={
                                'status': 'Active'
                            },
                            fields=['name', 'employee_name', 'date_of_joining', 'default_shift', 'holiday_list']
                        )
        for employee in employee_details:
            attendance_date = getdate(today()) - timedelta(days=1)
            attendance_record(employee, attendance_date)


@frappe.whitelist()
def mark_attendance(att_from_date, att_to_date):
    employee_details = frappe.get_all('Employee', filters={
                        'status': 'Active'
                    },
                    fields=['name', 'employee_name', 'date_of_joining', 'default_shift', 'holiday_list']
                )
    for employee in employee_details:
        attendance_date = getdate(att_from_date)
        diff = getdate(att_to_date) - getdate(att_from_date)
        g = 1
        while g <= diff.days:
            attendance_record(employee, attendance_date)
            attendance_date = attendance_date + timedelta(days=1)
            g += 1


def attendance_record(employee, attendance_date):
    if attendance_date >= employee.date_of_joining:
        if not frappe.db.exists({'doctype': 'Attendance', 'employee': employee.name, 'attendance_date': attendance_date}):
            biometric_records = frappe.get_all('Biometric Access Log', filters={
                'employee': employee.name,
                'date': ['=', attendance_date]
                },
                fields=['datetime', 'employee'],
                order_by='datetime'
            )
            if biometric_records:
                time_in = get_time(biometric_records[0]["datetime"])
                time_out = get_time(biometric_records[-1]["datetime"])
                check_total_working_hours(employee, attendance_date, time_in, time_out)
            else:
                auto_absent(employee, attendance_date)


def auto_absent(employee, attendance_date):
    auto_absent = frappe.db.get_single_value('Suprema Biometric Device Integration', 'auto_absent')
    if auto_absent == 1:
        absent_grace = frappe.db.get_single_value('Suprema Biometric Device Integration', 'absent_grace')
        holiday_list = employee.holiday_list
        grace_date = attendance_date - timedelta(days=absent_grace)
        grace_date_parsed = getdate(grace_date)
        if getdate(grace_date) > getdate("2020-08-31"):
            if not frappe.db.exists({'doctype': 'Attendance', 'employee': employee.name, 'attendance_date': grace_date}):
                if not is_holiday(holiday_list, grace_date_parsed):
                    mark_absent(employee, grace_date)


def mark_absent(employee, attendance_date):
    attendance = frappe.new_doc('Attendance')
    attendance.employee = employee.name
    attendance.attendance_date = attendance_date
    attendance.status = 'Absent'
    attendance.company = 'Dubai Autism Center'
    attendance.shift = employee.default_shift
    attendance.set('time_in', "")
    attendance.set('time_out', "")
    attendance.set('late_in', "")
    attendance.set('early_out', "")
    attendance.set('total_working_hours', "")
    attendance.set('diff_working_hours', "")
    attendance.set('start_time', "")
    attendance.set('end_time', "")
    attendance.set('total_time', "")
    attendance.submit()


def check_total_working_hours(employee, attendance_date, time_in, time_out):
    total_hours = formatted_time(time_out) - formatted_time(time_in)
    diff_hours = total_hours.total_seconds() / 3600
    if int(diff_hours) > 0:
        new_attendance(employee, attendance_date, time_in, time_out, total_hours)
    else:
        auto_attendance_request = frappe.db.get_single_value('Suprema Biometric Device Integration', 'auto_attendance_request')
        if auto_attendance_request == 1:
            new_attendance_request(employee, attendance_date)
        else:
            missed_punch(employee, attendance_date, time_in, time_out)


def missed_punch(employee, attendance_date, time_in, time_out):
    attendance = frappe.new_doc('Attendance')
    attendance.employee = employee.name
    attendance.attendance_date = attendance_date
    attendance.status = 'Present'
    attendance.company = 'Dubai Autism Center'
    attendance.shift = employee.default_shift
    attendance.time_in = time_in
    attendance.time_out = time_out
    attendance.set('missed_punch_data', 1)
    attendance.set('late_in', "")
    attendance.set('early_out', "")
    attendance.set('total_working_hours', "")
    attendance.set('diff_working_hours', "")
    attendance.save()


def new_attendance_request(employee, attendance_date):
    if not frappe.db.exists({'doctype': 'Attendance Request', 'employee': employee.name, 'from_date': attendance_date}):
        new_ar = frappe.new_doc('Attendance Request')
        new_ar.employee = employee.name
        new_ar.company = 'Dubai Autism Center'
        new_ar.from_date = attendance_date
        new_ar.to_date = attendance_date
        new_ar.reason = 'Missed Punch Data / Exception'
        new_ar.save()


def new_attendance(employee, attendance_date, time_in, time_out, total_hours):
    attendance = frappe.new_doc('Attendance')
    attendance.employee = employee.name
    attendance.attendance_date = attendance_date
    attendance.status = 'Present'
    attendance.company = 'Dubai Autism Center'
    attendance.shift = employee.default_shift
    attendance.time_in = time_in
    attendance.time_out = time_out
    attendance.total_working_hours = total_hours
    attendance.save()
    suprema_calculate_tardiness(attendance)
    attendance.submit()


def suprema_calculate_tardiness(attendance):
    if formatted_time(attendance.time_in) > formatted_time(attendance.start_time):
        attendance.set('late_entry', 1)
        attendance.late_in = formatted_time(attendance.time_in) - formatted_time(attendance.start_time)
    else:
        attendance.set('late_in', "")
    if formatted_time(attendance.end_time) > formatted_time(attendance.time_out):
        attendance.set('early_exit', 1)
        attendance.early_out = formatted_time(attendance.end_time) - formatted_time(attendance.time_out)
    else:
        attendance.set('early_out', "")
    if formatted_time(attendance.total_time) > formatted_time(attendance.total_working_hours):
        attendance.diff_working_hours = formatted_time(attendance.total_time) - formatted_time(attendance.total_working_hours)
    else:
        attendance.set('diff_working_hours', "")


def formatted_time(time):
    string_time = str(time)
    trimmed_time = string_time.split(".")[0]
    format_time = datetime.strptime(str(trimmed_time), "%H:%M:%S")
    return format_time


def attendance_custom_validate(attendance, method):
    if not attendance.status == 'Present' or attendance.attendance_request:
        attendance.set('time_in', "")
        attendance.set('time_out', "")
        attendance.set('late_in', "")
        attendance.set('early_out', "")
        attendance.set('total_working_hours', "")
        attendance.set('diff_working_hours', "")


def manual_tardiness(attendance, method):
    time_in = attendance.time_in
    time_out = attendance.time_out
    total_hours = formatted_time(time_out) - formatted_time(time_in)
    attendance.set('total_working_hours', total_hours)
    suprema_calculate_tardiness(attendance)


def salary_slip_deduction(salary_slip, method):
    base = base_salary(salary_slip)
    salary_slip.set('gross_pay_qcs', base)
    get_leave_details(salary_slip)
    if not salary_slip.deductions:
        salary_slip.set("deductions", [])
        frappe.errprint("if not salary_slip.deductions")
    if not salary_slip.cancel_tardiness:
        calculate_tardiness(salary_slip)
        frappe.errprint("if not salary_slip.cancel_tardiness")
    if not salary_slip.cancel_absent_days:
        calculate_absent_days(salary_slip)
        frappe.errprint("if not salary_slip.cancel_absent_days")


def get_leave_details(salary_slip):
    employee = salary_slip.employee
    start_date = getdate(salary_slip.start_date)
    end_date = getdate(salary_slip.end_date)
    total_annual_leave = leave_days_count(employee, start_date, end_date, 'Annual Leave')
    salary_slip.set('total_annual_leave', total_annual_leave)
    total_sick_leave = leave_days_count(employee, start_date, end_date, 'Sick Leave')
    salary_slip.set('total_sick_leave', total_sick_leave)
    total_without_pay = leave_days_count(employee, start_date, end_date, 'Without Pay')
    salary_slip.set('total_without_pay', total_without_pay)
    total_compassionate_leave = leave_days_count(employee, start_date, end_date, 'Compassionate Leave')
    salary_slip.set('total_compassionate_leave', total_compassionate_leave)
    total_maternity_leave = leave_days_count(employee, start_date, end_date, 'Maternity Leave')
    salary_slip.set('total_maternity_leave', total_maternity_leave)
    total_education_leave = leave_days_count(employee, start_date, end_date, 'Education')
    salary_slip.set('total_education_leave', total_education_leave)


def leave_days_count(employee, start_date, end_date, leave_type='None'):
    leave_days = 0
    leave_days_list = frappe.db.get_list('Attendance', filters=[
                        ['employee', '=', employee],
                        ['docstatus', '=', 1],
                        ['status', '=', 'On Leave'],
                        ['leave_type', '=', leave_type],
                        ['attendance_date', '<=', end_date],
                        ['attendance_date', '>=', start_date]
                    ],
                    fields=['name']
                    )
    leave_days = len(leave_days_list)
    return leave_days


def calculate_tardiness(salary_slip):
    late_mins = timedelta(0, 0, 0)
    early_mins = timedelta(0, 0, 0)
    attendance_details = frappe.get_all("Attendance", filters={
                                "employee": salary_slip.employee,
                                "status": "Present"
                                },
                                fields=["name", "late_in", "early_out", "time_in", "start_time", "time_out", "end_time", "attendance_date"]
                            )
    for d in attendance_details:
        if getdate(salary_slip.start_date) <= d.attendance_date <= getdate(salary_slip.end_date):
            if d.start_time and d.time_in and d.time_in > d.start_time:
                late_mins += d.time_in - d.start_time
            if d.end_time and d.time_out and d.time_out < d.end_time:
                early_mins += d.end_time - d.time_out
    check_tardiness(salary_slip, late_mins, "Tardiness Deduction - Late In")
    total_tardiness(salary_slip, late_mins, 'late_mins')
    check_tardiness(salary_slip, early_mins, "Tardiness Deduction - Early Out")
    total_tardiness(salary_slip, early_mins, 'early_mins')
    salary_slip.calculate_net_pay()


def check_tardiness(salary_slip, tardiness, salary_component):
    tardiness_mins = tardiness.total_seconds() / 60
    if tardiness_mins > 30 and tardiness_mins < 180:
        base = base_salary(salary_slip)
        amt = half_day_deduction(base)
        add_deduction(salary_slip, amt, salary_component)
    elif tardiness_mins > 180:
        base = base_salary(salary_slip)
        amt = full_day_deduction(base)
        add_deduction(salary_slip, amt, salary_component)


def total_tardiness(salary_slip, tardiness_time, ss_field='None'):
    total_tardiness_min = tardiness_time.total_seconds() / 60
    if total_tardiness_min < 1439:
        salary_slip.set(ss_field, tardiness_time)
    elif total_tardiness_min > 1439:
        salary_slip.set(ss_field, timedelta(hours=23, minutes=59, seconds=59))


def calculate_absent_days(salary_slip):
    start_date = getdate(salary_slip.start_date)
    end_date = getdate(salary_slip.end_date)
    absent_days_list = frappe.db.get_list('Attendance', filters=[
                        ['employee', '=', salary_slip.employee],
                        ['docstatus', '=', 1],
                        ['status', '=', 'Absent'],
                        ['attendance_date', '<=', end_date],
                        ['attendance_date', '>=', start_date]
                    ],
                    fields=['name']
                    )
    absent_days = len(absent_days_list)
    salary_slip.set('total_absent_days', absent_days)
    base = base_salary(salary_slip)
    full_day = full_day_deduction(base)
    amt = full_day * absent_days
    if amt > 0:
        add_deduction(salary_slip, amt, "Absent Days")
    salary_slip.calculate_net_pay()


def add_deduction(salary_slip, amt, salary_component="None"):
    salary_slip.append("deductions", {
        "salary_component": salary_component,
        "amount": amt
    })


def half_day_deduction(base):
    amt = base / 60
    return amt


def full_day_deduction(base):
    amt = base / 30
    return amt


def base_salary(salary_slip):
    ssa = frappe.db.get_value("Salary Structure Assignment", filters={
                "docstatus": 1,
                "employee": salary_slip.employee
            })
    ssadoc = frappe.get_doc("Salary Structure Assignment", ssa)
    base_salary = ssadoc.base
    return base_salary

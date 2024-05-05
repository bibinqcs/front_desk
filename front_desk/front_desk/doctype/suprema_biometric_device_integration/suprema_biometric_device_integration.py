# Copyright (c) 2020, Quark Cyber Systems and contributors
# For license information, please see license.txt

import frappe
import requests
import json
import dateutil.parser
import dateutil.relativedelta

from frappe.model.document import Document
from frappe.utils import today, getdate, get_time

from datetime import timedelta, datetime

from erpnext.setup.doctype.holiday_list.holiday_list import is_holiday
from dac_qcs.utils.common import formatted_time


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
        attendance_check = frappe.db.exists({
                            'doctype': 'Attendance',
                            'docstatus': 1,
                            'employee': employee.name,
                            'attendance_date': grace_date
                            })
        holiday_check = is_holiday(holiday_list, grace_date_parsed)
        if not attendance_check and not holiday_check:
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
        new_attendance(employee, attendance_date, time_in, time_out)
    else:
        auto_attendance_request = frappe.db.get_single_value('Suprema Biometric Device Integration', 'auto_attendance_request')
        if auto_attendance_request == 1:
            new_attendance_request(employee, attendance_date, time_in, time_out)
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


def new_attendance_request(employee, attendance_date, time_in, time_out):
    if not frappe.db.exists({'doctype': 'Attendance Request', 'employee': employee.name, 'from_date': attendance_date}):
        new_ar = frappe.new_doc('Attendance Request')
        new_ar.employee = employee.name
        new_ar.company = 'Dubai Autism Center'
        new_ar.from_date = attendance_date
        new_ar.to_date = attendance_date
        new_ar.reason = 'Missed Punch Data / Exception'
        new_ar.time_in = time_in
        new_ar.time_out = time_out
        new_ar.save()


def new_attendance(employee, attendance_date, time_in, time_out):
    attendance = frappe.new_doc('Attendance')
    attendance.employee = employee.name
    attendance.attendance_date = attendance_date
    attendance.status = 'Present'
    attendance.company = 'Dubai Autism Center'
    attendance.shift = employee.default_shift
    attendance.time_in = time_in
    attendance.time_out = time_out
    attendance.submit()

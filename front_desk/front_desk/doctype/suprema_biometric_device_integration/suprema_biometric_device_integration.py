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


class SupremaBiometricDeviceIntegration(Document):
    pass


@frappe.whitelist()
def api_hourly_sync():
    hourly_enabled = frappe.db.get_single_value('Suprema Biometric Device Integration', 'hourly_sync')
    if hourly_enabled == 1:
        json_data = api_payload(today(), today())
        new_biometric_log(json_data)


@frappe.whitelist()
def api_manual_sync(from_date, to_date):
    json_data = api_payload(from_date, to_date)
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


def api_payload(from_date, to_date):
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
                        "4102"
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


def custom_attendance(attendance, method):
    shift_time_details(attendance, method)
    update_time_in_and_time_out(attendance, method)
    calculate_tardiness(attendance, method)


def shift_time_details(attendance, method):
    if attendance.status == 'Present' and not attendance.start_time and not attendance.end_time:
        start_time = frappe.get_doc('Shift', attendance.shift).start_time
        end_time = frappe.get_doc('Shift', attendance.shift).end_time
        total_time = frappe.get_doc('Shift', attendance.shift).total_time
        attendance.set('start_time', start_time)
        attendance.set('end_time', end_time)
        attendance.set('total_time', total_time)


def update_time_in_and_time_out(attendance, method):
    if attendance.in_time_qcs and attendance.out_time_qcs:
        time_format_wof = "%Y-%m-%d %H:%M:%S"
        time_format_wf = "%Y-%m-%d %H:%M:%S.%f"
        try:
            dt_in = datetime.strptime(str(attendance.in_time_qcs), time_format_wof)
            dt_ot = datetime.strptime(str(attendance.out_time_qcs), time_format_wof)
        except ValueError:
            dt_in = datetime.strptime(str(attendance.in_time_qcs), time_format_wf)
            dt_ot = datetime.strptime(str(attendance.out_time_qcs), time_format_wf)
        attendance.time_in = dt_in.time().strftime("%H:%M:%S")
        attendance.time_out = dt_ot.time().strftime("%H:%M:%S")
    else:
        attendance.set('time_in', "")
        attendance.set('time_out', "")


def calculate_tardiness(attendance, method):
    if attendance.working_hours:
        if datetime.strptime(str(attendance.time_out),"%H:%M:%S") > datetime.strptime(str(attendance.time_in),"%H:%M:%S"):
            attendance.total_working_hours = datetime.strptime(str(attendance.time_out),"%H:%M:%S") - datetime.strptime(str(attendance.time_in),"%H:%M:%S")
        else:
            attendance.set('total_working_hours',"")

        if datetime.strptime(str(attendance.time_in),"%H:%M:%S") > datetime.strptime(str(attendance.start_time),"%H:%M:%S"):
            attendance.late_in = datetime.strptime(str(attendance.time_in),"%H:%M:%S") - datetime.strptime(str(attendance.start_time),"%H:%M:%S")
        else:
            attendance.set('late_in',"")

        if datetime.strptime(str(attendance.end_time),"%H:%M:%S") > datetime.strptime(str(attendance.time_out),"%H:%M:%S"):
            attendance.early_out = datetime.strptime(str(attendance.end_time),"%H:%M:%S") - datetime.strptime(str(attendance.time_out),"%H:%M:%S")
        else:
            attendance.set('early_out',"")

        if attendance.total_working_hours:
            if datetime.strptime(str(attendance.total_time),"%H:%M:%S") > datetime.strptime(str(attendance.total_working_hours),"%H:%M:%S"):
                attendance.diff_working_hours = datetime.strptime(str(attendance.total_time),"%H:%M:%S") - datetime.strptime(str(attendance.total_working_hours),"%H:%M:%S")
            else:
                attendance.set('diff_working_hours', "")
    else:
        attendance.set('late_in', "")
        attendance.set('early_out', "")
        attendance.set('total_working_hours', "")
        attendance.set('diff_working_hours', "")


@frappe.whitelist()
def daily_attendance():
    daily_enabled = frappe.db.get_single_value('Suprema Biometric Device Integration', 'daily_attendance')
    if daily_enabled == 1:
        employee_details = frappe.get_all('Employee', filters={
                                    'status': 'Active'
                                },
                                fields=['name', 'employee_name', 'date_of_joining']
                            )
        for emp in employee_details:
            fmonth = getdate(today())
            fmonth = fmonth - timedelta(days=1)
            if fmonth >= emp.date_of_joining:
                ip = frappe.get_all('Attendance', filters={
                            'attendance_date': fmonth,
                            'employee': emp.name
                            },
                            fields=['name']
                        )
                if not ip:
                    att_records = frappe.get_all('Biometric Access Log', filters={
                                        'employee': emp.name,
                                        'date': ['=', fmonth]
                                        },
                                        fields=['datetime', 'employee'],
                                        order_by='date'
                                    )
                    if att_records:
                        attendance = frappe.new_doc('Attendance')
                        attendance.employee = emp.name
                        attendance.attendance_date = fmonth
                        attendance.status = "Present"
                        attendance.company = "Dubai Autism Center"
                        attendance.time_in = get_time(att_records[0]["datetime"])
                        attendance.time_out = get_time(att_records[-1]["datetime"])
                        attendance.total_working_hours = formatted_time(attendance.time_out) - formatted_time(attendance.time_in)
                        attendance.save()
                        suprema_calculate_tardiness(attendance)
                        attendance.submit()


@frappe.whitelist()
def mark_attendance():
    today = datetime.today()
    employee_details = frappe.get_all('Employee', filters={
                                'status': 'Active'
                            },
                            fields=['name', 'employee_name', 'date_of_joining']
                        )
    for emp in employee_details:
        fmonth = datetime(today.year, today.month, 1)
        g = 1
        # fmonth = fmonth - dateutil.relativedelta.relativedelta(months=1)
        frappe.errprint(fmonth)
        while g <= 31:
            if fmonth.date() >= emp.date_of_joining:
                ip = frappe.get_all('Attendance', filters={
                            'attendance_date': fmonth,
                            'employee': emp.name
                            },
                            fields=['name']
                        )
                if not ip:
                    att_records = frappe.get_all('Biometric Access Log', filters={
                                        'employee': emp.name,
                                        'date': ['=', fmonth]
                                        },
                                        fields=['datetime', 'employee'],
                                        order_by='date'
                                    )
                    if att_records:
                        attendance = frappe.new_doc('Attendance')
                        attendance.employee = emp.name
                        attendance.attendance_date = fmonth
                        attendance.status = "Present"
                        attendance.company = "Dubai Autism Center"
                        frappe.errprint(att_records)
                        frappe.errprint(att_records[0])
                        frappe.errprint(att_records[-1])
                        frappe.errprint(get_time(att_records[0]["datetime"]))
                        frappe.errprint(get_time(att_records[-1]["datetime"]))
                        attendance.time_in = get_time(att_records[0]["datetime"])
                        attendance.time_out = get_time(att_records[-1]["datetime"])
                        attendance.total_working_hours = formatted_time(attendance.time_out) - formatted_time(attendance.time_in)
                        attendance.save()
                        suprema_calculate_tardiness(attendance)
                        attendance.submit()
            fmonth = fmonth + timedelta(days=1)
            g += 1


def suprema_calculate_tardiness(attendance):
    if formatted_time(attendance.time_out) > formatted_time(attendance.time_in):
        attendance.total_working_hours = formatted_time(attendance.time_out) - formatted_time(attendance.time_in)
    else:
        attendance.set('total_working_hours', "")
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
    if attendance.total_working_hours:
        if formatted_time(attendance.total_time) > formatted_time(attendance.total_working_hours):
            attendance.diff_working_hours = formatted_time(attendance.total_time) - formatted_time(attendance.total_working_hours)
        else:
            attendance.set('diff_working_hours', "")
    if not attendance.total_working_hours:
        attendance.set('late_in', "")
        attendance.set('early_out', "")
        attendance.set('total_working_hours', "")
        attendance.set('diff_working_hours', "")


def formatted_time(time):
    format_time = datetime.strptime(str(time), "%H:%M:%S")
    return format_time

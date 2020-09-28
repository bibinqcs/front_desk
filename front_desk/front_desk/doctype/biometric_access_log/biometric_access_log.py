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
from frappe.utils import today, getdate
from datetime import timedelta, datetime


class BiometricAccessLog(Document):
    pass


# biostar Integration
@frappe.whitelist()
def api_integration_bulk():
    login_url = "https://dacdevqcs.ddns.net:9006/api/login"
    payload_login = {
        "User": {
            "login_id": "admin",
            "password": "Dub@1@a1"
        }
    }
    payload_l = json.dumps(payload_login, default=jsonDefault)
    headers_l = {
        'Content-Type': 'application/json'
        }
    response = requests.request("POST", login_url, headers=headers_l, data=payload_l, verify=False)
    session_id = response.headers["bs-session-id"]
    url = "https://dacdevqcs.ddns.net:9006/api/events/search"
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
                        "2020-09-01T00:00:00.00Z",
                        "2020-09-30T23:59:59.99Z"
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
    for data in json_data["EventCollection"]["rows"]:
        existing_record = frappe.get_value('Biometric Access Log', dict(
            id_index=data["index"],
            server_datetime=iso_datetime_trim(data["server_datetime"])
        ))
        if not existing_record:
            if frappe.db.get_value("Employee", {"name": data["user_id"]["user_id"]}):
                new_r = frappe.new_doc("Biometric Access Log")
                new_r.id_index = data["index"]
                new_r.record_id = data["id"]
                new_r.date = iso_date_trim(data["datetime"])
                new_r.datetime = add_tz(data["timezone"]["hour"], data["datetime"])
                new_r.server_datetime = iso_datetime_trim(data["server_datetime"])
                new_r.device_id = data["device_id"]["id"]
                new_r.device_id_name = data["device_id"]["name"]
                new_r.employee = data["user_id"]["user_id"]
                new_r.save()


# biostar Integration
@frappe.whitelist()
def api_integration():
    login_url = "https://dacdevqcs.ddns.net:9006/api/login"
    payload_login = {
        "User": {
            "login_id": "admin",
            "password": "Dub@1@a1"
        }
    }
    payload_l = json.dumps(payload_login, default=jsonDefault)
    headers_l = {
        'Content-Type': 'application/json'
        }
    response = requests.request("POST", login_url, headers=headers_l, data=payload_l, verify=False)
    session_id = response.headers["bs-session-id"]
    url = "https://dacdevqcs.ddns.net:9006/api/events/search"
    today_date = getdate(today()).strftime("%Y-%m-%d")
    starttime = today_date + "T00:00:00.00Z"
    endtime = today_date + "T23:59:59.99Z"
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
    for data in json_data["EventCollection"]["rows"]:
        existing_record = frappe.get_value('Biometric Access Log', dict(
            id_index=data["index"],
            server_datetime=iso_datetime_trim(data["server_datetime"])
        ))
        if not existing_record:
            if frappe.db.get_value("Employee", {"name": data["user_id"]["user_id"]}):
                new_r = frappe.new_doc("Biometric Access Log")
                new_r.id_index = data["index"]
                new_r.record_id = data["id"]
                new_r.date = iso_date_trim(data["datetime"])
                new_r.datetime = add_tz(data["timezone"]["hour"], data["datetime"])
                new_r.server_datetime = iso_datetime_trim(data["server_datetime"])
                new_r.device_id = data["device_id"]["id"]
                new_r.device_id_name = data["device_id"]["name"]
                new_r.employee = data["user_id"]["user_id"]
                new_r.save()


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
        if datetime.strptime(str(attendance.time_out), "%H:%M:%S") > datetime.strptime(str(attendance.time_in),"%H:%M:%S"):
            attendance.total_working_hours = datetime.strptime(str(attendance.time_out), "%H:%M:%S") - datetime.strptime(str(attendance.time_in), "%H:%M:%S")
        else:
            attendance.set('total_working_hours', "")

        if datetime.strptime(str(attendance.time_in), "%H:%M:%S") > datetime.strptime(str(attendance.start_time),"%H:%M:%S"):
            attendance.late_in = datetime.strptime(str(attendance.time_in), "%H:%M:%S") - datetime.strptime(str(attendance.start_time),"%H:%M:%S")
        else:
            attendance.set('late_in', "")

        if datetime.strptime(str(attendance.end_time), "%H:%M:%S") > datetime.strptime(str(attendance.time_out),"%H:%M:%S"):
            attendance.early_out = datetime.strptime(str(attendance.end_time), "%H:%M:%S") - datetime.strptime(str(attendance.time_out), "%H:%M:%S")
        else:
            attendance.set('early_out', "")

        if attendance.total_working_hours:
            if datetime.strptime(str(attendance.total_time), "%H:%M:%S") > datetime.strptime(str(attendance.total_working_hours), "%H:%M:%S"):
                attendance.diff_working_hours = datetime.strptime(str(attendance.total_time), "%H:%M:%S") - datetime.strptime(str(attendance.total_working_hours), "%H:%M:%S")
            else:
                attendance.set('diff_working_hours', "")
    else:
        attendance.set('late_in', "")
        attendance.set('early_out', "")
        attendance.set('total_working_hours', "")
        attendance.set('diff_working_hours', "")


@frappe.whitelist()
def mark_attendance():
    today = datetime.today()
    # yt = datetime.combine(yesterday, datetime.min.time())
    for emp in frappe.get_all("Employee", fields={"name", "employee_name", "date_of_joining"},filters={"status":"Active"}):
        # fmonth = today
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

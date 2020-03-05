# -*- coding: utf-8 -*-
# Copyright (c) 2015, vivek and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe, requests, urllib3, json, datetime, dateutil.parser, urllib2, urllib, dateutil.relativedelta
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import flt, add_days, date_diff, get_request_site_address
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee
from json import dumps
from datetime import date, timedelta, datetime
from frappe.utils.response import json_handler
from dateutil.relativedelta import relativedelta






# biostar Integration
@frappe.whitelist()
def sync_access_log():
    url = "http://172.26.3.14:8795/v2/login"
    payload = "{\r\n  \"name\": \"DubaiAutismCenter\",\r\n  \"password\": \"Dub@1@a1\",\r\n  \"user_id\": \"admin\"\r\n}"
    headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "f11383dc-d6c1-ff3e-81aa-85635ec39eba"
    }


    r = requests.session()
    r.post('http://172.26.3.14:8795/v2/login', data=payload, headers=headers)

    #cookie_obj = requests.cookies.create_cookie(name='bs-cloud-session-id',value='the cookie works')
    #r.cookies.set_cookie(cookie_obj)
    #response = requests.post('http://172.26.3.14:8795/v2/login', data=data, headers=rheader)



    data2={
      "limit": 0,
      "offset": 0
    }
    t = r.post('http://172.26.3.14:8795/v2/monitoring/event_log/search', data=data2)
    url = "http://172.26.3.14:8795/v2/monitoring/event_log/search"
    #date = str(datetime.datetime.now().isoformat())
    #date = datetime.datetime.now()

    #payload = "{\r\n  \"datetime\":[date],\r\n  \"event_type_code\":[\"4865\"],\r\n   \"limit\": 0,\r\n  \"offset\": 0\r\n}"
    #payload.datetime = datetime.datetime.now()
    dt = date.today()
    #max = str(dt) +"T23:00:00.00Z"
    #min = str(dt) +"T01:00:00.00Z"
    max = "2019-12-30T23:00:00.00Z"
    min = "2019-12-01T01:00:00.00Z"


    info = {
  "device_query_list": [
    {
      "device_id": "546844676",
      "end_datetime": max,
      "start_datetime": min
    },
    {
      "device_id": "546844679",
      "end_datetime": max,
      "start_datetime": min
    }
  ],
  "event_type_code_list": [
    "4865"
  ],
  "limit": 0,
  "offset": 0
}
    payload = json.dumps(info, default=jsonDefault)
    headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "0905b128-5973-5b9c-0e12-dd60f3c4c7ca"
    }

    t = r.post('http://172.26.3.14:8795/v2/monitoring/event_log/search_by_device', data=payload, headers=headers)
    json_data = json.loads(t.text)
    frappe.errprint(json_data)
    for data in json_data["records"]:
        if not frappe.db.get_value("Access Log", {"id_index": data["index"]}):
            if frappe.db.get_value("Employee", {"name": data["user"]["user_id"]}):
                new_r = frappe.new_doc("Access Log")
                new_r.id_index = data["index"]
                new_r.date = data["server_datetime"]
                new_r.employee = data["user"]["user_id"]
                new_r.only_date = data["server_datetime"]
                new_r.save()
        #frappe.errprint(dateutil.parser.parse(data["server_datetime"]))




@frappe.whitelist()
def sync_access_log_test():
    url = "http://172.26.3.14:8795/v2/login"
    payload = "{\r\n  \"name\": \"DubaiAutismCenter\",\r\n  \"password\": \"Dub@1@a1\",\r\n  \"user_id\": \"admin\"\r\n}"
    headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "f11383dc-d6c1-ff3e-81aa-85635ec39eba"
    }


    r = requests.session()
    r.post('http://172.26.3.14:8795/v2/login', data=payload, headers=headers)

    #cookie_obj = requests.cookies.create_cookie(name='bs-cloud-session-id',value='the cookie works')
    #r.cookies.set_cookie(cookie_obj)
    #response = requests.post('http://172.26.3.14:8795/v2/login', data=data, headers=rheader)



    data2={
      "limit": 0,
      "offset": 0
    }
    t = r.post('http://172.26.3.14:8795/v2/monitoring/event_log/search', data=data2)
    url = "http://172.26.3.14:8795/v2/monitoring/event_log/search"
    #date = str(datetime.datetime.now().isoformat())
    #date = datetime.datetime.now()

    ##payload = "{\r\n  \"datetime\":[date],\r\n  \"event_type_code\":[\"4865\"],\r\n   \"limit\": 0,\r\n  \"offset\": 0\r\n}"
    #payload.datetime = datetime.datetime.now()
    #for emp in frappe.get_all("Employee", fields={"name", "employee_name"},filters={"status":"Active"}):
    #    usr = '"{}"'.format(emp.name)
    #    frappe.errprint(usr)

    dt = date.today()
    max = str(dt) +"T23:00:00.00Z"
    min = str(dt) +"T01:00:00.00Z"
    frappe.errprint(max)

    info = {
  "device_query_list": [
    {
      "device_id": "546844676",
      "end_datetime": max,
      "start_datetime": min
    },
    {
      "device_id": "546844679",
      "end_datetime": max,
      "start_datetime": min
    }
  ],
  "event_type_code_list": [
    "4865"
  ],
  "limit": 0,
  "offset": 0
}
    payload = json.dumps(info, default=jsonDefault)
    headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "0905b128-5973-5b9c-0e12-dd60f3c4c7ca"
    }
    t = r.post('http://172.26.3.14:8795/v2/monitoring/event_log/search_by_device', data=payload, headers=headers)
    json_data = json.loads(t.text)
    frappe.errprint(json_data)

        #frappe.errprint(dateutil.parser.parse(data["server_datetime"]))






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
                    ac = frappe.get_all("Access Log", fields={"date", "employee"}, filters={"employee":emp.name, "only_date":("=",fmonth)}, order_by='date')
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



@frappe.whitelist()
def auto_allocate_leave():
    for emp in frappe.db.get_all("Employee", fields =["name", "date_of_joining", "auto_allocate", "leave_policy", "status"]):
        if emp.auto_allocate:
            if emp.leave_policy:
                td = relativedelta(emp.date_of_joining, date.today())
                if td.years >= 1:
                    if td.months == 0:
                        if td.days == 0:
                            lp = frappe.get_doc("Leavy Policy", emp.leave_policy)
                            for item in lp.get("leave_policy_details"):
                                lalloc = frappe.new_doc("Leave Allocation")
                                lalloc.employee = emp.name
                                lalloc.leave_type = item.leave_type
                                lalloc.from_date = datetime.today()
                                lalloc.to_date = add_days(datetime.today(), 365)
                                lalloc.new_leaves_allocated = item.annual_allocation
                                lalloc.save()
                                lalloc.submit()



@frappe.whitelist()
def auto_allocate_leave_test():
    for emp in frappe.db.get_all("Employee", fields =["name", "date_of_joining", "auto_allocate", "leave_policy", "status"]):
        if emp.auto_allocate:
            if emp.leave_policy:
                td = relativedelta(emp.date_of_joining, date.today())
                frappe.errprint(emp.name)
                frappe.errprint(td.years)






# fetch employee details
@frappe.whitelist()
def get_employee_details(user):
    pass

# create class schedule for semester

@frappe.whitelist()
def create_class_semester_schedule(doc, method):
    if doc.create_for_academic_term:
        semester = frappe.get_doc("Academic Term", doc.academic_term)
        date = semester.term_start_date
    while(date < semester.term_end_date):
        make_class_schedule(date, doc.from_time, doc.to_time, doc.course, doc.student_group, doc.instructor)
        date = add_days(date, 7)

@frappe.whitelist()
def get_employee_gratuity(employee):
    emp = frappe.get_doc("Employee", employee)
    gratuity = 0

    if date_diff(emp.relieving_date, emp.joining_date) > 1 and date_diff(emp.relieving_date, emp.joining_date) < 5:
        gratuity = date_diff(emp.relieving_date, emp.joining_date) * 10 * 21
    if date_diff(emp.relieving_date, emp.joining_date) > 5:
        gratuity = date_diff(emp.relieving_date, emp.joining_date) * 10 * 21
    if date_diff(emp.relieving_date, emp.joining_date) < 1:
        gratuity = 0
    return gratuity



def make_class_schedule(date, from_time, to_time, course, student_group, instructor):
    course_schedule = frappe.new_doc("Course Schedule")
    course_schedule.student_group = student_group
    course_schedule.course = course
    course_schedule.instructor = instructor
    course_schedule.schedule_date = date
    course_schedule.from_time = from_time
    course_schedule.to_time = to_time
    course_schedule.save()

def add_env_bank(communication_assessment_in_therapy_rooms, method):
    for d in frappe.db.get_all("Environment Assessment Bank", fields = ["comm_assessment"]):
        if communication_assessment_in_therapy_rooms.get("__islocal"):
            communication_assessment_in_therapy_rooms.append("env_table", {"point":d["comm_assessment"]})


def add_ablls_bank(ablls_r_assessment, method):
    for a in frappe.db.get_all("ABLLSR Bank", fields = ["abllsr_cat", "abllsr_task", "abllsr_code"]):
        if ablls_r_assessment.get("__islocal"):
            if a["abllsr_cat"] == "A":
                ablls_r_assessment.append("abllsra", {
                                    "abllsr_code":a["abllsr_code"],
                                    "abllsr_task":a["abllsr_task"]
                })
            if a["abllsr_cat"] == "B":
                ablls_r_assessment.append("abllsrb", {
                                    "abllsr_code":a["abllsr_code"],
                                    "abllsr_task":a["abllsr_task"]
                })
            if a["abllsr_cat"] == "C":
                ablls_r_assessment.append("abllsrc", {
                                    "abllsr_code":a["abllsr_code"],
                                    "abllsr_task":a["abllsr_task"]
                })
            if a["abllsr_cat"] == "D":
                ablls_r_assessment.append("abllsrd", {
                                    "abllsr_code":a["abllsr_code"],
                                    "abllsr_task":a["abllsr_task"]
                })
            if a["abllsr_cat"] == "E":
                ablls_r_assessment.append("abllsre", {
                                    "abllsr_code":a["abllsr_code"],
                                    "abllsr_task":a["abllsr_task"]
                })

def add_vocation_checklist(vocational_checklist, method):
    for a in frappe.db.get_all("Computer Assessment Bank", fields =["domain", "serial", "item"]):
        if vocational_checklist.get("__islocal"):
            if a["domain"] == "Career Awareness":
                vocational_checklist.append("career_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Work Behavior":
                vocational_checklist.append("wb_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Lunch Service":
                vocational_checklist.append("ls_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Home Industry":
                vocational_checklist.append("hi_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Housekeeping":
                vocational_checklist.append("hk_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Janitorial":
                vocational_checklist.append("jt_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Office/Clerical":
                vocational_checklist.append("oc_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Money Concept":
                vocational_checklist.append("mc_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Community Participation":
                vocational_checklist.append("cp_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })


def add_gml1_cl(gm, method):
    for a in frappe.db.get_all("OT Bank", fields =["domain", "serial_no", "items"]):
        if gm.get("__islocal"):
            if a["domain"] == "2-3 years":
                gm.append("a_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "4-5 Years":
                gm.append("b_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "5-6 Years":
                gm.append("c_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "6-7 Years":
                gm.append("d_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "7-8 Years":
                gm.append("e_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })


def add_gml2_cl(gm, method):
    for a in frappe.db.get_all("OT Bank", fields =["domain", "serial_no", "items"]):
        if gm.get("__islocal"):
            if a["domain"] == "Physical Exercise":
                gm.append("pe_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "Balance":
                gm.append("ba_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "Ball Skills":
                gm.append("bs_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "Games/Sports":
                gm.append("gm_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })

def add_adl_cl(gm, method):
    for a in frappe.db.get_all("OT Bank", fields =["domain", "serial_no", "items"]):
        if gm.get("__islocal"):
            if a["domain"] == "PERSONAL HYGIENE (GROOMING-Combing)":
                gm.append("phgc_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "PERSONAL HYGIENE(GROOMING-Washing Face)":
                gm.append("phgwf_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "PERSONAL HYGIENE(GROOMING-Brushing Teeth)":
                gm.append("phgbt_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "PERSONAL HYGIENE(GROOMING-Buttoning of shirt)":
                gm.append("phgbs_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "PERSONAL HYGIENE(GROOMING-Putting on socks)":
                gm.append("phgps_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "EATING":
                gm.append("eating_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "PERSONAL CARE":
                gm.append("pc_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })

def add_iadl_cl(gm, method):
    for a in frappe.db.get_all("OT Bank", fields =["domain", "serial_no", "items"]):
        if gm.get("__islocal"):
            if a["domain"] == "Bed Making":
                gm.append("bed_making_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "Meal Preparation (sandwich making)":
                gm.append("meal_prep_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "Sweeping the floor with broom":
                gm.append("sweeping_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "Cleaning with vaccuum cleaner":
                gm.append("ct_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "Washing Dishes":
                gm.append("wd_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })


def add_ca_cl(vocational_checklist, method):
    for a in frappe.db.get_all("Computer Assessment Bank", fields =["domain", "serial", "item"]):
        if vocational_checklist.get("__islocal"):
            if a["domain"] == "Assistive Technology (Switch)":
                vocational_checklist.append("at_sw_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Assistive Technology (Chester Mouse)":
                vocational_checklist.append("at_cm_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Assistive Technology (Alternate Keyboard)":
                vocational_checklist.append("at_ak_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Assistive Technology (Multi-Touch Screen Skills)":
                vocational_checklist.append("at_mt_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "IPad Skills":
                vocational_checklist.append("ipad_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Mouse Skills":
                vocational_checklist.append("mouse_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Keyboard Skills":
                vocational_checklist.append("key_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Basic Computer Skills":
                vocational_checklist.append("basic_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })
            if a["domain"] == "Word Processing Skills":
                vocational_checklist.append("word_table", {
                                    "serial":a["serial"],
                                    "item":a["item"]
                })


def add_adfrm(gm, method):
    for a in frappe.db.get_all("OT Bank", fields =["domain", "serial_no", "items"]):
        if gm.get("__islocal"):
            if a["domain"] == "Creative Movement":
                gm.append("cm_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "Visual Arts":
                gm.append("va_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "Creative Dramatics":
                gm.append("cd_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })

def add_ot_cl(gm, method):
    for a in frappe.db.get_all("OT Bank", fields =["domain", "serial_no", "items"]):
        if gm.get("__islocal"):
            if a["domain"] == "GENERAL OBSERVATIONS":
                gm.append("go_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "Manipulative Skills":
                gm.append("ms_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "General Work Behaviors":
                gm.append("gw_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "COGNITIVE SKILLS":
                gm.append("cs_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "PLAY":
                gm.append("play_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "GRAPHIC SKILLS":
                gm.append("gs_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "Visual Motor Integration Skills":
                gm.append("vm_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "GRASPING SKILLS":
                gm.append("gr_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "In Hand Manipulation Skills":
                gm.append("ih_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })


def add_ot_sw_cl(gm, method):
    for a in frappe.db.get_all("OT Bank", fields =["domain", "serial_no", "items"]):
        if gm.get("__islocal"):
            if a["domain"] == "Aquatic Orientation":
                gm.append("ao_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "Level 1: Introduction to water skills":
                gm.append("l1_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "Level 2: Fundamental Aquatic Skills":
                gm.append("l2_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })
            if a["domain"] == "Level 3: Strokes and Development":
                gm.append("l3_table", {
                                    "serial_no":a["serial_no"],
                                    "items":a["items"]
                })

def get_target(code):
    tdoc = frappe.get_all('ABLLS-R Bank', filters={'code': code})
    data =[]
    for item in tdoc.target_table:
        data.append(item.target)
    return data

#def create_student_customer(doc, method):
#    if not frappe.db.get_values("Customer", {"name": doc.name}):
#        cust = frappe.new_doc("Customer")
#        cust.customer_name = doc.name
#        cust.customer_type = "Individual"
#        cust.customer_group = "Student"
#        cust.territory = "United Arab Emirates"
#        cust.save()
#    else:
#        cust = frappe.get_doc("Customer", doc.name)
#        cust.customer_name = doc.name
#        cust.customer_type = "Individual"
#        cust.customer_group = "Student"
#        cust.territory = "United Arab Emirates"
#        cust.student_name = doc.title
#	 cust.gender =  doc.gender
#        cust.fathers_name = doc.father_name
#        cust.fathers_mobile_no = doc.father_mob_number
#        cust.mothers_name = doc.mother_name
#        cust.mothers_mobile_no =  doc.mother_mob_number
#        cust.save()


#def employee_name(employee, method):
#    org = make_autoname('DAC-EM-' + '.###')
#    first = org[:7]
#    last = org[7:]
#    employee.name = first + employee.dept_abbr + '-' + last


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

def lwp_d(salary_slip, method):
    salary_slip.wages_per_day = flt(salary_slip.emp_salary/30)
    if salary_slip.payment_days != 30:
        salary_slip.lwp_deduction = salary_slip.wages_per_day * salary_slip.leave_without_pay

@frappe.whitelist()
def calculate_lwp(employee, date_of_joining, last_day):
		lwp = 0
#	        for holidays
#        		holiday_list = get_holiday_list_for_employee(employee)
		holidays = frappe.db.sql_list('''select holiday_date from `tabHoliday`
			where
				parent=%(holiday_list)s
				and holiday_date >= %(start_date)s
				and holiday_date <= %(end_date)s''', {
					"holiday_list": holiday_list,
					"start_date": date_of_joining,
					"end_date": last_day
				})

		holidays = [cstr(i) for i in holidays]
		working_days = date_diff(self.end_date, self.start_date) + 1

		holidays = "','".join(holidays)
		for d in range(working_days):
			dt = add_days(cstr(getdate(date_of_joining)), d)
			leave = frappe.db.sql("""
				select t1.name, t1.half_day
				from `tabLeave Application` t1, `tabLeave Type` t2
				where t2.name = t1.leave_type
				and t2.is_lwp = 1
				and t1.docstatus = 1
				and t1.employee = %(employee)s
				and CASE WHEN t2.include_holiday != 1 THEN %(dt)s not in ('{0}') and %(dt)s between from_date and to_date
				WHEN t2.include_holiday THEN %(dt)s between from_date and to_date
				END
				""".format(holidays), {"employee": employee, "dt": dt})
			if leave:
				lwp = cint(leave[0][1]) and (lwp + 0.5) or (lwp + 1)
		return lwp


def sync_teacher_student(teacher_schedule, method):
    	sc = frappe.new_doc("Student Schedule")
    	sc.from_time = teacher_schedule.from_time
    	sc.to_time = teacher_schedule.to_time
    	sc.notes = teacher_schedule.notes
    	sc.student = teacher_schedule.student
    	sc.save()

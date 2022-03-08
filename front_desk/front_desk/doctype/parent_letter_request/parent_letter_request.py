# -*- coding: utf-8 -*-
# Copyright (c) 2020, Quark Cyber Systems and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class ParentLetterRequest(Document):
    pass


@frappe.whitelist()
def fetch_student(student):
    student_name, student_nationality, emirates_id_no, guardian_mobile_no, date_of_birth, joining_date = frappe.db.get_value('Student', student, ['title', 'student_nationality', 'emirates_id_no', 'guardian_mobile_no', 'date_of_birth', 'joining_date'])
    return student_name, student_nationality, emirates_id_no, guardian_mobile_no, date_of_birth, joining_date


@frappe.whitelist()
def fetch_client(patient):
    patient_name, uid, dob = frappe.db.get_value('Patient', patient, ['patient_name', 'uid', 'dob'])
    return patient_name, uid, dob

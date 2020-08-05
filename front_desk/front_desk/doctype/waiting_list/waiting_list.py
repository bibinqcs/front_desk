# -*- coding: utf-8 -*-
# Copyright (c) 2017, Quark Cyber Systems and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import add_days, today, flt, getdate
from erpnext.healthcare.doctype.healthcare_settings.healthcare_settings import get_receivable_account, get_income_account
from erpnext.accounts.doctype.sales_invoice.test_sales_invoice import create_sales_invoice

class WaitingList(Document):
	def validate(self):
		self.create_observation_invoice()
		self.validate_date()
		if not self.student_age:
			self.student_age = getdate(today()).year - getdate(self.date_of_birth).year
		if not self.student_full_name:
			if self.student_middle_name:
				self.student_full_name = " ".join(filter(None, [self.student_first_name, self.student_middle_name, self.student_last_name]))
			else:
				self.student_full_name = " ".join(filter(None, [self.student_first_name, self.student_last_name]))

	def create_observation_invoice(self):
		for item in self.observation_list:
			if item.status == "Complete" and item.fee == None:
				si = frappe.new_doc("Sales Invoice")
				si.set_posting_time = 1
				si.customer = "Waiting List"
				si.posting_date = today()
				si.update_stock = 0
				si.is_pos = 0
				si.debit_to = get_receivable_account(si.company)
				si.payment_schedule = []
				si.append("items", {
							"item_code":item.item_observation,
							"qty": "1",
							})
				si.run_method("set_missing_values")
				si.run_method("calculate_taxes_and_totals")
				si.save()
				item.fee = si.name

	def validate_date(self):
		if self.date_of_birth and getdate(self.date_of_birth) >= getdate(today()):
			frappe.throw(msg='Date of Birth cannot be greater than today.',
			title='Error')
		
		if self.date_of_birth and getdate(today()).year - getdate(self.date_of_birth).year < 2:
			frappe.throw(msg='Student has to be atleast 2 years old to apply.',
			title='Error')

		if self.expiry_date and getdate(self.expiry_date) <= getdate(today()):
			frappe.throw(msg='Passport is expired.',
			title='Error')

		if self.eid_expiry_date and self.valid_eid == 'Yes' and getdate(self.eid_expiry_date) <= getdate(today()):
			frappe.throw(msg='Emirates ID is expired.',
			title='Error')

		if self.guardian_id_expiry and getdate(self.guardian_id_expiry) <= getdate(today()):
			frappe.throw(msg='Guardian Emirates ID is expired.',
			title='Error')
		
		if self.guardian_pp_expiry and getdate(self.guardian_pp_expiry) <= getdate(today()):
			frappe.throw(msg='Guardian Passport is expired.',
			title='Error')

@frappe.whitelist()
def add_guardians(waitinglist):
	w_doc = frappe.get_doc("Waiting List", waitinglist)
	if w_doc.guardian_relation == "Father":
		add_guardian_father(w_doc)
		add_mother(w_doc)
	if w_doc.guardian_relation == "Mother":
		add_guardian_mother(w_doc)
		add_father(w_doc)
	if w_doc.guardian_relation == "Others":
		add_other(w_doc)
		add_father(w_doc)
		add_mother(w_doc)

def add_guardian_father(w_doc):
	guardian = frappe.get_value('Guardian', dict(guardian_name=w_doc.guardian_full_name,mobile_number=w_doc.guardian_mobile_no))
	if guardian:
		frappe.errprint("Guardians Exist - Skipping")
	else:
		g_father = frappe.get_doc({
			'doctype': 'Guardian',
			'guardian_name': w_doc.guardian_full_name,
			'email_address': w_doc.guardian_email,
			'mobile_number': w_doc.guardian_mobile_no,
			'nationality': w_doc.guardian_nationality,
			'passport': w_doc.guardian_passport_number,
			'passport_expiry': w_doc.guardian_pp_expiry,
			'passport_copy': w_doc.guard_pp_att,
			'emirates_id': w_doc.guardian_id,
			'emiratesid_expiry': w_doc.guardian_id_expiry,
			'emirates_id_copy': w_doc.guard_eid_att,
		}).insert(ignore_permissions = True)
		w_doc.append('guardians', {
			'guardian': g_father.name,
			'guardian_name': w_doc.guardian_full_name,
			'relation': w_doc.guardian_relation
		})
		w_doc.save()

def add_guardian_mother(w_doc):
	guardian = frappe.get_value('Guardian', dict(guardian_name=w_doc.guardian_full_name,mobile_number=w_doc.guardian_mobile_no))
	if guardian:
		frappe.errprint("Guardians Exist - Skipping")
	else:
		g_mother = frappe.get_doc({
			'doctype': 'Guardian',
			'guardian_name': w_doc.guardian_full_name,
			'email_address': w_doc.guardian_email,
			'mobile_number': w_doc.guardian_mobile_no,
			'nationality': w_doc.guardian_nationality,
			'passport': w_doc.guardian_passport_number,
			'passport_expiry': w_doc.guardian_pp_expiry,
			'passport_copy': w_doc.guard_pp_att,
			'emirates_id': w_doc.guardian_id,
			'emiratesid_expiry': w_doc.guardian_id_expiry,
			'emirates_id_copy': w_doc.guard_eid_att,
		}).insert(ignore_permissions = True)
		w_doc.append('guardians', {
			'guardian': g_mother.name,
			'guardian_name': w_doc.guardian_full_name,
			'relation': w_doc.guardian_relation
		})
		w_doc.save()
		
def add_other(w_doc):
	guardian = frappe.get_value('Guardian', dict(guardian_name=w_doc.guardian_full_name,mobile_number=w_doc.guardian_mobile_no))
	if guardian:
		frappe.errprint("Guardians Exist - Skipping")
	else:
		other = frappe.get_doc({
			'doctype': 'Guardian',
			'guardian_name': w_doc.guardian_full_name,
			'email_address': w_doc.guardian_email,
			'mobile_number': w_doc.guardian_mobile_no,
			'nationality': w_doc.guardian_nationality,
			'passport': w_doc.guardian_passport_number,
			'passport_expiry': w_doc.guardian_pp_expiry,
			'passport_copy': w_doc.guard_pp_att,
			'emirates_id': w_doc.guardian_id,
			'emiratesid_expiry': w_doc.guardian_id_expiry,
			'emirates_id_copy': w_doc.guard_eid_att,
		}).insert(ignore_permissions = True)
		w_doc.append('guardians', {
			'guardian': other.name,
			'guardian_name': w_doc.guardian_full_name,
			'relation': w_doc.guardian_relation
		})
		w_doc.save()

def add_father(w_doc):
	guardian = frappe.get_value('Guardian', dict(guardian_name=w_doc.father_name,mobile_number=w_doc.father_mob))
	if guardian:
		frappe.errprint("Guardians Exist - Skipping")
	else:
		father = frappe.get_doc({
			'doctype': 'Guardian',
			'guardian_name': w_doc.father_name,
			'mobile_number': w_doc.father_mob,
			'nationality': w_doc.father_nationality,
		}).insert(ignore_permissions = True)
		w_doc.append('guardians', {
			'guardian': father.name,
			'guardian_name': w_doc.father_name,
			'relation': "Father"
		})
		w_doc.save()
		

def add_mother(w_doc):
	guardian = frappe.get_value('Guardian', dict(guardian_name=w_doc.mother_name,mobile_number=w_doc.mother_mob))
	if guardian:
		frappe.errprint("Guardians Exist - Skipping")
	else:
		mother = frappe.get_doc({
			'doctype': 'Guardian',
			'guardian_name': w_doc.mother_name,
			'mobile_number': w_doc.mother_mob,
			'nationality': w_doc.mother_nationality,
		}).insert(ignore_permissions = True)
		w_doc.append('guardians', {
			'guardian': mother.name,
			'guardian_name': w_doc.mother_name,
			'relation': "Mother"
		})
		w_doc.save()

@frappe.whitelist()
def verify_student_details(student_name, date_of_birth):
	student = frappe.get_doc('Student', student_name)
	if not getdate(student.date_of_birth) == getdate(date_of_birth):
		frappe.throw(msg='No Matching Records Found.',
		title='Error')
	else:
		return student

@frappe.whitelist()
def register_student(source_name, target_doc=None):

	def parent_details(source, target):
		if source.guardian_relation == "Father":
			target.father_name = source.guardian_first_name

	doclist = get_mapped_doc("Waiting List", source_name, {
		"Waiting List": {
			"doctype": "Student",
			"field_map": {
				"student_first_name": "first_name",
				"student_middle_name": "middle_name",
				"student_last_name": "last_name",
				"date_of_birth": "date_of_birth",
				"gender": "gender",
				"religion": "religion",
				"sibling_number": "sibling_number",
				"language": "language",
				"nationality": "student_nationality",
				"place_of_birth": "place_of_birth",
				"student_passport_no": "passport_no",
				"expiry_date": "passport_expiry_date",
				"student_eid_no": "emirates_id_no",
				"eid_expiry_date": "emirates_id_expiry",
				"student_pod_no": "student_pod_no",
				"emirate": "emirate",
				"building_no": "building_no",
				"street_no": "street_no",
				"area": "area",
				"apt_villa_no": "apt_villa_no",
				"makani_no": "makani_no",
				"emergency_contact_name_1": "emergency_contact_name_1",
				"emergency_contact_no_1": "emergency_contact_no_1",
				"emergency_contact_name_2": "emergency_contact_name_2",
				"emergency_contact_no_2": "emergency_contact_no_2",
				"blood_grp": "blood_grp",
				#"allergies": "allergies",
				"allergy_type": "allergy_type",
				"allergy_period_treatment": "allergy_period_treatment",
				#"seizures": "seizures",
				"seizure_type": "seizure_type",
				"seizure_period_type": "seizure_period_type",
				"other_diseases_type": "other_type",
				"other_diseases_period": "other_period_treatment",
				"persons_pickup1": "persons_pickup1",
				"persons_pickup1_mobile": "persons_pickup1_mobile",
				"persons_pickup2": "persons_pickup2",
				"persons_pickup2_mobile": "persons_pickup2_mobile",
				"persons_pickup3": "persons_pickup3",
				"persons_pickup3_mobile": "persons_pickup3_mobile",
				#"report_att":
				"child_pic_att": "image",
				#"child_birth_att":
				"child_pp_att": "passport_copy",
				"child_eid_att": "eid_copy",
			}
		},
		"Student Medication": {
			"doctype": "Student Medication",
			"field_map": {
				"parent": "prevdoc_docname",
			}
		},
		"Waitlist Guardian": {
			"doctype": "Student Guardian",
			"field_map": {
				"parent": "prevdoc_docname",
			}
		},
	},target_doc)
	return doclist

@frappe.whitelist()
def make_appointment(source_name, target_doc=None):
	doclist = get_mapped_doc("Waiting List", source_name,
		{"Waiting List": {
			"doctype": "Appointments",
			"field_map": {
				"name1": "contact_name",
				"father_mob": "mobile_number",
				}
		}})
	return doclist



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
		
		self.student_age = getdate(today()).year - getdate(self.date_of_birth).year
		
		if self.student_middle_name:
			self.student_full_name = " ".join(filter(None, [self.student_first_name, self.student_middle_name, self.student_last_name]))
		else:
			self.student_full_name = " ".join(filter(None, [self.student_first_name, self.student_last_name]))		
		
		self.guardian_full_name = " ".join(filter(None, [self.guardian_first_name, self.guardian_last_name]))

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
def verify_student_details(student_name, date_of_birth):
	student = frappe.get_doc('Student', student_name)
	if not getdate(student.date_of_birth) == getdate(date_of_birth):
		frappe.throw(msg='No Matching Records Found.',
		title='Error')
	else:
		return student

@frappe.whitelist()
def register_student(source_name, target_doc=None):
	doclist = get_mapped_doc("Waiting List", source_name,
		{"Waiting List": {
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
				"guardian_first_name": "guardian_first_name",
				"guardian_relation": "guardian_relation",
				"guardian_mobile_no": "guardian_mobile_no",
				"guardian_id": "guardian_id",
				"guardian_id_expiry": "guardian_id_expiry",
				"guardian_last_name": "guardian_last_name",
				"guardian_nationality": "guardian_nationality",
				"guardian_email": "guardian_email",
				"guardian_passport_number": "guardian_passport_number",
				"guardian_pp_expiry": "guardian_pp_expiry",
				"emergency_contact_name_1": "emergency_contact_name_1",
				"emergency_contact_relation_1": "emergency_contact_relation_1",
				"emergency_contact_no_1": "emergency_contact_no_1",
				"emergency_contact_name_2": "emergency_contact_name_2",
				"emergency_contact_relation_2": "emergency_contact_relation_2",
				"emergency_contact_no_2": "emergency_contact_no_2",
				"father_name": "father_name",
				"father_prof": "father_profession",
				"father_mob": "father_mob_number",
				"father_nationality": "father_nationality",
				"mother_name": "mother_name",
				"mother_prof": "mother_profession",
				"mother_mob": "mother_mob_number",
				"mother_nationality": "father_nationality",
				"blood_grp": "blood_grp",
				#"allergies": "allergies",
				"allergy_type": "allergy_type",
				"allergy_period_treatment": "allergy_period_treatment",
				#"seizures": "seizures",
				"seizure_type": "seizure_type",
				"seizure_period_type": "seizure_period_type",
				#"medication":
				#"medication_type":
				#"medication_quantity":
				#"medication_period":
				#"other_diseases_or_medical_conditions":
				"other_diseases_type": "other_type",
				"other_diseases_period": "other_period_treatment",
				"persons_pickup1": "persons_pickup1",
				"persons_pickup1_mobile": "persons_pickup1_mobile",
				"persons_pickup2": "persons_pickup2",
				"persons_pickup2_mobile": "persons_pickup2_mobile",
				"persons_pickup3": "persons_pickup3",
				"persons_pickup3_mobile": "persons_pickup3_mobile",
				#"report_att":
				#"child_pic_att":
				#"child_birth_att":
				#"child_pp_att":
				#"child_eid_att":
				#"guard_pp_att":
				#"guard_eid_att":
				}
		}})
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



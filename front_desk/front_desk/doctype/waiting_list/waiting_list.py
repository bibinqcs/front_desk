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
			frappe.throw('Date of Birth cannot be greater than today.')
		
		if self.date_of_birth and getdate(today()).year - getdate(self.date_of_birth).year < 2:
			frappe.throw('Child has to be atleast 2 years old to apply.')

		if self.expiry_date and getdate(self.expiry_date) <= getdate(today()):
			frappe.throw('Passport is expired.')

		if self.eid_expiry_date and self.valid_eid == 'Yes' and getdate(self.eid_expiry_date) <= getdate(today()):
			frappe.throw('Emirates ID is expired.')

		if self.guardian_id_expiry and getdate(self.guardian_id_expiry) <= getdate(today()):
			frappe.throw('Guardian Emirates ID is expired.')
		
		if self.guardian_pp_expiry and getdate(self.guardian_pp_expiry) <= getdate(today()):
			frappe.throw('Guardian Passport is expired.')


@frappe.whitelist()
def verify_student_details(student_name, date_of_birth):
	student = frappe.get_doc('Student', student_name)
	if not getdate(student.date_of_birth) == getdate(date_of_birth):
		frappe.throw('No Matching Records Found')
	else:
		return student

@frappe.whitelist()
def register_student(source_name, target_doc=None):
	doclist = get_mapped_doc("Waiting List", source_name,
		{"Waiting List": {
			"doctype": "Student",
			"field_map": {
				"name1": "first_name",
				"language": "language",
				"father_name":"father_name",
				"father_mob": "father_mob_number",
				"father_email":"fathers_email",
				"mother_name":"mother_name",
				"mother_mob":"mother_mob_number",
				"mother_email":"mother_email"
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



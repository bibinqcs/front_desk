# -*- coding: utf-8 -*-
# Copyright (c) 2017, Quark Cyber Systems and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import add_days, today
from frappe.utils import flt
from erpnext.healthcare.doctype.healthcare_settings.healthcare_settings import get_receivable_account, get_income_account
from erpnext.accounts.doctype.sales_invoice.test_sales_invoice import create_sales_invoice

class WaitingList(Document):
	def validate(self):
		self.create_observation_invoice()

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

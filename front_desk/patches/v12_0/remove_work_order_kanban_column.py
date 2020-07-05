from __future__ import unicode_literals
import frappe

def execute():
	if frappe.db.exists("Custom Field", "Work Order-kanban_column"):
        frappe.delete_doc("Custom Field", "Work Order-kanban_column")
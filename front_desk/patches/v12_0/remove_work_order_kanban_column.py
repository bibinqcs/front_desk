import frappe

def execute():
    if frappe.db.exists("Custom Field", "Work Order-kanban_column"):
        frappe.delete_doc("Custom Field", "Work Order-kanban_column")
    frappe.reload_doc('manufacturing', 'doctype', 'work_order')
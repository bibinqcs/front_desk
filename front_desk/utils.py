# -*- coding: utf-8 -*-
# Copyright (c) 2015, vivek and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.utils.file_manager import save_url
import requests
from frappe.utils import get_url, getdate
from erpnext.hr.doctype.leave_application.leave_application import get_number_of_leave_days


@frappe.whitelist()
def custom_submit(doctype, name):
    doc = frappe.get_doc(doctype, name)
    doc.submit()


@frappe.whitelist()
def employee_salary(employee):
    ssa = frappe.db.get_value("Salary Structure Assignment", filters={
                "docstatus": 1,
                "employee": employee
            })
    ssadoc = frappe.get_doc("Salary Structure Assignment", ssa)
    base_salary = ssadoc.base
    return base_salary


@frappe.whitelist()
def get_approved_leaves_for_period(employee, leave_type):
    from_date, to_date = frappe.db.get_value('Leave Period', {'is_active': 1}, ['from_date', 'to_date'])

    query = """
        select employee, leave_type, from_date, to_date, total_leave_days
        from `tabLeave Application`
        where employee=%(employee)s
            and status="Approved"
            and (from_date between %(from_date)s and %(to_date)s
                or to_date between %(from_date)s and %(to_date)s
                or (from_date < %(from_date)s and to_date > %(to_date)s))
    """
    if leave_type:
        query += "and leave_type=%(leave_type)s"

    leave_applications = frappe.db.sql(query, {
        "from_date": from_date,
        "to_date": to_date,
        "employee": employee,
        "leave_type": leave_type
    }, as_dict=1)

    leave_days = 0
    for leave_app in leave_applications:
        if leave_app.from_date >= getdate(from_date) and leave_app.to_date <= getdate(to_date):
            leave_days += leave_app.total_leave_days
        else:
            if leave_app.from_date < getdate(from_date):
                leave_app.from_date = from_date
            if leave_app.to_date > getdate(to_date):
                leave_app.to_date = to_date
            leave_days += get_number_of_leave_days(employee, leave_type, leave_app.from_date, leave_app.to_date)

    return leave_days


@frappe.whitelist()
def attach_fields_docs(document, method=None):
    """This function attaches files from fields to general attachments"""
    document = json.loads(document)

    current_attachments = []
    files = frappe.db.sql("""SELECT
                    file_url
                FROM
                    `tabFile`
                WHERE
                    attached_to_doctype = %(doctype)s
                AND
                    attached_to_name = %(docname)s""", {
                        'doctype': document["doctype"],
                        'docname': document["name"]},
                        as_dict=True)

    for file_url in files:
        current_attachments.append(file_url.file_url)
        count = 0
        for item_doc in document["items"]:
            # frappe.msgprint(item_doc)
            # Check to see if the quantity is = 1
            item = frappe.get_doc("Item", item_doc["item_code"])
            attachments = []
            # Get the path for the attachments
            if item.drawing_attachment:
                attachments.append(item.drawing_attachment)
            if item.stp_attachment:
                attachments.append(item.stp_attachment)
            if item.dxf_attachment:
                attachments.append(item.dxf_attachment)
            if item.x_t_attachment:
                attachments.append(item.x_t_attachment)

            for attach in attachments:
                # Check to see if this file is attached to the one we are looking for
                if not attach in current_attachments:
                    count = count + 1
                    save_url(attach, document["doctype"], document["name"], "Home/Attachments")
    frappe.msgprint("Attached {0} files".format(count))


def manage_staff_student_permission(student_group, method):
    sg = frappe.get_doc("Student Group", student_group.name)

    # delete previous user Permissions
    for st in sg.student_class:
        frappe.db.sql(""" delete
                from `tabUser Permission`
                where for_value = %(voucher_no)s""", {
                    'voucher_no': st.student
                }
            )
    # assign new user permission
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

@frappe.whitelist()
def delete_doc():
    frappe.db.delete('Email Queue', {
        'status': 'Error'
    })
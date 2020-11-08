# -*- coding: utf-8 -*-
# Copyright (c) 2015, vivek and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe.utils.file_manager import save_url
import requests
from frappe.utils import get_url


@frappe.whitelist()
def custom_submit(doctype, name):
    doc = frappe.get_doc(doctype, name)
    doc.submit()


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


def is_valid_url(url):
    is_valid = False
    if url.startswith("/files") or url.startswith("/private/files"):
        url = get_url(url)
    try:
        r = requests.get(url)
        is_valid = True if r.status_code == 200 else False
    except Exception:
        pass
    return is_valid


def attach_file_to_doc(doctype, docname, file_url):
    # check if attachment is already available
    # check if the attachement link is relative or not
    if not file_url:
        return
    if not is_valid_url(file_url):
        return
    files = frappe.db.sql("""Select name from `tabFile` where attached_to_doctype='{doctype}' and
        attached_to_name='{docname}' and (file_url='{file_url}' or thumbnail_url='{file_url}')""".format(
            doctype=doctype,
            docname=docname,
            file_url=file_url
        ))
    if files:
        # file is already attached
        return
    _file = frappe.get_doc({
        "doctype": "File",
        "file_url": file_url,
        "attached_to_name": docname,
        "attached_to_doctype": doctype,
        "attached_to_field": 0,
        "folder": "Home/Attachments"})
    _file.save()


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

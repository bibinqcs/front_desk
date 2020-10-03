# -*- coding: utf-8 -*-
# Copyright (c) 2015, vivek and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


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

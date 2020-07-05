# Copyright (c) 2020, QCS and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals

import frappe

def execute():
    if frappe.db.exists("Custom Field", "Work Order-kanban_column"):
        frappe.delete_doc("Custom Field", "Work Order-kanban_column")
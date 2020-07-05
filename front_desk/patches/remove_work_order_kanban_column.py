  
# Copyright (c) 2020, QCS and Contributors
# License: GNU General Public License v3. See license.txt

import frappe

def execute():
    if frappe.db.exists('Custom Field', 'Work Order-kanban_column'):
        frappe.db.sql('''DELETE
            FROM `tabCustom Field`
            WHERE
                name = 'Work Order-kanban_column' LIMIT 1''')
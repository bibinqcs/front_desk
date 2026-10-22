# Copyright (c) 2026, Quark Cyber Systems and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import flt

# group_by filter -> how rows are keyed
GROUP_EMPLOYEE = "Employee"
GROUP_DEPARTMENT = "Department"
GROUP_DETAIL = "Detail (one row per record)"


def execute(filters=None):
    filters = frappe._dict(filters or {})
    if not (filters.from_date and filters.to_date):
        frappe.throw(_("Please set both From Date and To Date"))
    if filters.from_date > filters.to_date:
        frappe.throw(_("From Date cannot be after To Date"))

    group_by = filters.get("group_by") or GROUP_EMPLOYEE
    rows = get_attendance(filters)

    if group_by == GROUP_DETAIL:
        return get_detail_columns(), get_detail_rows(rows)
    if group_by == GROUP_DEPARTMENT:
        return get_department_columns(), group_rows(rows, by="department")
    return get_employee_columns(), group_rows(rows, by="employee")


def hours(seconds):
    """Duration fields store seconds; convert to decimal hours.

    Full precision on purpose - rounding here and then summing makes the per-record
    error accumulate. Callers round once, at display time, so totals stay exact
    regardless of how the rows are grouped.
    """
    if not seconds:
        return 0.0
    return flt(seconds) / 3600.0


def get_conditions(filters):
    conditions = ["a.docstatus = 1", "a.attendance_date between %(from_date)s and %(to_date)s"]
    if filters.get("company"):
        conditions.append("a.company = %(company)s")
    if filters.get("employee"):
        conditions.append("a.employee = %(employee)s")
    if filters.get("department"):
        conditions.append("e.department = %(department)s")
    if filters.get("status"):
        conditions.append("a.status = %(status)s")
    return " and ".join(conditions)


def get_attendance(filters):
    return frappe.db.sql("""
        select
            a.name, a.employee, a.employee_name, e.department, a.attendance_date,
            a.status, a.shift, a.time_in, a.time_out, a.start_time, a.end_time,
            a.total_working_hours_duration as total_working_hours,
            a.late_in_duration as late_in,
            a.early_out_duration as early_out,
            a.late_entry, a.early_exit
        from `tabAttendance` a
        left join `tabEmployee` e on e.name = a.employee
        where {conditions}
        order by e.department, a.employee_name, a.attendance_date
    """.format(conditions=get_conditions(filters)), filters, as_dict=True)


# ---------------------------------------------------------------- grouped views

MEASURE_COLUMNS = [
    {"label": _("Present"), "fieldname": "present_days", "fieldtype": "Int", "width": 80},
    {"label": _("Absent"), "fieldname": "absent_days", "fieldtype": "Int", "width": 80},
    {"label": _("On Leave"), "fieldname": "leave_days", "fieldtype": "Int", "width": 90},
    {"label": _("Half Day"), "fieldname": "half_days", "fieldtype": "Int", "width": 90},
    {"label": _("Total Working Hours"), "fieldname": "total_working_hours",
     "fieldtype": "Float", "precision": 2, "width": 160},
    {"label": _("Late Entries"), "fieldname": "late_entry_count", "fieldtype": "Int", "width": 110},
    {"label": _("Total Late In (Hrs)"), "fieldname": "late_in_hours",
     "fieldtype": "Float", "precision": 2, "width": 150},
    {"label": _("Early Exits"), "fieldname": "early_exit_count", "fieldtype": "Int", "width": 110},
    {"label": _("Total Early Out (Hrs)"), "fieldname": "early_out_hours",
     "fieldtype": "Float", "precision": 2, "width": 160},
]


def get_employee_columns():
    return [
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link",
         "options": "Employee", "width": 120},
        {"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 180},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link",
         "options": "Department", "width": 200},
        {"label": _("Shift"), "fieldname": "shift", "fieldtype": "Data", "width": 210},
    ] + MEASURE_COLUMNS


def get_department_columns():
    return [
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link",
         "options": "Department", "width": 250},
        {"label": _("Employees"), "fieldname": "employee_count", "fieldtype": "Int", "width": 100},
        {"label": _("Shifts Used"), "fieldname": "shift_count", "fieldtype": "Int", "width": 110},
    ] + MEASURE_COLUMNS


def group_rows(rows, by):
    summary = {}
    for r in rows:
        key = r.get(by)
        s = summary.get(key)
        if not s:
            s = summary[key] = {
                "present_days": 0, "absent_days": 0, "leave_days": 0, "half_days": 0,
                "total_working_hours": 0.0, "late_entry_count": 0, "late_in_hours": 0.0,
                "early_exit_count": 0, "early_out_hours": 0.0, "_employees": set(),
                "_shifts": {},
            }
            if by == "employee":
                s["employee"] = r.employee
                s["employee_name"] = r.employee_name
                s["department"] = r.department
            else:
                s["department"] = r.department

        s["_employees"].add(r.employee)
        if r.shift:
            s["_shifts"][r.shift] = s["_shifts"].get(r.shift, 0) + 1

        if r.status == "Present":
            s["present_days"] += 1
        elif r.status == "Absent":
            s["absent_days"] += 1
        elif r.status == "On Leave":
            s["leave_days"] += 1
        elif r.status == "Half Day":
            s["half_days"] += 1

        # Reads the Duration columns, which are NULL wherever the underlying value was
        # never trustworthy - so no junk-filtering is needed here any more. Still scoped
        # to Present because hours/tardiness are only meaningful for a worked day.
        if r.status == "Present":
            s["total_working_hours"] += hours(r.total_working_hours)
            s["late_in_hours"] += hours(r.late_in)
            s["early_out_hours"] += hours(r.early_out)
            if r.late_entry or r.late_in:
                s["late_entry_count"] += 1
            if r.early_exit or r.early_out:
                s["early_exit_count"] += 1

    data = []
    for s in summary.values():
        s["employee_count"] = len(s.pop("_employees"))
        shifts = s.pop("_shifts")
        s["shift_count"] = len(shifts)
        s["shift"] = describe_shifts(shifts)
        for k in ("total_working_hours", "late_in_hours", "early_out_hours"):
            s[k] = flt(s[k], 2)
        data.append(s)

    if by == "employee":
        data.sort(key=lambda d: (d.get("department") or "", d.get("employee_name") or ""))
    else:
        data.sort(key=lambda d: d.get("department") or "")
    return data


def describe_shifts(shifts):
    """Employees commonly span several shifts in a range (Ramadan variants), so show
    the one worked most and flag how many others there were."""
    if not shifts:
        return ""
    ranked = sorted(shifts.items(), key=lambda kv: (-kv[1], kv[0]))
    primary = ranked[0][0]
    if len(ranked) == 1:
        return primary
    return "%s (+%d more)" % (primary, len(ranked) - 1)


# ----------------------------------------------------------------- detail view

def get_detail_columns():
    return [
        {"label": _("Employee"), "fieldname": "employee", "fieldtype": "Link",
         "options": "Employee", "width": 120},
        {"label": _("Employee Name"), "fieldname": "employee_name", "fieldtype": "Data", "width": 170},
        {"label": _("Department"), "fieldname": "department", "fieldtype": "Link",
         "options": "Department", "width": 180},
        {"label": _("Date"), "fieldname": "attendance_date", "fieldtype": "Date", "width": 100},
        {"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 90},
        {"label": _("Shift"), "fieldname": "shift", "fieldtype": "Data", "width": 170},
        {"label": _("Time In"), "fieldname": "time_in", "fieldtype": "Data", "width": 90},
        {"label": _("Time Out"), "fieldname": "time_out", "fieldtype": "Data", "width": 90},
        {"label": _("Working Hours"), "fieldname": "total_working_hours",
         "fieldtype": "Float", "precision": 2, "width": 130},
        {"label": _("Late In (Hrs)"), "fieldname": "late_in_hours",
         "fieldtype": "Float", "precision": 2, "width": 120},
        {"label": _("Early Out (Hrs)"), "fieldname": "early_out_hours",
         "fieldtype": "Float", "precision": 2, "width": 130},
        {"label": _("Attendance"), "fieldname": "name", "fieldtype": "Link",
         "options": "Attendance", "width": 130},
    ]


def as_clock(value):
    if not value:
        return ""
    total = int(value.total_seconds()) if hasattr(value, "total_seconds") else int(value)
    return "%02d:%02d:%02d" % (total // 3600, (total % 3600) // 60, total % 60)


def get_detail_rows(rows):
    data = []
    for r in rows:
        present = r.status == "Present"
        data.append({
            "employee": r.employee, "employee_name": r.employee_name,
            "department": r.department, "attendance_date": r.attendance_date,
            "status": r.status, "shift": r.shift,
            "time_in": as_clock(r.time_in) if present else "",
            "time_out": as_clock(r.time_out) if present else "",
            "total_working_hours": flt(hours(r.total_working_hours), 2) if present else 0.0,
            "late_in_hours": flt(hours(r.late_in), 2) if present else 0.0,
            "early_out_hours": flt(hours(r.early_out), 2) if present else 0.0,
            "name": r.name,
        })
    return data

# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "front_desk"
app_title = "Front Desk"
app_publisher = "Quark Cyber Systems"
app_description = "App for reception"
app_icon = "octicon octicon-organization"
app_color = "#b5cbf2"
app_email = "vivek@quarkcs.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/front_desk/css/front_desk.css"
# app_include_js = "/assets/front_desk/js/front_desk.js"

# include js, css files in header of web template
# web_include_css = "/assets/front_desk/css/front_desk.css"
# web_include_js = "/assets/front_desk/js/front_desk.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "front_desk.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "front_desk.install.before_install"
# after_install = "front_desk.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "front_desk.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }
doc_events = {
	"Course Schedule": {
		"validate": "front_desk.front_desk.doctype.student_schedule.student_schedule.create_class_semester_schedule"
	},
#	"Employee":{
#		"autoname": "front_desk.common.employee_name"
#	},
	"Student Group":{
		"validate": "front_desk.common_12.manage_staff_student_permission"
	},
#	"Attendance":{
#		"validate": "front_desk.common_12.redundant_attendance_custom_fields"
#		"validate": "front_desk.common_12.calculate_tardiness"
#	},
#	"Salary Slip":{
#		"validate": "front_desk.common.lwp_d"
#	},
#	"Salary Slip":{
#		"validate": "front_desk.common_12.salary_slip_deduction"
#	},
#	"Teacher Schedule":{
#        	"validate": "front_desk.common.sync_teacher_student"
#	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
# 	"all": [
# 		"front_desk.tasks.all"
# 	],
#	"daily": [
#		"front_desk.common.sync_access_log",
#		"front_desk.common.mark_attendance",
#	]
 	"hourly": [
# 		"front_desk.tasks.hourly"
		"front_desk.common_12.remove_custom_field_kanban_column",
 	],
# 	"weekly": [
# 		"front_desk.tasks.weekly"
# 	]
# 	"monthly": [
# 		"front_desk.tasks.monthly"
# 	]
}

# Testing
# -------

# before_tests = "front_desk.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "front_desk.event.get_events"
# }

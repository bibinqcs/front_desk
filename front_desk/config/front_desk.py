from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Reception"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Call Log",
					"description": _("Log Calls Recieved."),
				},
				{
					"type": "doctype",
					"name": "Appointments",
					"description": _("Schedule Appointments."),
				},
			]
		},
		{
			"label": _("Reservations"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Meeting Room Reservation",
					"description": _("Reserve Meeting Room."),
				},
				{
					"type": "doctype",
					"name": "Transport Request",
					"description": _("Make Transportation Request."),
				},
			]
		},
		{
			"label": _("School"),
			"icon": "fa fa-star",
			"items": [
				{
					"type": "doctype",
					"name": "Waiting List",
					"description": _("Waiting List."),
				},

			]
		},
	]

frappe.views.calendar["Appointments"] = {
	field_map: {
		// from_datetime and to_datetime don't exist as docfields but are used in onload
		"start": "from_datetime",
		"end": "to_datetime",
		"id": "contact_name",
		"title": "subject",
		"allDay": "allDay",
		"status": "type",
		"color": "color"
	},
	style_map: {
		"Doctor": "success",
		"Teacher": "info"
	},
	gantt: false,
	textColor: 'black',
	filters: [
		{
			"fieldtype": "Data",
			"fieldname": "contact_name",
			"label": __("Appointments")
		}

	],
	get_events_method: "front_desk.front_desk.doctype.appointments.appointments.get_appointments"
}

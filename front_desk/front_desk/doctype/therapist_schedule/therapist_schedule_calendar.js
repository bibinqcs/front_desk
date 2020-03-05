frappe.views.calendar["Therapist Schedule"] = {
	field_map: {
		// from_datetime and to_datetime don't exist as docfields but are used in onload
		"start": "from_datetime",
		"end": "to_datetime",
		"id": "name",
		"title": "title",
		"allDay": "allDay"
	},
	gantt: false,
	filters: [
		{
			"fieldtype": "Link",
			"fieldname": "therapist",
			"options": "Instructor",
			"label": __("Instructor")
		}
	],
	get_events_method: "front_desk.front_desk.doctype.therapist_schedule.therapist_schedule.get_therapist_schedule"
}

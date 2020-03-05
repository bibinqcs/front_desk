frappe.views.calendar["Student Schedule"] = {
	field_map: {
		// from_datetime and to_datetime don't exist as docfields but are used in onload
		"start": "from_time",
		"end": "to_time",
		"id": "title",
		"title": "notes",
		"allDay": "allDay",
		"status": "type",
		"tooltip":"teacher_name",
		"color" : "color",
		"defaultView": 'listWeek',

	},
	gantt: false,
	textColor: 'black',
	filters: [
		{
			"fieldtype": "Link",
			"fieldname": "student",
			"options": "Student",
			"label": __("Student")
		}


	],

	get_events_method: "front_desk.front_desk.doctype.teacher_schedule.teacher_schedule.get_teacher_schedule"
}

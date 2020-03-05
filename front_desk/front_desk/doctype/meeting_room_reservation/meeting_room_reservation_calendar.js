frappe.views.calendar["Meeting Room Reservation"] = {
	field_map: {
		// from_datetime and to_datetime don't exist as docfields but are used in onload
		"start": "from_datetime",
		"end": "to_datetime",
		"id": "contact_name",
		"title": "name",
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
			"label": __("Meeting Room Reservation")
		}

	],
	get_events_method: "front_desk.front_desk.doctype.meeting_room_reservation.meeting_room_reservation.get_meetings"
}

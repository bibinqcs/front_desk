frappe.views.calendar["Teacher Schedule"] = {
	field_map: {
		// from_datetime and to_datetime don't exist as docfields but are used in onload
		"start": "from_time",
		"end": "to_time",
		"id": "title",
		"title": "student_name",
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
			"fieldname": "teacher",
			"options": "Employee",
			"label": __("Teacher")
		},
		{
			"fieldtype": "Check",
			"fieldname": "student_check",
			"label": __("Student View")
		},

	],
	customButtons: {
    myCustomButton: {
      text: 'Student View',
      click: function() {
        alert('clicked the custom button!');
      }
    }
  },
	get_events_method: "front_desk.front_desk.doctype.teacher_schedule.teacher_schedule.get_teacher_schedule"
}

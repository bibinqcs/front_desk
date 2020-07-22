// Copyright (c) 2017, Quark Cyber Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on ('Waiting List', {
	refresh: function(frm) {
		frm.add_custom_button(__("Register Student"), function() {
			frappe.model.open_mapped_doc({
				method: "front_desk.front_desk.doctype.waiting_list.waiting_list.register_student",
				frm: cur_frm
			});
		   }, __("Make"));
		frm.add_custom_button(__("Appointment"), function() {
			frappe.model.open_mapped_doc({
				method: "front_desk.front_desk.doctype.waiting_list.waiting_list.make_appointment",
				frm: cur_frm
			});
		   }, __("Make"));
	},

	onload: function(frm) {
		frm.set_query('item_observation', function() {
			return {
				'filters': {
					'item_group': 'Observations'
				}
			};
		});
	},

	get_student_details: function(frm) {
		if (frm.doc.student && frm.doc.chk_date_of_birth) {
			frappe.call({
				method: "front_desk.front_desk.doctype.waiting_list.waiting_list.verify_student_details",
				args: {
					student_name: frm.doc.student,
					date_of_birth: frm.doc.chk_date_of_birth
				},
				success: 
				frappe.model.with_doc("Student", frm.doc.student, function() {
					var sd = frappe.model.get_doc("Student", frm.doc.student);
					frm.set_value("student_first_name", sd.first_name);
					frm.set_value("student_middle_name", sd.middle_name);
					frm.set_value("student_last_name", sd.last_name);
					frm.set_value("student_full_name", sd.title);
					frm.set_value("date_of_birth", sd.date_of_birth);
					frm.set_value("gender", sd.gender);
					frm.set_value("religion", sd.religion);
					frm.set_value("nationality", sd.student_nationality);
					frm.set_value("place_of_birth", sd.place_of_birth);
					frm.set_value("student_first_name", sd.first_name);
					frm.set_value("student_first_name", sd.first_name);
					frm.set_value("student_first_name", sd.first_name);
					frm.set_value("student_first_name", sd.first_name);
					frm.set_value("student_first_name", sd.first_name);
					frm.set_value("student_first_name", sd.first_name);
					frm.set_value("student_first_name", sd.first_name);
					frm.set_value("student_first_name", sd.first_name);
					frm.set_value("student_first_name", sd.first_name);
					frm.set_value("student_first_name", sd.first_name);
					frm.set_value("student_first_name", sd.first_name);
					frm.set_value("student_first_name", sd.first_name);
					frm.set_value("student_first_name", sd.first_name);
				}),
				error: 
				frappe.throw("Record Not Found"),
			});
		} else {
			frappe.msgprint(__("Please enter Student ID and Date of Birth"));
		}
	}

});
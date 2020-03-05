// Copyright (c) 2017, Quark Cyber Systems and contributors
// For license information, please see license.txt

frappe.ui.form.on('Waiting List', {
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


	}
});


frappe.ui.form.on("Waiting List", "date_of_birth", function(frm, doctype, name) {
  var v1 = 0;
  v1 = frappe.datetime.get_diff(frappe.datetime.get_today(), frm.doc.date_of_birth);
  frm.doc.age = Math.floor((v1).toFixed(2) / 365.25);
  refresh_field("age");
});
